import torch
import torch.nn as nn
import onnxruntime
import numpy as np
import argparse
from utils import (
    LoadImages,
    non_max_suppression,
    plot_images,
    output_to_target,
)
import sys
import pathlib
CURRENT_DIR = pathlib.Path(__file__).parent
sys.path.append(str(CURRENT_DIR))
from optimum.amd.ryzenai import RyzenAIModelForObjectDetection
import os
path = os.path.abspath(__file__)
folder = os.path.dirname(path)

def preprocess(img):
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    return img


class DFL(nn.Module):
    # Integral module of Distribution Focal Loss (DFL) proposed in Generalized Focal Loss https://ieeexplore.ieee.org/document/9792391
    def __init__(self, c1=16):
        super().__init__()
        self.conv = nn.Conv2d(c1, 1, 1, bias=False).requires_grad_(False)
        x = torch.arange(c1, dtype=torch.float)
        self.conv.weight.data[:] = nn.Parameter(x.view(1, c1, 1, 1))
        self.c1 = c1

    def forward(self, x):
        b, c, a = x.shape  # batch, channels, anchors
        return self.conv(x.view(b, 4, self.c1, a).transpose(2, 1).softmax(1)).view(
            b, 4, a
        )


def dist2bbox(distance, anchor_points, xywh=True, dim=-1):
    """Transform distance(ltrb) to box(xywh or xyxy)."""
    lt, rb = torch.split(distance, 2, dim)
    x1y1 = anchor_points - lt
    x2y2 = anchor_points + rb
    if xywh:
        c_xy = (x1y1 + x2y2) / 2
        wh = x2y2 - x1y1
        return torch.cat((c_xy, wh), dim)  # xywh bbox
    return torch.cat((x1y1, x2y2), dim)  # xyxy bbox


def post_process(x):
    dfl = DFL(16)
    anchors = torch.tensor(
        np.load(
            os.path.join(folder, "anchors.npy"),
            allow_pickle=True,
        )
    )
    strides = torch.tensor(
        np.load(
            os.path.join(folder, "strides.npy"),
            allow_pickle=True,
        )
    )
    box, cls = torch.cat([xi.view(x[0].shape[0], 144, -1) for xi in x], 2).split(
        (16 * 4, 80), 1
    )
    dbox = dist2bbox(dfl(box), anchors.unsqueeze(0), xywh=True, dim=1) * strides
    y = torch.cat((dbox, cls.sigmoid()), 1)
    return y, x


def make_parser():
    parser = argparse.ArgumentParser("onnxruntime inference sample")
    parser.add_argument(
        "-m",
        "--onnx_model",
        type=str,
        default="./yolov8m.onnx",
        help="input your onnx model.",
    )
    parser.add_argument(
        "-i",
        "--image_path",
        type=str,
        default='./demo.jpg',
        help="path to your input image.",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        default='./demo_infer.jpg',
        help="path to your output directory.",
    )
    parser.add_argument(
        "--ipu", action='store_true', help='flag for ryzen ai'
    )
    parser.add_argument(
        "--provider_config", default='', type=str, help='provider config for ryzen ai'
    )
    return parser

classnames = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush'] 
names = {k: classnames[k] for k in range(80)}
imgsz = [640, 640]


if __name__ == '__main__':
    args = make_parser().parse_args()
    source = args.image_path 
    dataset = LoadImages(
        source, imgsz=imgsz, stride=32, auto=False, transforms=None, vid_stride=1
    )
    onnx_weight = args.onnx_model
    if args.ipu:
        onnx_model = RyzenAIModelForObjectDetection.from_pretrained(".\\", vaip_config=args.provider_config)
        # providers = ["VitisAIExecutionProvider"]
        # provider_options = [{"config_file": args.provider_config}]
        # onnx_model = onnxruntime.InferenceSession(onnx_weight, providers=providers, provider_options=provider_options)
    else:
        onnx_model = onnxruntime.InferenceSession(onnx_weight)
    for batch in dataset:
        path, im, im0s, vid_cap, s = batch
        im = preprocess(im)
        if len(im.shape) == 3:
            im = im[None]
        # outputs = onnx_model.run(None, {onnx_model.get_inputs()[0].name: im.cpu().numpy()})
        # outputs = [torch.tensor(item) for item in outputs]
        # outputs = onnx_model.run(None, {onnx_model.get_inputs()[0].name: im.permute(0, 2, 3, 1).cpu().numpy()})
        # outputs = [torch.tensor(item).permute(0, 3, 1, 2) for item in outputs]
        outputs = onnx_model(im.permute(0, 2, 3, 1))
        outputs = [outputs[0].permute(0, 3, 1, 2), outputs[1].permute(0, 3, 1, 2), outputs[2].permute(0, 3, 1, 2)]
        preds = post_process(outputs)
        preds = non_max_suppression(
            preds, 0.25, 0.7, agnostic=False, max_det=300, classes=None
        )
        plot_images(
            im,
            *output_to_target(preds, max_det=15),
            source,
            fname=args.output_path,
            names=names,
        )
