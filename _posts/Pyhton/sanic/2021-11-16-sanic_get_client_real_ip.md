---
layout: post
title: "Sanic获取客户端的真实IP"
date: 2021-11-16 18:33:12 +0800
categories: 技术
tags: Sanic python
---

自己之前写的DDNS脚本最近发现不好使了，查看原因发现是之前获取ip的服务大幅减少免费的请求次数了，我的脚本无法拿到自己的IP了。网上还有很多免费的获取ip的共公服务，
但可能还会发生这样的事，反正我公网上也有服务，加个获取IP地址的接口就可以。

获取ip的API使用python的Sanic框架来实现。

## Nginx 部署

官方文档 

https://sanicframework.org/zh/guide/advanced/proxy-headers.html

有两种方式获得真实ip

### 1.FORWARDED

官方文档 https://sanicframework.org/zh/guide/deployment/nginx.html

```python
from sanic import Sanic
from sanic.response import text

app = Sanic("proxied_example")
app.config.FORWARDED_SECRET = "YOUR SECRET"

@app.get("/")
def index(request):
    # 此处将会显示公网IP
    return text(
        f"{request.remote_addr} connected to {request.url_for('index')}\n"
        f"Forwarded: {request.forwarded}\n"
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=8, access_log=False)
```

nginx配置

```conf
server {
  server_name example.com;
  listen 443 ssl http2 default_server;
  listen [::]:443 ssl http2 default_server;

  location / {
    proxy_pass http://127.0.0.1:8000;
    # Allow fast streaming HTTP/1.1 pipes (keep-alive, unbuffered)
    proxy_http_version 1.1;
    proxy_request_buffering off;
    proxy_buffering off;
    # Proxy forwarding (password configured in app.config.FORWARDED_SECRET)
    proxy_set_header forwarded "$proxy_forwarded;secret=\"YOUR SECRET\"";
    # Allow websockets and keep-alive (avoid connection: close)
    proxy_set_header connection "upgrade";
    proxy_set_header upgrade $http_upgrade;
  }
}
```

> nginx中的<YOUR SECRET>要和sanic的配置app.config.FORWARDED_SECRET一致

新建 `/etc/nginx/conf.d/forwarded.conf`

```
# RFC 7239 Forwarded header for Nginx proxy_pass

# Add within your server or location block:
#    proxy_set_header forwarded "$proxy_forwarded;secret=\"YOUR SECRET\"";

# Configure your upstream web server to identify this proxy by that password
# because otherwise anyone on the Internet could spoof these headers and fake
# their real IP address and other information to your service.


# Provide the full proxy chain in $proxy_forwarded
map $proxy_add_forwarded $proxy_forwarded {
  default "$proxy_add_forwarded;by=\"_$hostname\";proto=$scheme;host=\"$http_host\";path=\"$request_uri\"";
}

# The following mappings are based on
# https://www.nginx.com/resources/wiki/start/topics/examples/forwarded/

map $remote_addr $proxy_forwarded_elem {
  # IPv4 addresses can be sent as-is
  ~^[0-9.]+$          "for=$remote_addr";

  # IPv6 addresses need to be bracketed and quoted
  ~^[0-9A-Fa-f:.]+$   "for=\"[$remote_addr]\"";

  # Unix domain socket names cannot be represented in RFC 7239 syntax
  default             "for=unknown";
}

map $http_forwarded $proxy_add_forwarded {
  # If the incoming Forwarded header is syntactically valid, append to it
  "~^(,[ \\t]*)*([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?(;([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?)*([ \\t]*,([ \\t]*([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?(;([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?)*)?)*$" "$http_forwarded, $proxy_forwarded_elem";

  # Otherwise, replace it
  default "$proxy_forwarded_elem";
}
```

然后访问api就可以通过`request.remote_addr`拿到客户端的ip了。

### 2.配置REAL_IP_HEADER

第一种方式适用于直连的方式，如果api服务套了CDN的话这样就不好使了，拿到的其实是CDN节点的IP。这时候就用第二种方式。

```python
from sanic import Sanic
from sanic.response import json

app = Sanic()
app.config.REAL_IP_HEADER = "cf-connecting-ip"

@app.get("/")
def index(request):
    # 此处将会显示公网IP
    return json({"ip": request.remote_addr})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=8, access_log=False)
```

> REAL_IP_HEADER根据实际情况配置，不同的CDN厂商可能放置IP的header不同

nginx的话就正常配置proxy_pass就行，不需要`proxy_set_header forwarded`

```conf
server {
  server_name example.com;
  listen 443 ssl http2 default_server;
  listen [::]:443 ssl http2 default_server;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header connection "upgrade";
    proxy_set_header upgrade $http_upgrade;
  }
}
```

## 关于Sanic

Sanic使用python的asyncio，宣称高性能，我用压测工具测试了一下我这个API接口，服务器是个1core的KVM云主机，1k并发的毫无问题，调成1w的时候就有很多请求失败了。
确实性能还不错。

Sanic和flask的写法上很像，使用flask项目的目录结构来写Sanic项目也没啥不妥

```
api
├── app.py
├── config.json
├── utils
│   └── response.py
└── views
    ├── __init__.py
    └── ip.py
```
