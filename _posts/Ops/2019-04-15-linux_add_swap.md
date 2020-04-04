---
layout: post
title: "Linux添加交换空间(SWAP)"
date: 2019-04-15 16:38:44 +0800
categories: 技术
tags: Linux SWAP
---

今天`pip`安装`lxml`的时候总报`gcc`编译错误，google原因后应该是缺少依赖程序包。

```bash
apt-get install build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev
```

安装完发现确实开始编译安装了（之前直接就报错了），然后等了许久发现还是失败了，还是`gcc`

```text
error: command 'aarch64-linux-gnu-gcc' failed with exit status 4
```

于是又google以下，找到了问题的原因，我这1G内存的机器编译的时候内存不足了，网上也给出了解决办法：扩大SWAP空间。

参考：[https://www.cyberciti.biz/faq/linux-add-a-swap-file-howto/](https://www.cyberciti.biz/faq/linux-add-a-swap-file-howto/)

## 添加交换空间

添加512MB的交换空间

```bash
# 生成交换文件
dd if=/dev/zero of=/swapfile1 bs=1024 count=524288

# 设置文件权限
chown root:root /swapfile1
chmod 0600 /swapfile1

# 设置Linux交换区域
mkswap /swapfile1

# 激活/swapfile1交换空间
swapon /swapfile1
```

这样添加的交换空间是临时的，重启会失效，如果想要永久添加此交换空间，在`/etc/fstab`中添加以下内容

```config
/swapfile1 none swap sw 0 0
```

## 移除已添加的交换文件空间

```bash
swapoff -v /swapfile1
rm /swapfile1
```

## 查看交换空间

查看交换空间总量

```bash
free -m
```

查看所有交换空间详情

```bash
swapon -s
# cat /proc/swaps
```
