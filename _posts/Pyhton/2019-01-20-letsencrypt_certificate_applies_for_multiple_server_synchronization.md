---
layout: post
title: "Letsencrypt证书一处申请多服务器同步"
date: 2019-01-20 13:12:31
categories: 技术
tags: https Letsencrypt python
---

我自己域名的SSL证书都是使用的`Letsencrypt`，不但免费而且使用`certbot`申请也特别方便快速。之前都是申请单域名的证书，在每个需要的服务器上分别单独申请。开始需要证书的服务少还好，后来越来越多了，自己的一个小网站、nextcloud服务器、openVPN、家里的路由器后台、openmediavault等，这样的话在每个机器上都得申请一次，太繁琐。而`Letsencrypt`支持泛域名申请，那么我们就可以在一台服务器上申请然后同步到其他服务器上。

于是我抽空这两天简单撸了一个Letsencrypt证书自动续租及其他服务器自动同步的程序。项目地址：

[https://github.com/xubiaosunny/certbot-async](https://github.com/xubiaosunny/certbot-async)

具体使用方法参见项目的`README.md`

服务运行模式为 客户端-服务器 模式，代码使用python3开发。

整套服务的两种工作模式：

* 主动式（相对于客户端而言）

该模式就是客户端自动请求服务端，如果发现证书已经变动则下载证书。可以将客户端脚本加入`crontab`，让脚本定时检查服务端证书的变化，并获取。这种方式相对于订阅模式缺乏实时性，但也影响不大，Letsencrypt证书续租一次三个月有效期，而只能提前30天续租，只要客户端更新及时，不会逾期也，可以定时任务设置为每天运行。

* 订阅模式

该模式讲究实时性，只要服务端续租成功将马上将证书同步到已经订阅服务的客户端服务器上。客户端订阅的时候会将服务端的ssh公钥注入到本地，已方便服务端免密码同步证书文件。服务端免密同步使用`rsync`。客户端也需要加入`crontab`来不断订阅，因为订阅的有效期为60天。
