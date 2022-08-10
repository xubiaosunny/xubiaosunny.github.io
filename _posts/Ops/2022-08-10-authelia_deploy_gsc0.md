---
layout: post
title: "Authelia统一认证服务部署"
date: 2022-08-10 16:20:25 +0800
categories: 技术
tags: Authelia SSO 2FA
---

> 文中的所有示例配置文件中域名是`auth.example.com`，各种加密用的key和secret都为`123456789ABCDEF`，这些配置请根据实际进行替换。并且根据实际情况将配置中的相对路径改为绝对路径。

## 配置

创建目录`authelia`，在目录下创建`configuration.yml`和`users_database.yml`两个配置文件

### `configuration.yml`

```yaml
theme: light
jwt_secret: 123456789ABCDEF
default_redirection_url: https://auth.example.com
server:
  host: 0.0.0.0
  port: 9091
  path: ""
  buffers:
    read: 4096
    write: 4096
  enable_pprof: false
  enable_expvars: false
  disable_healthcheck: false
  tls:
    key: ""
    certificate: ""
log:
  level: debug
authentication_backend:
  refresh_interval: 5m
  file:
    path: ./users_database.yml
    password:
      algorithm: argon2id
      iterations: 1
      key_length: 32
      salt_length: 16
      memory: 1024
      parallelism: 8
storage:
  local:
    path: ./db.sqlite3
  encryption_key: 123456789ABCDEF
session:
  name: authelia_session
  secret: 123456789ABCDEF
  expiration: 3600
  inactivity: 300
  domain: auth.example.com
access_control:
  default_policy: deny
  rules:
    - domain: auth.example.com
      policy: bypass
notifier:
  disable_startup_check: false
  filesystem:
    filename: ./notification.txt
```

配置简介：

* `authentication_backend`用户配置用户认证后端，例子为file认证，可配置ldap认证
* `notifier`配置提醒，例子中使用文件来接收提醒，可配置为STMP邮件发送
* `storage`配置数据存储，例子中使用sqlite，可改为mysql或者postgres等其他数据库
* `access_control`用于配置使用Authelia认证的web服务

具体配置参考:

* 官方文档(https://www.authelia.com/configuration/prologue/introduction/)
* 配置模版(https://github.com/authelia/authelia/blob/master/config.template.yml)

### users_database.yml

使用基于文件的用户服务需要在此文件中配置用户

```yaml
users:
  john:
    displayname: "John Doe"
    password: "$argon2id$v=19$m=65536,t=3,p=2$BpLnfgDsc2WD8F2q$o/vzA4myCqZZ36bUGsDY//8mKUYNZZaR0t4MFFSs+iM"
    email: john.doe@authelia.com
    groups:
      - admins
      - dev
  harry:
    displayname: "Harry Potter"
    password: "$argon2id$v=19$m=65536,t=3,p=2$BpLnfgDsc2WD8F2q$o/vzA4myCqZZ36bUGsDY//8mKUYNZZaR0t4MFFSs+iM"
    email: harry.potter@authelia.com
    groups: []
  bob:
    displayname: "Bob Dylan"
    password: "$argon2id$v=19$m=65536,t=3,p=2$BpLnfgDsc2WD8F2q$o/vzA4myCqZZ36bUGsDY//8mKUYNZZaR0t4MFFSs+iM"
    email: bob.dylan@authelia.com
    groups:
      - dev
  james:
    displayname: "James Dean"
    password: "$argon2id$v=19$m=65536,t=3,p=2$BpLnfgDsc2WD8F2q$o/vzA4myCqZZ36bUGsDY//8mKUYNZZaR0t4MFFSs+iM"
    email: james.dean@authelia.com
```

用户的哈希密码可以通过命令`authelia hash-password -- 'mypass'`生成

```bash
./authelia hash-password -- 'mypass'
# Password hash: $argon2id$v=19$m=65536,t=3,p=4$N210b2F1V1AwWFhPZzNLSw$2fD9Y6EOomWyoLPlDy+8sSr35kt1v9On9lYCIWFZD+w
```

详见官方文档：https://www.authelia.com/configuration/first-factor/file/


## 运行服务

### Docker

> 官方文档：https://www.authelia.com/integration/deployment/docker/

```bash
# 配置文件在 /data/configs/authelia 目录
docker pull authelia/authelia
docker run --rm -it --name authelia \
  -v /data/configs/authelia:/config \
  -p 9091:9091 authelia/authelia
```

### Bare-Metal

裸机运行authelia可以在[github](https://github.com/authelia/authelia/releases)下载authelia的二进制文件来直接运行。

```bash
./authelia --config configuration.yml
```

## Nginx代理

> 官方文档：https://www.authelia.com/integration/proxies/nginx/

`proxy.conf`

```conf
## Headers
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $http_host;
proxy_set_header X-Forwarded-Uri $request_uri;
proxy_set_header X-Forwarded-Ssl on;
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header Connection "";

## Basic Proxy Configuration
client_body_buffer_size 128k;
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503; ## Timeout if the real server is dead.
proxy_redirect  http://  $scheme://;
proxy_http_version 1.1;
proxy_cache_bypass $cookie_session;
proxy_no_cache $cookie_session;
proxy_buffers 64 256k;

## Trusted Proxies Configuration
## Please read the following documentation before configuring this:
##     https://www.authelia.com/integration/proxies/nginx/#trusted-proxies
# set_real_ip_from 10.0.0.0/8;
# set_real_ip_from 172.16.0.0/12;
# set_real_ip_from 192.168.0.0/16;
# set_real_ip_from fc00::/7;
real_ip_header X-Forwarded-For;
real_ip_recursive on;

## Advanced Proxy Configuration
send_timeout 5m;
proxy_read_timeout 360;
proxy_send_timeout 360;
proxy_connect_timeout 360;
```

`auth.example.com.conf`

```conf
server {
    listen 80;
    listen [::]:80;
    server_name auth.example.com;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    include /etc/nginx/ssl.conf;
    server_name auth.example.com;
    location / {
        include /etc/nginx/proxy.conf;
        set $upstream_authelia http://127.0.0.1:9091;
        proxy_pass $upstream_authelia;
    }
}
```

## 参考链接

* https://www.modb.pro/db/375836
* https://www.authelia.com/integration/prologue/get-started/
