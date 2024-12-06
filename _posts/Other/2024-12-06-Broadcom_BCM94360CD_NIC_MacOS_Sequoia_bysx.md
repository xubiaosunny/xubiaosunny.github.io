---
layout: post
title: "博通BCM94360CD网卡MacOS Sequoia驱动"
date: 2024-12-06 22:55:14 +0800
categories: 折腾
tags: 黑苹果 MacOS 网卡
---

我的黑苹果从2020年装机到现在已经4年了，当时买了 Fenvi T919 无线网卡（其实就是博通BCM94360CD），免驱。可惜好景不长，到MacOS 14的时候不支持了。
由于看网上BCM94360CD修补后，有软件出问题，而且当时刚好有空闲的AX200，就使用 [itlwm](https://github.com/OpenIntelWireless/itlwm) 驱动了wifi和蓝牙，也能用，但是丢失了隔空投送，且不太稳定，每次更新系统还得禁用相关kext，要不更新过程中会出错。
最近想升级了一下 MacOS 15，而 `AirportItlwm` 现在还不支持。于是就又折腾换回了Fenvi T919，和之前免驱的的时候无差别，隔空投送也回来了。这里记录一下过程。

## 具体步骤

### 1 添加kext文件

将 `AMFIPass.kext` 、 `IOSkywalkFamily.kext` 、 `IO80211FamilyLegacy.kext` 三个kext拷贝到 `EFI` 中的 `OC/Kexts` 文件夹中

对应文件可在[这里](https://github.com/dortania/OpenCore-Legacy-Patcher/tree/main/payloads/Kexts)下载

### 2 编辑 config.plist
**Kernel** → **Add** 中，依次添加 `AMFIPass.kext` 、 `IOSkywalkFamily.kext` 、 `IO80211FamilyLegacy.kext` 这三个kext。

![](\assets\images\post\截屏2024-12-06 22.26.17.png)

**Kernel** → **Block** 中，添加 `com.apple.iokit.IOSkywalkFamily` 。

![](\assets\images\post\截屏2024-12-06 22.27.38.png)

**NVRAM** → **Add** → **7C436110-AB2A-4BBB-A880-FE41995C9F82** 中， `boot-args` 添加两个参数   `ipc_control_port_options=0` 和 `-amfipassbeta` 。`csr-active-config` 修改为 `03080000` 。

![](\assets\images\post\截屏2024-12-06 22.46.28.png)

### 3 使用 [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher) 进行修补

然后重启，在OpenCore引导界面选择 `CleanNvram.efi` 来清除Nvram。

> 如果没有该项，需要在 `EFI` 中的 `OC/Tools` 文件夹下添加 `CleanNvram.efi` 

最后打开 `OpenCore-Patcher.app` 软件，点击 `Post-install Root Patch` ，等执行完重启即可。

## 参考链接

* <https://www.cnblogs.com/coder-wys/p/18457604>
* <https://imacos.top/2024/09/21/89754/>
* <https://github.com/perez987/Broadcom-wifi-back-on-macOS-Sonoma-with-OCLP>