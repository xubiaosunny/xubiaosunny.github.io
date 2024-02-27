---
layout: post
title: "Windows 10 LTSC 2021 不能连接SMB共享文件服务问题解决"
date: 2024-02-26 21:12:54 +0800
categories: 折腾
tags: Windows Smaba
---

## 问题描述

在虚拟机中安装了Win10 LTSC 2021系统，并打开了“SMB 1.0/CIFS 文件共享支持”和“启用网络发现”，但任然不能连接samba共享文件服务。
具体现象是可以在【网络】中看到该SMB服务，但是点击打开或者在地址栏输入`\\{ip}`都会报错（错误代码：0x80070035）。

![](/assets/images/post/截屏2024-02-26 21.28.08.png)

## 解决方法

1. 打开注册表

2. 打开路径 `计算机\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters`

3. 将其中参数 `AllowInsecureGuestAuth` 的值改为 `1`。如果该参数不存在的话就右键-新建-DWORD (32位)值(D)。

![](/assets/images/post/截屏2024-02-26 21.29.52.png)

## 必须的设置

### “控制面板”打开 SMB 1.0 支持功能

1. 打开“控制面板”。

2. 选择“程序”>“程序和功能”>“启用或关闭 Windows 功能”>“SMB 1.0/CIFS 文件共享支持”。

3. 检查“SMB 1.0/CIFS 客户端”，然后按 Enter。

![](/assets/images/post/smb-client-feature-on.svg)

### 打开网络发现和文件与打印机共享选项

1. 打开“控制面板”。

2. 选择“网络和 Internet”>“网络和共享中心”>“高级共享设置”。

3. 选择“启用网络发现”。

4. 选择“专用”下的“启用文件和打印机共享”。

5. 选择“保存更改”。

![](/assets/images/post/turn-on-network-discovery-share-settings.svg)

## 参考链接

* https://blog.csdn.net/hzgnet2021/article/details/122081740
* https://learn.microsoft.com/zh-cn/troubleshoot/windows-client/networking/cannot-access-shared-folder-file-explorer
