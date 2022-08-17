---
layout: post
title: "访问Docker容器中服务的三种方式"
date: 2022-08-16 20:33:22 +0800
categories: 技术
tags: Docker
---

在同一个宿主机上一个服务需要访问另一个服务，比如常见的web服务需要链接mysql等数据库。这里有三种方式来实现。
我之前大多采用第一种方式，我这里建议使用第三种方式。

## `端口映射后使用宿主机的IP来访问`

```bash
# 启动mysql容器映射3306端口
docker run -d --name mysql -p 3306:3306 mysql:8
# 通过宿主机IP来连接mysql
docker run --rm -it mysql:8 mysql -h 192.168.1.123 -u root -p
```

## `--link`

```bash
# 启动mysql容器
docker run -d --name mysql mysql:8
# 启动一个alpine容器连接到mysql网络来测试与mysql是否连通
docker run --rm -it --link mysql alpine ping mysql
```

⚠️ 注意该方法后续不建议使用，后续可能回被移除

> The --link flag is a legacy feature of Docker. It may eventually be removed. Unless you absolutely need to continue using it, we recommend that you use user-defined networks to facilitate communication between two containers instead of using --link. One feature that user-defined networks do not support that you can do with --link is sharing environment variables between containers. However, you can use other mechanisms such as volumes to share environment variables between containers in a more controlled way.

## `Use bridge networks`

创建一个docker网络，将需要相互访问的网络都加入到该网络

```bash
# 创建my-net网络
docker network create -d bridge my-net
# 启动mysql容器加入my-net
docker run -d --name mysql --network my-net mysql:8
# 启动一个alpine容器加入my-net网络来测试与mysql是否连通
docker run --rm -it --network my-net alpine ping mysql
```