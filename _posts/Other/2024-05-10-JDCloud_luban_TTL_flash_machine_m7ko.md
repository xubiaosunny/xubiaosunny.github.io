---
layout: post
title: "京东云无线宝鲁班TTL刷机"
date: 2024-05-10 21:00:31 +0800
categories: 折腾
tags: TTL 路由器
---

## 前置阅读

* <https://post.smzdm.com/p/avxgd6r9/>
* <https://www.right.com.cn/forum/thread-8307028-1-1.html>

我主要参考以上两篇文章

整体流程smzdm中的这篇文章写的很详细，我也是按照其流程来做的。

恩山的这个帖子我主要用了其开启ssh的方法和刷机需要的软件（uboot固件，降级固件，ftp软件）

## 刷机过程

### 拆机

确实和smzdm文章作者说的有8个卡扣，拆机确实挺费劲，缝隙很窄，我用一把小刀和一个一字螺丝刀才撬开。没啥说的大力出奇迹！

### 官方固件降级

这里就需要用到TTL进行刷机了。USB转TTL我使用的也是CH340G。

说起串口，大学的时候就是干这个的，我记得我是有这个玩意的，后来找了一圈没找到，估计是之前在闲鱼上和开发板传感器一起出了。。。不过这东西淘宝几块钱，又买一个。

接线方式就是USB的rx接板子的tx，USB的tx接板子的rx，地线接地线（GND）。

我这里用的软件是`PuTTY`，我使用`MobaXterm`能识别到串口但是路由器插电不跑码没动静，换`PuTTY`就正常了。

这里需要注意的点：

* USB转TTL需要装驱动，我的CH340G的驱动是店家给的，实测在win11上也正常驱动。
* 固件读取方式选用的是ftp，就是这个板子要通过ftp下载固件，所以要在本地起一个ftp服务，地址和输入的对应。
* 板子上的引脚注意不要松动，可以焊接上，我是使用皮筋向一个方向拉紧固定的，防止刷机过程中断开。

### 开启SSH

这里的降级固件用的是上面恩山帖子里提供的，具体版本我也没看是哪个版本。但我是进不去`http://192.168.68.1/cgi-bin/luci/`这个OpenWRT原始的后台界面，显示forbidden。但是这个降级估计也提供了开始ssh的方式。

先登录鲁班后台，按F12（或者右键-检查），进入console控制台，输入以下代码直接开启ssh

```javascript
$.ajax({
    url: 'http://' + $.cookie("HostAddrIP") + '/jdcapi',
    async: false,
    data: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "call",
        params: [
            $.cookie("sessionid"),
            "service",
            "set",
            {
                "name": "dropbear",
                "instances": {"instance1": {"command": ["/usr/sbin/dropbear"]}}
            }
        ]
    }),
    dataType: 'json',
    type: 'POST'
})
```

不过现在高版本的chrome或者edge都不让直接在控制台复制粘贴，会报如下警告

```none
Warning: Don't paste code into the DevTools Console that you don't understand or haven't reviewed yourself. This could allow attackers to steal your identity or take control of your computer. Please type 'allow pasting' below and hit Enter to allow pasting.
```

按照提示在控制台输入`allow pasting` 回车后，再次粘贴上面的代码即可

### 刷入uboot

使用ssh登录到路由器

```none
ssh root@192.168.68.1
```

备份原厂分区

```bash
# ssh到路由器执行，备份原厂分区到/tmp
dd if=/dev/mtd2 of=/tmp/factory.bin

# 自己电脑上执行，将路由器中备份拷贝到自己电脑上
scp root@192.168.68.1:/tmp/factory.bin .\Downloads\
```

刷入uboot

```bash
# 自己电脑上执行，将uboot上传到路由器中
scp .\u-boot-mt7621-68.bin root@192.168.68.1:/tmp/

# ssh到路由器执行，将uboot写入分区
cd /tmp
mtd write u-boot-mt7621-68.bin /dev/mtd0
```

### 刷入第三方固件

我也是用的`ImmortalWRT`，我本来一直使用原生OpenWRT，但是原生OpenWRT不支持无线宝路由器。

Kernel和Sysupgrade固件包都需要下载，在uboot界面上传Kernel包，然后登入`ImmortalWRT`后台在上传Sysupgrade包写入。

鲁班的固件型号是`JD-Cloud RE-CP-02`。

