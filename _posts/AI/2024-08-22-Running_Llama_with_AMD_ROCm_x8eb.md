---
layout: post
title: "AMD ROCm运行Llama"
date: 2024-08-22 21:12:21 +0800
categories: 技术
tags: AI 大模型 Llama ROCm
---

> 我在安装的时候`ROCm`最新版本为6.2，本文操作都基于 **Ubuntu 24.04 LTS** 和 **ROCm 6.2**

当初装机为了(黑苹果)一直选择AMD显卡，现在搞AI一搞一个不吱声。早知道投入老黄的怀抱了，现在的N卡更加让我高攀不起😭

我的显卡是 `6800XT`, 一开始我是在MacOS系统上跑Llama，但是在MacOS上使用Apple的metal计算平台跑起来太慢，比使用CPU还慢。
所以就想使用AMD自己的计算平台 `ROCm` ，发现在 `ROCm` 也已经比较完善了，还支持了Windows系统。
但是我选择安装 `Ubuntu 24.04 LTS`，毕竟一开始就支持Linux的，估计优化会好些。

## **ROCm安装**

ROCm支持以下linux系统和内核，最好安装官方的来。本来想用debian的，还是别给自己找事做了😄

| Operating system | Kernel | Support |
|----|----|----|
| Ubuntu 24.04 | 6.8 \[GA\] | ✅ |
| Ubuntu 22.04.5 | 5.15 \[GA\], 6.8 \[HWE\] | ✅  |
| Ubuntu 22.04.4 | 5.15 \[GA\], 6.5 \[HWE\] | ✅ |
| RHEL 9.4 | 5.14.0 | ✅ |
| RHEL 9.3 | 5.14.0 | ✅ |
| RHEL 8.10 | 4.18.0 | ✅ |
| RHEL 8.9 | 4.18.0 | ✅ |
| SLES 15 SP6 | 6.4.0 | ✅ |
| SLES 15 SP5 | 5.14.21 | ✅ |
| Oracle Linux 8.9 | 5.15.0 | ✅  |

我这里选择`Ubuntu 24.04 TLS` ，根据官方文档安装命令如下

```bash
sudo apt update
sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
sudo usermod -a -G render,video $LOGNAME # Add the current user to the render and video groups
wget https://repo.radeon.com/amdgpu-install/6.2/ubuntu/noble/amdgpu-install_6.2.60200-1_all.deb
sudo apt install ./amdgpu-install_6.2.60200-1_all.deb
sudo apt update
sudo apt install amdgpu-dkms rocm
```

## **使用Llama.cpp**

`llama.cpp`在Github上下载的预编译文件只支持CPU运行。我是要用 `ROCm` 来加速，需要自己编译一下，也比较简单，详见文档：<https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md>

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

make GGML_HIPBLAS=1
```

---

> 2025.02.09 更新 

使用 `make` 构建现在会报如下错误

```bash
Makefile:2: *** The Makefile build is deprecated. Use the CMake build instead. For more details, see https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md.  Stop
```

按照当前文档使用 `cmake` 构建

```bash
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
    cmake -S . -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1030 -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --config Release -- -j 16
