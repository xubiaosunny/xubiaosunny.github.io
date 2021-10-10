---
layout: post
title: "wireguard安装配置"
date: 2021-10-10 14:10:29 +0800
categories: 技术
tags: wireguard
---

## 安装

使用docker安装（https://hub.docker.com/r/linuxserver/wireguard）

```bash
docker run -d \
  --name=wireguard \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Asia/Shanghai \
  -e SERVERURL=wireguard.domain.com `#optional` \
  -e SERVERPORT=51820 `#optional` \
  -e PEERS=1 `#optional` \
  -e PEERDNS=auto `#optional` \
  -e INTERNAL_SUBNET=10.13.13.0 `#optional` \
  -e ALLOWEDIPS=0.0.0.0/0 `#optional` \
  -p 51820:51820/udp \
  -v /path/to/appdata/config:/config \
  -v /lib/modules:/lib/modules \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --restart unless-stopped \
  lscr.io/linuxserver/wireguard
```

按实际情况修改`SERVERURL`(服务器域名或者IP)、`SERVERPORT`(端口)以及-v -p的映射参数。

## 配置

配置在容器中`/config/wg0.conf`

默认生成一个peer，多用户配置（peer）如下（在容器中执行添加）：

```bash
mkdir /config/peer2
cd /config/peer2
# 生成一对客户端密匙
wg genkey | tee privatekey-peer2 | wg pubkey > publickey-peer2
# 服务器上执行添加客户端配置代码,ip不要重复
wg set wg0 peer $(cat publickey-peer2) allowed-ips 10.13.13.3/32
# 保存到配置文件
wg-quick save wg0
```

生成客户端配置文件

```bash
cd /config
cp peer1/peer1.conf peer2/peer2.conf
```
将peer1/privatekey-peer2中的内容填入`PrivateKey`中，IP地址改为`10.13.13.3`

```conf
[Interface]
Address = 10.13.13.3
PrivateKey = <cat peer1/privatekey-peer2>
ListenPort = 51820
DNS = 10.13.13.1

[Peer]
PublicKey = ******************
Endpoint = xxxxxxx:51820
AllowedIPs = 0.0.0.0/0
```

根据客户端配置文件生成二维码

```bash
qrencode -t ansiutf8 < peer2.conf
```

多添加peer，重复此步骤即可，修改名称peer2为peer*，不要重复。

配置如果不能链接重启下容器
