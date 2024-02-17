from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)
try:
    requirements = [str(ir.req) for ir in install_reqs]
except:
    requirements = [str(ir.requirement) for ir in install_reqs]

setup(name='ryzenaiyolov8m',
      version='0.0.6',
      description='yolov8m for ryzenai test',
      author='fangyuan',
      author_email='fangyuan@amd.com',
      install_requires=requirements,
      packages=find_packages(),  # 系统自动从当前目录开始找包
      include_package_data=True,
      license="apache 3.0"
     )
