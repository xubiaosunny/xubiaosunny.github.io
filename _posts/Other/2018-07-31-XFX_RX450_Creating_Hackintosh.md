---
layout: post
title: "讯景RX460安装黑苹果"
date: 2018-07-31 23:05:09
categories: 折腾
tags: RX460 黑苹果
---
前段时间开始搞黑苹果，当时挺有兴趣的，搞了一周没搞定，在网上发现讯景这个牌子的A卡都驱动不了，后来就放弃了。我的台式机配置为`I3-6100`+`华硕H110-k`+`讯景RX460 4GB`+`光威DDR4 2133 8G`。上周末在远景论坛看到有人使用讯景RX560安装黑苹果成功了，于是又激起了我的兴趣，给显卡刷了Bios，居然很顺利装好了，如果有配置类似的可以联系我分享一下我的EFI文件。

## 制作安装U盘

两种方法不细说了，直接上链接。

1. TrashMac

    [https://osx.cx/macos-high-sierra-10-13-xhackintosh-installation-tutorial.html](https://osx.cx/macos-high-sierra-10-13-xhackintosh-installation-tutorial.html)

    镜像下载地址(10.13.5)：[https://osx.cx/macos-high-sierra-10-13-5-17f77.html](https://osx.cx/macos-high-sierra-10-13-5-17f77.html)

    这个镜像做完驱动基本上都是全的，我就是用的这个

2. UniBeast

    [https://www.tonymacx86.com/threads/unibeast-install-macos-high-sierra-on-any-supported-intel-based-pc.235474/](https://www.tonymacx86.com/threads/unibeast-install-macos-high-sierra-on-any-supported-intel-based-pc.235474/)

### 配置config.plist
[https://github.com/RehabMan/OS-X-Clover-Laptop-Config](https://github.com/RehabMan/OS-X-Clover-Laptop-Config)

选择自己机器配置的config文件替换clover下的config.plist
我选的是`config_HD515_520_530_540.plist`(i3-6100核心显卡为HD530)

## 刷显卡Bios

bios文件可以在[这里](https://www.techpowerup.com/vgabios/?architecture=AMD&manufacturer=Asus&model=RX+560&version=&interface=&memType=&memSize=&since=)下载，选择对应型号的进行下载。

刷显卡Bios的方法参考[这里](http://mybt.cn/html/shishang/18.html)。刷之前记得备份原bois，下载`atiflash`和`atikmdag-patcher`。

1. 管理员打开cmd并进入到atiflash程序所在文件夹

2. 解锁显卡 bios
    ```
    AtiFlash.exe -unlockrom 0
    ```
3. 写入bois
    ```
    AtiFlash.exe -f -p 0 xxx.rom
    ```
4. 使用`atikmdag-patcher`破解签名（否则win下的新驱动不能使）。
5. 重启电脑

如果重启正常且windows可以驱动那么一般没啥问题。我开始刷了蓝宝石的、刷了华硕的一个4GB版本的都不好使，最严重黑屏不能启动，后来用核显进系统重新在刷，包括刷了备份的原版bios都不好使，后来刷了华硕的game的bios就好了，切频率由1220升到了1335，玩GTA5测试了一下也没有问题。

## 安装

uEFI引导进入clover，-v模式进入u盘。如果没有问题就会进入安装界面，然后格盘安装。之后会重启两次进入硬盘安装。我在第一次进硬盘安装的时候卡住，后来把主板bios上的快速启动关闭就过去了。如果要报错只能上网查。

## 驱动硬件

我安装完成大部分硬件都以驱动，只有声卡没有驱动，我的声卡为`ALC887`。解决办法是config里Audio Inject设置为5。重启后选择输出设备为`内置扬声器`即可。

## 收尾

使用`Clover Configurator`挂载系统的ESP分区，将U盘中EFI下的clover文件夹拷贝到ESP分区的EFI文件夹下，然后到windows下使用easyUEFI新建clover引导项并将其放到第一位。

想要美化clover可以下载主题或自己制作一个。

完。