```

---

我这里使用的Llama3.1-8B模型（[Meta-Llama-3.1-8B-Instruct.Q8_0.gguf](https://huggingface.co/QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF)）

```bash
./llama-server --host 0.0.0.0  -c 4096 -ngl 999 -m models/Meta-Llama-3.1-8B-Instruct.Q8_0.gguf
```

## **使用Ollama**

Ollama安装直接支持ROCm，安装命令如下

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

输出可以看到`Compatible AMD GPU ROCm library detected at /opt/rocm`，说明可以使用`ROCm`

```
>>> Installing ollama to /usr/local
>>> Downloading Linux amd64 CLI
######################################################################## 100.0%  
>>> Making ollama accessible in the PATH in /usr/local/bin
>>> Creating ollama user...
>>> Adding ollama user to render group...
>>> Adding ollama user to video group...
>>> Adding current user to ollama group...
>>> Creating ollama systemd service...
>>> Enabling and starting ollama service...
Created symlink /etc/systemd/system/default.target.wants/ollama.service → /etc/systemd/system/ollama.service.
>>> Compatible AMD GPU ROCm library detected at /opt/rocm
>>> The Ollama API is now available at 127.0.0.1:11434.
>>> Install complete. Run "ollama" from the command line.
```

拉取 `llama3.1` 模型

```bash
ollama pull llama3.1
```

运行 `llama3.1` 

```bash
ollama run llama3.1
```

## **验证是否GPU加速**

ROCm使用 `rocm-smi` 命令来查看GPU的状态，类似于CUDA的 `nvidia-smi`

![](/assets/images/post/截屏2024-08-23 15.58.10.png)

看到GPU的占用还是挺高的，说明已经用到GPU加速了，同时也可以看看CPU占用，正常用了GPU计算的话CPU占用就相对较低。

## **额外的问题解决**

安装完 `ROCm`，在linux桌面操作，系统应用如设置、文件、监视器等都打不开，火狐浏览器还可以打开。查看syslog发现以下日志。

```
libEGL warning: DRI3: Screen seems not DRI3 capable
libEGL warning: DRI2: failed to authenticate
libEGL warning: DRI3: Screen seems not DRI3 capable
libEGL fatal: DRI driver not from this Mesa build ('24.2.0-devel' vs '24.0.9-0ubuntu0.1')
```

查看mesa版本

```bash
dpkg -l | grep mesa
```

看到版本是 `24.0.9-0ubuntu0.1`

```
ii  libegl-mesa0:amd64                            24.0.9-0ubuntu0.1                        amd64        free implementation of the EGL API -- Mesa vendor library
ii  libgl1-amdgpu-mesa-dri:amd64                  1:24.2.0.60200-2009582.24.04             amd64        free implementation of the OpenGL API -- DRI modules
ii  libgl1-amdgpu-mesa-glx:amd64                  1:24.2.0.60200-2009582.24.04             amd64        free implementation of the OpenGL API -- GLX runtime
ii  libgl1-mesa-dri:amd64                         24.0.9-0ubuntu0.1                        amd64        free implementation of the OpenGL API -- DRI modules
ii  libglapi-amdgpu-mesa:amd64                    1:24.2.0.60200-2009582.24.04             amd64        free implementation of the GL API -- shared library
ii  libglapi-mesa:amd64                           24.0.9-0ubuntu0.1                        amd64        free implementation of the GL API -- shared library
ii  libglu1-mesa:amd64                            9.0.2-1.1build1                          amd64        Mesa OpenGL utility library (GLU)
ii  libglx-mesa0:amd64                            24.0.9-0ubuntu0.1                        amd64        free implementation of the OpenGL API -- GLX vendor library
ii  mesa-amdgpu-va-drivers:amd64                  1:24.2.0.60200-2009582.24.04             amd64        Mesa VA-API video acceleration drivers
ii  mesa-common-dev:amd64                         24.0.9-0ubuntu0.1                        amd64        Developer documentation for Mesa
ii  mesa-va-drivers:amd64                         24.0.9-0ubuntu0.1                        amd64        Mesa VA-API video acceleration drivers
ii  mesa-vdpau-drivers:amd64                      24.0.9-0ubuntu0.1                        amd64        Mesa VDPAU video acceleration drivers
ii  mesa-vulkan-drivers:amd64                     24.0.9-0ubuntu0.1                        amd64        Mesa Vulkan graphics drivers
```

根据日志，升级mesa到 `24.2.0`应该就可以。解决方法如下

```bash
sudo add-apt-repository ppa:kisak/kisak-mesa
sudo apt update
sudo apt upgrade
```

## **参考链接**

* <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html>
* <https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md>
* <https://blog.lyric.im/p/using-llamacpp-to-run-llama-2-using-amd-radeon-rx-6900-for-gpu-acceleration>
* <https://askubuntu.com/questions/1420736/settings-window-does-not-open-in-ubuntu-22-04>
