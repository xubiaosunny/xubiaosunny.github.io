---
layout: post
title: "Smaba搭建共享服务"
date: 2018-08-01 23:13:24
categories: 技术
tags: Samba
---

前段时间开发在公司做了一个云物理几的项目，使用戴尔iDRAC控制卡实现物理机的开关机等操作，并支持远程挂载镜像。我们是搭建samba共享服务来给同一数据中心的物理机提供镜像文件，以便物理机挂载镜像。

samba的搭建环境为ubuntu16.04。

## 安装samba

```shell
apt update
apt install samba samba-common
apt install cifs-utils
```

## 创建 共享目录及log目录

```shell
cd /data/
mkdir share
mkdir log
```

## 为samba创建用户

这里我的用户名为samba，创建用户需设置密码

```shell
adduser samba
smbpasswd -a samba
```

## 修改samba配置文件`/etc/samba/smb.conf`

```
log file = /data/log/samba/log.%m
# 修改log目录到/data/log

# 在配置文件最后添加以下配置
[share]
comment = share
path = /data/share
read only = yes
public = no
valid users = samba
```

## 重启samba服务

```shell
service smbd restart
```

## 验证服务是否可用
在其他机器（需保证与samba服务器网络可通）上执行以下命令，若输入正确密码后可以进去samba命令行即说明共享目录成功

```shell
apt imstall smbclient
# 安装samba客户端

smbclient //<ip>/share -U samba
# <ip> 为samba服务器IP地址，share为目录名应与配置文件中一致
# 示例：smbclient //192.168.34.252/share -U samba
```

然后将需要共享的文件上传到samba服务器上的`/data/share`目录即可

> 文中`/data/share`为服务器目录，`/share`为samba共享服务目录，访问的时候访问的是samba共享服务目录