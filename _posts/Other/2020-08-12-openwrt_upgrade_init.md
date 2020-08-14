---
layout: post
title: "OpenWrt升级固件恢复笔记"
date: 2020-08-12 18:33:35 +0800
categories: 折腾
tags: OpenWrt
---

每次升级OpenWrt固件，之前的软件包都会丢失。为了方便以后升级快速恢复，记录一下。

## 备份

* /etc/dnsmasq.d/dnsmasq_gfwlist_ipset.conf
* /etc/dnsmasq.d/my_gfwlist_ipset.conf

## 汉化

```
opkg update
opkg install luci-i18n-base-zh-cn 
```

## 挂载外置存储

### 安装所需软件包

```bash
opkg install kmod-usb-storage
opkg install block-mount
opkg install e2fsprogs
opkg install kmod-fs-ext4
```

### 自动挂载分区

```bash
block detect > /etc/config/fstab

uci set fstab.@mount[0].enabled='1'
uci commit
```

重启路由器使用`block info`查看是否正确挂载

## 安装软件到外置存储

### 编辑`/etc/opkg.conf`添加如下内容

```
dest usb /mnt/sda1/optware
```

### 编辑`/etc/profile`添加如下内容

```
export LD_LIBRARY_PATH="/mnt/sda1/optware/usr/lib:/mnt/sda1/optware/lib"
export PATH=$PATH:/mnt/sda1/optware/usr/bin:/mnt/sda1/optware/usr/sbin
```

### 安装软件到外置存储

```
opkg install XXXX -d usb
```

## 网络分流

### 安装dnsmasq-full和ipset

```
opkg install ipset
opkg remove dnsmasq && opkg install dnsmasq-full
```

### 编辑`/etc/dnsmasq.conf`添加如下内容

```
conf-dir=/etc/dnsmasq.d
```

### 将ipset配置文件放入`/etc/dnsmasq.d`

dnsmasq_gfwlist_ipset.conf(通过gfwlist2dnsmasq.sh生成)
my_gfwlist_ipset.conf(我自己定义的域名规则)

### 通过iptables分流

网络 -> 防火墙 -> Custom Rules

```
ipset -N gfwlist iphash
ipset add gfwlist 8.8.8.8

iptables -t nat -N GFW
iptables -t nat -A GFW -p tcp -m set --match-set gfwlist dst -j REDIRECT --to-port 1090

iptables -t nat -A GFW -d 0.0.0.0/8 -j RETURN
iptables -t nat -A GFW -d 10.0.0.0/8 -j RETURN
iptables -t nat -A GFW -d 127.0.0.0/8 -j RETURN
iptables -t nat -A GFW -d 169.254.0.0/16 -j RETURN
iptables -t nat -A GFW -d 172.16.0.0/12 -j RETURN
iptables -t nat -A GFW -d 192.168.0.0/16 -j RETURN
iptables -t nat -A GFW -d 224.0.0.0/4 -j RETURN
iptables -t nat -A GFW -d 240.0.0.0/4 -j RETURN

iptables -t nat -A OUTPUT -p tcp -j GFW
iptables -t nat -A PREROUTING -s 192.168/16 -j GFW
iptables -t nat -A POSTROUTING -s 192.168/16 -j MASQUERADE
```

## 添加启动项

openwrt的启动项是类似与ubuntu的service这样的守护进程。

以KMS激活服务的启动项为例来为openwrt添加一个启动项，在`/etc/init.d`目录下添加文件`vlmcsd`并写入以下内容：

```
#!/bin/sh /etc/rc.common

START=99

USE_PROCD=1
NAME=vlmcsd
PROG=/mnt/sda1/app/vlmcsd-mips16el-openwrt-uclibc-static

start_service() {
	procd_open_instance
	procd_set_param command "$PROG" -D
	procd_close_instance
}
```

## 参考链接

* https://openwrt.org/zh/docs/guide-user/storage/usb-drives
* https://www.jianshu.com/p/5549241429d0
* https://www.itgeeker.net/openwrt-dnsmasq-full-install-and-config/
* https://openwrt.org/docs/guide-user/services/vpn/openvpn/basic