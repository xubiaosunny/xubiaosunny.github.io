---
layout: post
title: "CUDA相关安装问题记录"
date: 2021-10-14 16:33:22 +0800
categories: 技术
tags: CUDA TensorRT
---


## CUDA

### docker运行

先安装nvidia-docker

https://nvidia.github.io/nvidia-docker/

```bash
apt-get install -y nvidia-docker2
```

启动cuda10.1和cudnn7环境

```bash
docker run --rm --runtime=nvidia -ti -v /data:/data nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04
```

问题

在docker中安装了nvidia-cuda-toolkit后`nvidia-smi`出现`failed to initialize nvml: driver/library version mismatch`错误
`pycuda`出现`pycuda._driver.LogicError: cuInit failed: system has unsupported display driver / cuda driver combination`

网上的方法基本都是重启和重装驱动，因为大家基本都是物理机直接安装的，不是docker环境，我这docker里装不上特定版本的nvidia-driver。
将nvidia驱动都卸载了，奇迹般的nvidia-smi和pycuda就正常了，估计docker环境的驱动直接打在kernel里面了，装了其他驱动就版本不匹配了。

```
apt-get remove --purge nvidia-\*
```


## TensorRT

```
TensorRT Internal Error: Assertion failed: Unsupported SM
```

https://forums.developer.nvidia.com/t/rtx-3070-tensorrt-internal-error-assertion-failed-unsupported-sm/169830

我用的3080TI显卡，TRT6，30系列需要TRT7，换用2080解决


## pycuda

```
error: expected declaration before ‘}’ token
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

报语法错误，指定c++11解决（`-std=c++11`）

```bash
tar xzvf pycuda-2019.1.2.tar.gz
cd pycuda-2019.1.2/
# 配置参数
 ./configure.py --cuda-root=/home/xx/software/cuda/install/ --boost-compiler=gcc49 --cxxflags=-std=c++11
# 编译
python setup.py build
# 安装
python setup.py install
```

还有一些`x86_64-linux-gnu-gcc`错误，找不到`cuda.h`或者`Python.h`的，指明位置或者安装所需的包即可，比如找不到`Python.h`安装python3-dev即可
