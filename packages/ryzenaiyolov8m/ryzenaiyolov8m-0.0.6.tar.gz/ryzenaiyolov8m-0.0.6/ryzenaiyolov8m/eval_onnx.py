import json
from pathlib import Path
import torch
import argparse
import numpy as np
from tqdm import tqdm
import onnxruntime
from utils import check_det_dataset, yaml_load, IterableSimpleNamespace, build_dataloader, post_process, xyxy2xywh, LOGGER, \
                DetMetrics, increment_path, get_cfg, smart_inference_mode, box_iou, TQDM_BAR_FORMAT, scale_boxes, non_max_suppression, xywh2xyxy

# Default configuration
DEFAULT_CFG_DICT = yaml_load("./default.yaml")
for k, v in DEFAULT_CFG_DICT.items():
    if isinstance(v, str) and v.lower() == 'none':
        DEFAULT_CFG_DICT[k] = None
DEFAULT_CFG_KEYS = DEFAULT_CFG_DICT.keys()
DEFAULT_CFG = IterableSimpleNamespace(**DEFAULT_CFG_DICT)
import sys
import pathlib
CURRENT_DIR = pathlib.Path(__file__).parent
sys.path.append(str(CURRENT_DIR))


class DetectionValidator:

    def __init__(self, dataloader=None, save_dir=None, pbar=None, logger=None, args=None):
        self.dataloader = dataloader
        self.pbar = pbar
        self.logger = LOGGER
        self.args = args
        self.model = None
        self.data = None
        self.device = None
        self.batch_i = None
        self.speed = None
        self.jdict = None
        self.args.task = 'detect'
        project = Path("./runs") / self.args.task
        self.save_dir = save_dir or increment_path(Path(project),
                                                   exist_ok=True)
        (self.save_dir / 'labels').mkdir(parents=True, exist_ok=True)
        self.args.conf = 0.001  # default conf=0.001
        self.is_coco = False
        self.class_map = None
        self.metrics = DetMetrics(save_dir=self.save_dir)
        self.iouv = torch.linspace(0.5, 0.95, 10)  # iou vector for mAP@0.5:0.95
        self.niou = self.iouv.numel()

    @smart_inference_mode()
    def __call__(self, trainer=None, model=None):
        """
        Supports validation of a pre-trained model if passed or a model being trained
        if trainer is passed (trainer gets priority).
        """
        self.device = torch.device('cpu')
        onnx_weight = self.args.onnx_weight
        if isinstance(onnx_weight, list):
            onnx_weight = onnx_weight[0] 
        if self.args.ipu:
            providers = ["VitisAIExecutionProvider"]
            provider_options = [{"config_file": self.args.provider_config}]
            onnx_model = onnxruntime.InferenceSession(onnx_weight, providers=providers, provider_options=provider_options)
        else:
            onnx_model = onnxruntime.InferenceSession(onnx_weight)
        self.data = check_det_dataset(self.args.data)
        self.args.rect = False
        self.dataloader = self.dataloader or self.get_dataloader(self.data.get("val") or self.data.get("test"), self.args.batch)
        total = len(self.dataloader)
        n_batches = len(self.dataloader)
        desc = self.get_desc()
        bar = tqdm(self.dataloader, desc, total, bar_format=TQDM_BAR_FORMAT)
        self.init_metrics()
        self.jdict = []  # empty before each val

        for batch_i, batch in enumerate(bar):
            self.batch_i = batch_i
            # pre-process
            batch = self.preprocess(batch)

            # inference
            # outputs = onnx_model.run(None, {onnx_model.get_inputs()[0].name: batch["img"].cpu().numpy()})
            outputs = onnx_model.run(None, {onnx_model.get_inputs()[0].name: batch["img"].permute(0, 2, 3, 1).cpu().numpy()})
            # outputs = [torch.tensor(item).to(self.device) for item in outputs]
            outputs = [torch.tensor(item).permute(0, 3, 1, 2).to(self.device) for item in outputs]
            preds = post_process(outputs)

            # pre-process predictions
            preds = self.postprocess(preds)
            self.update_metrics(preds, batch)
        stats = self.get_stats()
        self.print_results()
        if self.args.save_json and self.jdict:
            with open(str(self.save_dir / "predictions.json"), 'w') as f:
                self.logger.info(f"Saving {f.name}...")
                json.dump(self.jdict, f)  # flatten and save
            stats = self.eval_json(stats)  # update stats
        return stats

    def get_dataloader(self, dataset_path, batch_size):
        # calculate stride - check if model is initialized
        return build_dataloader(self.args, batch_size, img_path=dataset_path, stride=32, names=self.data['names'], mode="val")[0]

    def get_desc(self):
        return ('%22s' + '%11s' * 6) % ('Class', 'Images', 'Instances', 'Box(P', "R", "mAP50", "mAP50-95)")

    def init_metrics(self):
        self.is_coco = True
        self.class_map = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 31, 32, 33, 34,
                          35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
                          64, 65, 67, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90]
        self.args.save_json = True
        self.nc = 80
        classnames = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush'] 
        self.names = {k: classnames[k] for k in range(80)}
        self.metrics.names = self.names
        self.metrics.plot = True
        self.seen = 0
        self.jdict = []
        self.stats = []

    def preprocess(self, batch):
        batch["img"] = batch["img"].to(self.device, non_blocking=True)
        batch["img"] = batch["img"].float() / 255
        for k in ["batch_idx", "cls", "bboxes"]:
            batch[k] = batch[k].to(self.device)

        nb = len(batch["img"])
        self.lb = [torch.cat([batch["cls"], batch["bboxes"]], dim=-1)[batch["batch_idx"] == i]
                   for i in range(nb)] if self.args.save_hybrid else []  # for autolabelling

        return batch

    def postprocess(self, preds):
        preds = non_max_suppression(preds,
                                    self.args.conf,
                                    self.args.iou,
                                    labels=self.lb,
                                    multi_label=True,
                                    agnostic=self.args.single_cls,
                                    max_det=self.args.max_det)
        return preds

    def update_metrics(self, preds, batch):
        # Metrics
        for si, pred in enumerate(preds):
            idx = batch["batch_idx"] == si
            cls = batch["cls"][idx]
            bbox = batch["bboxes"][idx]
            nl, npr = cls.shape[0], pred.shape[0]  # number of labels, predictions
            shape = batch["ori_shape"][si]
            correct_bboxes = torch.zeros(npr, self.niou, dtype=torch.bool, device=self.device)  # init
            self.seen += 1

            if npr == 0:
                if nl:
                    self.stats.append((correct_bboxes, *torch.zeros((2, 0), device=self.device), cls.squeeze(-1)))
                continue

            # Predictions
            if self.args.single_cls:
                pred[:, 5] = 0
            predn = pred.clone()
            scale_boxes(batch["img"][si].shape[1:], predn[:, :4], shape,
                        ratio_pad=batch["ratio_pad"][si])  # native-space pred

            # Evaluate
            if nl:
                height, width = batch["img"].shape[2:]
                tbox = xywh2xyxy(bbox) * torch.tensor(
                    (width, height, width, height), device=self.device)  # target boxes
                scale_boxes(batch["img"][si].shape[1:], tbox, shape,
                                ratio_pad=batch["ratio_pad"][si])  # native-space labels
                labelsn = torch.cat((cls, tbox), 1)  # native-space labels
                correct_bboxes = self._process_batch(predn, labelsn)
            self.stats.append((correct_bboxes, pred[:, 4], pred[:, 5], cls.squeeze(-1)))  # (conf, pcls, tcls)

            # Save
            if self.args.save_json:
                self.pred_to_json(predn, batch["im_file"][si])

    def _process_batch(self, detections, labels):
        """
        Return correct prediction matrix
        Arguments:
            detections (array[N, 6]), x1, y1, x2, y2, conf, class
            labels (array[M, 5]), class, x1, y1, x2, y2
        Returns:
            correct (array[N, 10]), for 10 IoU levels
        """
        iou = box_iou(labels[:, 1:], detections[:, :4])
        correct = np.zeros((detections.shape[0], self.iouv.shape[0])).astype(bool)
        correct_class = labels[:, 0:1] == detections[:, 5]
        for i in range(len(self.iouv)):
            x = torch.where((iou >= self.iouv[i]) & correct_class)  # IoU > threshold and classes match
            if x[0].shape[0]:
                matches = torch.cat((torch.stack(x, 1), iou[x[0], x[1]][:, None]),
                                    1).cpu().numpy()  # [label, detect, iou]
                if x[0].shape[0] > 1:
                    matches = matches[matches[:, 2].argsort()[::-1]]
                    matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                    # matches = matches[matches[:, 2].argsort()[::-1]]
                    matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
                correct[matches[:, 1].astype(int), i] = True
        return torch.tensor(correct, dtype=torch.bool, device=detections.device)

    def pred_to_json(self, predn, filename):
        stem = Path(filename).stem
        image_id = int(stem) if stem.isnumeric() else stem
        box = xyxy2xywh(predn[:, :4])  # xywh
        box[:, :2] -= box[:, 2:] / 2  # xy center to top-left corner
        for p, b in zip(predn.tolist(), box.tolist()):
            self.jdict.append({
                'image_id': image_id,
                'category_id': self.class_map[int(p[5])],
                'bbox': [round(x, 3) for x in b],
                'score': round(p[4], 5)})

    def get_stats(self):
        stats = [torch.cat(x, 0).cpu().numpy() for x in zip(*self.stats)]  # to numpy
        if len(stats) and stats[0].any():
            self.metrics.process(*stats)
        self.nt_per_class = np.bincount(stats[-1].astype(int), minlength=self.nc)  # number of targets per class
        return self.metrics.results_dict

    def print_results(self):
        pf = '%22s' + '%11i' * 2 + '%11.3g' * len(self.metrics.keys)  # print format
        self.logger.info(pf % ("all", self.seen, self.nt_per_class.sum(), *self.metrics.mean_results()))
        if self.nt_per_class.sum() == 0:
            self.logger.warning(
                f'WARNING ⚠️ no labels found in {self.args.task} set, can not compute metrics without labels')

        # Print results per class
        if self.args.verbose and self.nc > 1 and len(self.stats):
            for i, c in enumerate(self.metrics.ap_class_index):
                self.logger.info(pf % (self.names[c], self.seen, self.nt_per_class[c], *self.metrics.class_result(i)))


    def eval_json(self, stats):
        if self.args.save_json and self.is_coco and len(self.jdict):
            anno_json = Path(self.data['path']) / 'annotations/instances_val2017.json'  # annotations
            pred_json = self.save_dir / "predictions.json"  # predictions
            self.logger.info(f'\nEvaluating pycocotools mAP using {pred_json} and {anno_json}...')
            try:  # https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocoEvalDemo.ipynb
                from pycocotools.coco import COCO  # noqa
                from pycocotools.cocoeval import COCOeval  # noqa
                # for x in anno_json, pred_json:
                #     assert x.is_file(), f"{x} file not found"
                anno = COCO(str(anno_json))  # init annotations api
                pred = anno.loadRes(str(pred_json))  # init predictions api (must pass string, not Path)
                eval = COCOeval(anno, pred, 'bbox')
                if self.is_coco:
                    eval.params.imgIds = [int(Path(x).stem) for x in self.dataloader.dataset.im_files]  # images to eval
                eval.evaluate()
                eval.accumulate()
                eval.summarize()
                stats[self.metrics.keys[-1]], stats[self.metrics.keys[-2]] = eval.stats[:2]  # update mAP50-95 and mAP50
            except Exception as e:
                self.logger.warning(f'pycocotools unable to run: {e}')
        return stats


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ipu', action='store_true', help='flag for ryzen ai')
    parser.add_argument('--provider_config', default='', type=str, help='provider config for ryzen ai')
    parser.add_argument("-m", "--onnx_model", default="./yolov8m.onnx", type=str, help='onnx_weight')
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opt = parse_opt()
    args = get_cfg(DEFAULT_CFG)
    args.ipu = opt.ipu
    args.onnx_weight = opt.onnx_model
    args.provider_config = opt.provider_config
    validator = DetectionValidator(args=args)
    validator()
