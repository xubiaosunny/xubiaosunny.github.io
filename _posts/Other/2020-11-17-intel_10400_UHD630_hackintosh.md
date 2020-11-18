---
layout: post
title: "10400核显+昂达B460SD4打造丐版黑苹果"
date: 2020-11-17 20:18:06 +0800
categories: 折腾
tags: 黑苹果 OpenCore Intel 10400
---

由于习惯载macOS系统下开发，公司一般给配win本，用不习惯。工作我一直使用16年购买的15款的配置为8+256的MacBookPro，一般自带电脑公司会给补贴。现在算下来估计补贴回4千多块钱估计。
但现在手里干活的工具用着有些不趁手，开两个Pycharm，开两个vscode内存，chrome再开几个页面就满了，虚拟内存经常载4个G左右，而且在各种编译的时候，cpu都打满各种操作都卡卡的。
也到不是卡的不能用，就是开发体验不太好。而且也想使用性能较好的设备。。。于是在征得家里领导的同意后，便在双十一期间购买了硬件装了一台黑苹果在公司办公用。

为了压缩预算，本次装机的所有配件除内存条外均在陪多多购买，使用月卡券或黑卡价格都还不错，配置如下：

* CPU：Intel I5-10400散片 （¥1014）
* 主板：昂达B460SD4 （¥360）
* 内存：玖合-DDR4-2666-32G （¥389）
* 硬盘：铠侠RC10-500G （¥319）
* 电源：先马500p （¥194）
* 无线网卡： Fenvi T919 （¥215）
* 机箱：金河田Meta3s （¥220）
* CPU风扇：超频3红海mini增强版 （¥19）

## 黑苹果安装

具体U盘制作可以参考我之前的黑苹果博客《[讯景RX460安装黑苹果](/折腾/2018/07/31/XFX_RX450_Creating_Hackintosh.html)》和
《[AMD 3700x使用vanilla安装黑苹果](/折腾/2020/06/23/amd_3700x_b450_hackintosh.html)》，
这里我主要记录一下安装过程中遇到的问题，主要是驱动核显来显示和计算的问题。

另外还是参考一下[Dortania's OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)，这里面
对各代CPU的OpenCore配置的介绍十分详细。

我大体上是抄的[司波图的作业](https://www.bilibili.com/video/av753491352/)，不同的是我没有独显，用的也不是es版的U。

基本的EFI模版用的也是司波图的，然后更新了OpenCore的版本到0.6.3，更新`VirtualSMC.kext`、`Lilu.kext`、`AppleALC.kext`、
`WhateverGreen.kext`等核心驱动到最新。因为司波图用的独显，他把核显的缓存帧设置为不输出显示来启用核显加速，这里我没有独显，
要用核显来显示，根据[Dortania](https://dortania.github.io/OpenCore-Install-Guide/config.plist/comet-lake.html#deviceproperties)
文档将缓存帧设置为`07009B3E`或`00009B3E`。

### 使用恢复模式安装

之前我安装黑苹果都是全镜像直接安装，因为下载缓慢和u盘（4块5的夏科32GU盘）写入也慢，于是还是采用恢复镜像的方式来安装。
使用`gibMacOS`制作好u盘后，开机引导进入安装界面点击【重新安装macOS】，然后我这报了一个问题`未能与恢复服务器取得联系`，
这其实是本地时间与服务器时间不一致导致的，具体可以参[知乎的这个回答](https://www.zhihu.com/question/282626105)。

我这使用`date`命令返回的时间跟本地时间是一样的，但是后面显示区时是UTC。于是将当前时间减去8小时然后使用`date`命令来重新设置下时间就好了。
然后一直等待从网络下载安装即可。

## 完善驱动

在安装完，还是有许多不完美的地方，主要还是集中在核显上，不得不说的是200多买的黑苹果免驱网卡还是不错的，wifi、蓝牙、隔空投送、随航等都没有问题，
更吊的是我的蓝牙键盘在没有进入系统还在OpenCore界面就可以连上蓝牙来操作选择。

### 显示发紫

网上网友有说到是因为默认识别主板的输出接口是DP，只有配置手动为HDMI即可，这里需要用到[Hackintool](https://github.com/headkaze/Hackintool)，
具体操作可以参考[这篇文章](https://blog.skk.moe/post/hackintosh-fix-magenta-screen/)。

![](\assets\images\post\1605687603578.jpg)

> `00080000`代表HDMI，`00040000`代表DP。

### 休眠后唤醒无法亮屏，插拔HDMI才能点亮

这个问题[Dortania上就有解决方法](https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/extended/post-issues.html#coffee-lake-systems-failing-to-wake)。

* 添加`igfxonln=1`到引导参数
* 确保您使用的是WhateverGreen v1.3.8或更高版本

![](\assets\images\post\1605688553309.jpg)

### 无法核显加速，微信等打不开，强制开启HIDPI不成功

解决完显示发紫和唤醒不亮屏后，显示正常了，但微信登陆就奔溃，我的2k屏开启HIDPI只有两个分辨率的HIDPI。应该是无法进行核显计算的缘故，看网上的案例应该PS等也是无法打开的。

解决办法是先删除司波图的EFI中多余的驱动`FakePCIID_Intel_HDMI_Audio.kext`和`FakePCIID.kext`（同时也在config.list中删除），
然后使用缓存帧`00009B3E`来进行相应配置，详细如下：

![](\assets\images\post\1605691620578.jpg)

其中的`framebuffer-con0-*`和`framebuffer-con2-*`不用配置也可以，`framebuffer-con1-*`是昂达这个板子的HDMI的配置。

> 配置操作可以参考[这里](https://www.bilibili.com/video/bv1sK411n7sk/)

### 声卡不能使用

昂达的声卡芯片使用的是Realtek的ALC662，根据[AppleALC支持列表](https://github.com/acidanthera/AppleALC/wiki/Supported-codecs)
添加`alcid=5`到引导参数。

![](\assets\images\post\1605688553309.jpg)

## 后续

和网上的测评一致，我这个10400能跑到单核4.3GHz，全核4.0GHz。需要在bios中设置PL1为95W，并将overclocking lock打开，否则只能到全核3.4GHz。

![](\assets\images\post\1605679408260.jpg)

几天使用下来，很完美，顺利替换下我之前的MacBook Pro。今年下半年显卡涨的有点多，A卡挖矿，等价格下来再花个300收个二手470，也方便接多个显示器，也不用折腾核显的这么多问题。

最近苹果M1也发布了，看起来还挺强，以后黑苹果可能就不行了或者没这么完美了，不能话较少的钱来得到较强的macOS体验了，所以且黑且珍惜。
