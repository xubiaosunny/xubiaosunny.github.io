---
layout: post
title: "北京联通hg2543c1光猫改桥接"
date: 2021-11-18 18:26:16 +0800
categories: 折腾
tags: ipv6
---

之前都是光猫拨号，自己的路由器作为二级路由器。用着也没啥问题，但现在各大运营商都已经相应国家号召都提供了ipv6，我现在的网络架构有个问题就是路由器本身是光猫分配ip可以拿到ipv6，
但我路由器下面的所有设备都没有ipv6，白给的公网ipv6不要白不要。

路由器下的设备想要拿到ipv6有两种方式，一种是路由器接入lan口当交换机和AP用，这样下面的ip全由光猫来分配管理，发挥不出我路由器的性能来。另一种就是光猫桥接，路由器来拨号，这样就
可以发挥路由器本身的作用了。

## 开始桥接

本来看网上说打个电话就给改了，但我打了联通客服，人家说得报修才行（客服说之前可以的，但今天技术客服说得报修。估计是比较晚了人家不想给解决了，当时9点），那就得周末了，但我今天就想搞。
于是就有了下面的实践。

大致流程是：[生成当前配置] -> [去掉配置中的地区配置] -> [加载修改后的配置文件] -> [登录维护账户并配置桥接] -> [生成新的配置文件] -> [配置中添加地区配置] -> [加载最终的配置文件]

> ⚠️ `注意备份原始的配置文件以便恢复`

### 获取管理员维护密码

http://192.168.1.1/servmngr.html

在上面的网页开启telent和ftp服务


```bash
# telent登录，输入用户名和密码
telent 192.168.1.1

....
# 生成当前的配置文件，路径在/fhconf/backpresettings.conf
> gendefsettings
```

找到如下位置将`AdminPassword`用base64解密出来就是管理员维护密码，默认是123qweasdzxc

```xml
     <Web>
        <UserPassword>xxxxxxxxx</UserPassword>
        <AdminPassword>MTIzcXdlYXNkenhjAA==</AdminPassword>
        <AdminHideEnable>FALSE</AdminHideEnable>
      </Web>
```

> /fhconf/backpresettings.conf在ftp中可能不显示，可先将其拷贝到/mnt目录下(用sh命令进入sh环境，然后用cp拷贝)


> 在其他地区的话到这一步用维护账户登录后台配置即可，但看网上貌似北京地区限制了维护账号，总是报密码错误。

### 去掉地区配置并加载配置

删掉backpresettings.conf文件中的以下配置

```xml
    <X_FIB_COM_Tr069Control>
      <AreaCode>G</AreaCode>
    </X_FIB_COM_Tr069Control>
```

加载配置，然后光猫会重启。

```bash
loaddefsettings mnt/backpresettings.conf
```

等光猫重启完，在该页面 http://192.168.1.1/cu.html 用维护密码登录修改桥接。

这时候改完桥接是不成功的，因为丢失的地区配置


### 加上地区配置并重新加载配置

首先通过`gendefsettings`命令生成当前桥接的配置，然后在生成配置中加入地区配置

```xml
    <X_FIB_COM_Tr069Control>
      <AreaCode>G</AreaCode>
    </X_FIB_COM_Tr069Control>
```

加载配置，光猫重启后桥接成功。

```bash
loaddefsettings fhconf/backpresettings.conf
```

## 路由拨号

然后在路由器里拨号即可，开启ipv6后，链接到路由器的设备就会分配到ipv6地址。通过[https://test-ipv6.com/](https://test-ipv6.com/)可以测试。

## 参考链接

* https://zhuanlan.zhihu.com/p/103844530
* https://danteng.org/peking-unicom-epon-hg2201u-cracking/
