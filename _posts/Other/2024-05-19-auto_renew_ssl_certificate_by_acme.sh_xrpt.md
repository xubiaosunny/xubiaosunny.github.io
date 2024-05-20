---
layout: post
title: "使用acme.sh自动申请SSL证书"
date: 2024-05-19 15:18:43 +0800
categories: 折腾
tags: acme.sh Letsencrypt 阿里云
---

## 需求背景

我在国内也有个域名，之前一直使用阿里云的免费证书，有效期一年每年搞一次也还好，但是现在免费证书只给3个月了，免费证书都不支持泛域名的证书。每三个月都得给所有二级域名申请一次，太麻烦了。

本来我自己有一套方案，我之前写的一套自动申请`Let's encrypt`证书并支持其他服务器自动同步的服务[certbot-async](https://github.com/xubiaosunny/certbot-async)。
挺好使的，我自己一直在用，因为我的使用局限当时只对接了`cloudflare`的DNS接口。这是当时写的博客《[Letsencrypt证书一处申请多服务器同步](/post/letsencrypt_certificate_applies_for_multiple_server_synchronization.html)》

我国内的域名在阿里云，想要使用我之前这一套我就需要对接一下阿里云的DNS，但是现在阿里云文档不显示API，只提供SDK，还得装他的SDK，懒得搞这么多依赖了。
好在有找到一个很不错的工具`acme.sh`，支持的SSL证书厂商多，支持的DNS厂商也巨多。在国内我也不需要多服务器同步证书。研究了一下很快就搭建成功了，这里记录一下。

## 部署过程

### 创建单独的sudo用户

为了安全隔离，我这里添加单独用户用于运行acme.sh，当然也可以使用自己的用户或者root都就没问题

```bash
adduser acme
```

申请证书是不需要用sudo权限的，但是如果想要续租证书后自动重启Nginx的话就需要了，我这里只给了这个用户nginx程序的sudo权限

编辑/etc/sudoers文件添加以下内容

```
# 免输入密码sudo执行nginx命令
acme ALL=(ALL:ALL) NOPASSWD:/sbin/nginx
```

### 安装acme.sh

```bash
curl https://get.acme.sh | sh -s email=my@example.com
```

Or:

```
wget -O -  https://get.acme.sh | sh -s email=my@example.com
```

### 切换默认CA

默认CA是zerossl，但是总报504，所以切换使用letsencrypt

```bash
acme.sh --set-default-ca --server letsencrypt
```

文档地址：https://github.com/acmesh-official/acme.sh/wiki/Server

### 申请证书

在~/.acme.sh/acme.sh.env添加阿里云(子)帐号的AccessKey信息，确保该帐号有DNS的权限

```
export Ali_Key="xxxxxxxxxxxxxxxxxxxxxxxxx"
export Ali_Secret="xxxxxxxxxxxxxxxxxxxxxxxx"
```

申请泛域名证书

```bash
acme.sh --issue --dns dns_ali -d example.com -d *.example.com
```

### 安装证书到Nginx

```bash
acme.sh --install-cert -d example.com \
  --key-file /you_path/example.com/key.pem  \
  --fullchain-file /you_path/example.com/cert.pem \
  --reloadcmd "sudo /sbin/nginx -s reload"
```

安装`acme.sh`的时候会默认添加一条crontab定时任务，到时候自动续期证书的时候也会默认执行该操作，实现自动化更新nginx证书。

## 参考链接

* https://github.com/acmesh-official/acme.sh
