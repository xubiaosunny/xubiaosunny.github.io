---
layout: post
title: "Tailscale使用以及搭建自己的derp中继服务器"
date: 2022-09-14 18:24:40 +0800
categories: 折腾
tags: Tailscale DERP
---

## Tailscale安装

各平台在这个页面对应点击下载安装（https://tailscale.com/download/）

有UI的平台都比较容易，主要记录一下Linux server 加入Tailscale网络的过程，以Debian 11 为例

1. Add Tailscale’s package signing key and repository:

```bash
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
```

2. Install Tailscale:

```bash
sudo apt-get update
sudo apt-get install tailscale
```

3. Connect your machine to your Tailscale network and authenticate in your browser:

```bash
sudo tailscale up
```

> 在这一步将命令行的连接复制到浏览器打开认证即可。并且可以通过`--advertise-routes`来设置子网转发，例如`sudo tailscale up --advertise-routes=10.0.0.0/24,10.0.1.0/24`

4. You’re connected! You can find your Tailscale IPv4 address by running:

```bash
tailscale ip -4
```


## 搭建derp中继服务器（Docker）

Dockerfile

```dockerfile
FROM golang:1.19
# 在国内可以加上这行使用国内源
# RUN go env -w  GOPROXY=https://goproxy.cn,direct
RUN go install tailscale.com/cmd/derper@main
ENTRYPOINT ["/go/bin/derper"]
```

构建镜像

```bash
docker build . -t derper:latest
```

docker运行derper服务

```bash
docker run -d --name derper -p 8001:8001 -p 3478:3478/udp derper -a :8001
```

使用`--verify-clients`参数开启验证，防止他人使用我们的derper，开启客户端验证的话需要该derper也是Tailscale节点

```bash
docker run -d --name derper \
-v /var/run/tailscale/tailscaled.sock:/var/run/tailscale/tailscaled.sock \
-p 8001:8001 -p 3478:3478/udp 
derper -a :8001 --verify-clients
```

使用nginx配置https并代理derper，以域名`derper.example.com`为例，在`/etc/nginx/conf.d/derper.example.com.conf`文件中写入如下配置

```conf
server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  ssl_certificate     /data/ssls/derper.example.com/derper.example.com.pem;
  ssl_certificate_key /data/ssls/derper.example.com/derper.example.com.key;

  server_name derper.example.com;
  client_max_body_size 500M;

  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

relaod配置

```bash
nginx -s reload
```

## 配置 acls

https://login.tailscale.com/admin/acls

```json
...

    "derpMap": {
        "OmitDefaultRegions": true,
        "Regions": {
            "900": {
                "RegionID":   900,
                "RegionCode": "myderp",
                "Nodes": [
                    {
                        "Name":     "1",
                        "RegionID": 900,
                        "HostName": "derper.example.com",
                        "STUNPort": 3478,
                        "DERPPort": 443,
                    },
                ],
            },
        },
    },

...
```
