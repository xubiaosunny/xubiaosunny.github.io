---
layout: post
title: "在WSL里用ROCm部署大模型"
date: 2026-10-25 15:30:00 +0800
categories: 技术
tags: AI 大模型 ROCm WSL2 llama.cpp RX6800XT
---

> 本文环境:**Windows + WSL2(Ubuntu 24.04)+ ROCm 10.1(gfx1030)+ llama.cpp(源码编译,HIP 后端)**,显卡还是那块 AMD **RX 6800 XT(16GB 显存)**。

2024 年我写过一篇[《AMD ROCm运行Llama》](/post/2024-08-22-Running_Llama_with_AMD_ROCm_x8eb.html),当时是装原生 Ubuntu 跑 ROCm。这次不想装双系统,直接在 Windows 的 **WSL2** 里,用 **ROCm** 给 6800 XT 跑大模型。

之所以现在可行了,是因为 AMD 为 WSL 推出了开源方案 **ROCDXG(librocdxg)** 并已进入生产级支持:它是一个用户态翻译层,位于 Linux ROCm 运行时和 Windows GPU 驱动之间,走微软的 DXCore 接口(`/dev/dxg`)。官方入口是这篇 WSL How-to:<https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installrad/wsl/howto_wsl.html>

整个流程走下来比较顺畅,下面按「装环境 → 编译 llama.cpp → 跑模型」记录过程,踩过的坑放在文末统一总结。

## ROCm 环境安装

安装步骤(在 WSL 的 Ubuntu 24.04 里):

