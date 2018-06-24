---
layout: post
title: "MBR转GPT重建win10引导"
date: 2018-06-24 13:43:54
categories: 折腾
tags: ESP UEFI MBR GPT
---

昨天手贱将硬盘分区表由MBR转为GPT（GUID），关机后发现无法启动。这情况就很蛋疼，说不定还得重装系统，想想还要装那么多软件就愁。
马上在网上查解决方案，但基本都是教怎么无损MBR转GPT，但是我这已经转完了。经过一番研究，结合多篇教程终于重建引导成功，这里记录一下。

## 准备工作
两个U盘启动盘，一个写入win10镜像，一个写入PE镜像（维护系统， 可以用大白菜、老毛桃什么的，须集成磁盘工具DiskGenius）。

如果只有一个U盘也可以，先用pe再用win10。

## 重建过程
### 创建ESP分区

开机通过UEFI引导进入PE，使用DiskGenius新建空白分区（200M以上，我分出500M），两种途径：

* 通过调整分区大小形成空白分区
* 一般MBR引导会有一个隐藏分区，可以直接删除该分区得到空白分区

然后在该空白分区上新建分区，文件系统类型要选`EFI system partition`。

接下给该分区分配盘符（我这里分配的是I:），这样我们就可以在计算机上发现该分区了。在该分区建立路径`I:\EFI\Microsoft\Boot\`

## 重建引导

参考 https://www.cnblogs.com/kingstrong/p/7120044.html

关闭PE然后通过UEFI引导从win10启动盘启动。进入修复计算机 -> 疑难解答，可以先试一下【启动项修复】，看看能不能自动修复，我这里是不行的。
如果不能修复打开【命令行工具】。

* 命令`diskpart`进入磁盘工具
* `list vol`所有显示分区信息，在里面找到创建好的ESP分区，我这里是卷4

![](\assets\images\post\2018-06-24_14_33_00.JPG)

* 选中该卷并设置盘符
```
sel vol 4
assign letter=I:
```
* `exit`推出磁盘工具
* `cd /d I:\EFI\Microsoft\Boot\`，cd到创建好的目录
* 重建BCD
```
bootrec /fixboot
bootrec /rebuildbcd
```

然后重启电脑发现win10可以正常引导了