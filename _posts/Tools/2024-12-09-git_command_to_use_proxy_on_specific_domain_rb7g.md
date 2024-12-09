---
layout: post
title: "Git命令在特定域名使用代理"
date: 2024-12-09 12:18:35 +0800
categories: 技术
tags: Git Github
---

## 问题背景

我们公司IT真是不拿程序员当员工，网络策略把 `Github` 都给禁了，你禁个视频网站啥的都能理解，禁Github也是服了。IT可能新来的，说不太清楚，给看看，一直也没个下文了。所以就自己通过走代理来绕过公司的网络来使用。 

## Git代理

在公司网络下会报如下错误

```
致命错误：无法访问 'https://github.com/xx/xxx.git/'：SSL certificate problem: unable to get local issuer certificate
```

我还以为我电脑的 `OpenSSL` 什么的包有问题，折腾了好久，后来通过 `git config --global http.sslVerify false` 关闭了ssl验证才发现，请求被转到 `1.1.1.1` 了，想到之前公司禁用的网站都是转到 `1.1.1.1` ，这才发现是公司网络的问题。浏览器访问的时候因为直接连接太慢默认一直是走代理的，所以一直也没发现。这里就有个疑问是我PAC规则是全局的，为啥在git命令上不生效，而浏览器却没问题。

不管了既然改变不了公司网络那只能自己解决。使用如下命令为 `git` 添加代理

```bash
git config --global http.proxy socks5://127.0.0.1:1080
# 取消代理
git config --global --unset http.proxy
```

或者在 `.gitconfig` 中添加如下内容

```ini
[http]
	proxy = socks5://127.0.0.1:1080
```


## Git只代理特定域名

这样后来又发现问题，因为有内网的git服务，现在所有git请求都走代理了，所以又会报如下错误。

```
致命错误：无法访问 'https://gitlab.example.com/xx/xxx.git/'：OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to gitlab.example.com:443 
```

可以这样解决（指定github.com走代理，其他git服务不走代理）

```bash
git config --global http.https://github.com.proxy socks5://127.0.0.1:1080
# 取消代理
git config --global --unset http.https://github.com.proxy
```

或者在 `.gitconfig` 中添加如下内容

```ini
[http "https://github.com"]
	proxy = socks5://127.0.0.1:1080
```

## 参考链接

* https://gist.github.com/laispace/666dd7b27e9116faece6