1. Windows 侧装好最新版 Adrenalin 驱动;
2. 安装 WSL2 和 Ubuntu(24.04/22.04);
3. 按 [ROCm/librocdxg](https://github.com/ROCm/librocdxg) README 的 **Quickstart** 装好 librocdxg;
4. 注册 ROCm 软件源后安装运行时,6800 XT 是 gfx1030,用 gfx1030 专用包:

   ```bash
   sudo apt install amdrocm10.1-gfx1030
   ```
5. 把当前用户加入 `render`、`video` 组,重启 WSL(`wsl --shutdown`)。

注意:WSL 里只需要 ROCm 计算组件,**不要**装 Linux 显示驱动(图形驱动归 Windows 宿主机管)。

装完验证:

```bash
export HSA_ENABLE_DXG_DETECTION=1
rocminfo
```

输出里有这两处,基本就成功了:

```text
WSL environment detected.
...
Agent 2
   Name:                    gfx1030
   Marketing Name:          AMD Radeon RX 6800 XT
```

`"WSL environment detected."` 说明 librocdxg 正常加载;Agent 2 识别出 gfx1030、72 个计算单元、显存约 15.96 GiB。建议把 `export HSA_ENABLE_DXG_DETECTION=1` 写进 `~/.bashrc` 一劳永逸。

> 提醒:WSL 里没有 `/dev/kfd`,`rocm-smi` 会报 `amdgpu not found`,这都是正常现象,验证一律用 `rocminfo`。

## 源码编译 llama.cpp(HIP 后端)

官方构建文档 HIP 一节:<https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#hip>

之所以选择源码编译,是因为预编译版本(llama.app 脚本、Ollama)在 WSL2 里都识别不到 GPU(原因见文末总结),而源码编译的产物直接链接系统 `/opt/rocm`,和 librocdxg 是同一套 ROCm,天然匹配。

安装编译依赖:

```bash
sudo apt install build-essential cmake git libssl-dev
# ROCm 开发包(HIP 编译器、CMake 配置、头文件),编译必需
sudo apt install amdrocm-core-dev10.1-gfx1030
```

然后一条命令编译:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build \
  -DGGML_HIP=ON \
  -DGPU_TARGETS=gfx1030 \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/opt/rocm/core-10.1 \
  -DLLAMA_OPENSSL=ON
cmake --build build --config Release -j 12
```

几点说明:

* `-DGPU_TARGETS=gfx1030` 指定 6800 XT 的架构;老版本文档里叫 `-DAMDGPU_TARGETS`,报"未使用"就换另一个试;
* `-DCMAKE_PREFIX_PATH=/opt/rocm/core-10.1` 必须加,且只能写在 **configure 阶段**(`cmake -S . -B build`)才生效;
* `-j` 按 CPU 核数来,HIP 要为 gfx1030 生成大量 kernel,全核编译要十几分钟,耐心等;
* 编译完不用安装,产物就在 `build/bin/` 下。

验证 GPU:

```bash
export HSA_ENABLE_DXG_DETECTION=1
./build/bin/llama-server --list-devices
```

能列出 RX 6800 XT,就大功告成。

## 跑模型

16GB 显存选模型的经验法则:**权重文件体积至少比可用显存小 3GB**,给 KV cache 和计算缓冲留余量(WSL 下显存本身还有少量损耗)。比如 14B 级 Q4_K_M(约 8~9GB)很宽裕,27B 级 3-bit 量化(约 12GB)刚好能塞下;再大的量化档位放不进,溢出的层落到 CPU,速度会断崖式下跌。

启动:

```bash
./build/bin/llama-server \
  -m ~/models/xxx.gguf \
  -ngl 99 -c 4096 \
  --host 127.0.0.1 --port 8080
```

* `-ngl 99`:尽量把所有层塞进 GPU;
* `-c` 上下文从 4096 起步,稳定后再加;
* 确认吃上 GPU 有三处:启动日志出现 `offloaded xx/xx layers to GPU`(理想是全层);Windows 任务管理器 → 性能 → GPU 的「专用显存」被吃掉 10GB+;浏览器打开 `http://localhost:8080` 就是自带的 Web UI(也兼容 OpenAI API,可接 Open WebUI 等前端)。

实测 27B 的 3-bit 量化模型打字机速度相当流畅,整体体验达到预期。

## 踩坑总结

过程比较顺,但有几个坑值得单独记一笔:

* **llama.cpp 预编译版(llama.app 一键脚本)在 WSL2 里不可用**:安装时 `Probing ROCm/Vulkan` 全部探测失败,`llama serve --list-devices` 为空,静默装成 CPU 版;
* **Ollama 在 WSL2 里也不可用**:安装脚本靠 `/dev/kfd` 检测 AMD 卡,WSL 里没有这个设备;按文档补装 ROCm 组件包、给 systemd 注入 `HSA_ENABLE_DXG_DETECTION=1` 后依然 `total_vram="0 B"`。根因是 Ollama 自带的是打包好的 ROCm 7.2 运行库,而系统装的是 ROCm 10.1,AMD 文档明确要求 **librocdxg 和 HSA 运行时必须来自同一份构建**,版本错配自然走不通 `/dev/dxg` 的 GPU 发现。预编译产物都是"焊死自带运行时",只有源码编译才能链接系统这套 ROCm;
* **编译必须装 ROCm 开发包**:`amdrocm10.1-gfx1030` 只是运行时,配置阶段会报 `does not contain the HIP runtime CMake package`,需要补装 `amdrocm-core-dev10.1-gfx1030`(运行时 + 编译器 + CMake 配置 + 头文件);figure 命令里;配置失败过要 `rm -rf build` 重来,CMake 会缓存失败配置;
* **漏装 `libssl-dev` 会导致 `-hf` 下载模型失败**:报 `HTTPS is not supported`,构建时 OpenSSL 支持被静默跳过,补装后重新 configure(`-DLLAMA_OPENSSL=ON`)增量编译即可;
* **`HSA_OVERRIDE_GFX_VERSION=10.3.0` 不需要设**:这是给 gfx1031/1034 之类"借架构"的卡用的,6800 XT 原生就是 gfx1030,网上老教程会让你白折腾;
* **RDNA2 + HIP 先别开 KV cache 量化**(`--cache-type-k q8_0` 之类):有 issue 报告会导致处理提示词期间显存持续增长,默认 f16 最稳;运行卡死可试 `export HSA_ENABLE_SDMA=0`(WSL2 里 SDMA 有已知问题)。

## 参考链接

* WSL 官方 How-to(ROCDXG/librocdxg):<https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installrad/wsl/howto_wsl.html>
* ROCDXG 仓库:<https://github.com/ROCm/librocdxg>
* ROCm 安装(gfx1030 包):<https://rocm.docs.amd.com/en/latest/install/rocm.html>
* llama.cpp 构建文档(HIP 后端):<https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#hip>
* 我的前作(原生 Ubuntu + ROCm):[AMD ROCm运行Llama](/post/2024-08-22-Running_Llama_with_AMD_ROCm_x8eb.html)
