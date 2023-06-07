---
layout: post
title: "知识库系统Outline搭建过程"
date: 2023-06-07 15:11:42 +0800
categories: 技术
tags: Outline MinIO Authelia docker
---

官方的Docker方式的安装示例是通过Docker Compose来部署的。具体[docker-compose.yml](https://docs.getoutline.com/s/hosting/doc/docker-7pfeLP5a8t)请查看官方文档。由`docker-compose.yml`可以看出Outline服务还需依赖redis、postgres、storage(MinIO)、https-portal（我这里使用Nginx）这四个服务，另外为了完全本地化部署，还需要一个认证服务，我这里使用`Authelia`。

## 配置Authelia

Authelia搭建详见《[Authelia统一认证服务部署](/post/authelia_deploy_gsc0.html)》和《[Authelia为其他服务提供认证](/post/Authelia_as_an_OpenID_Connect_provider_vtwl.html)》

添加 `Outline` client 配置

```yaml
      - id: outline
        description: Outline
        secret: xxxxxxxxxxxxxxxxxxxx
        public: false
        authorization_policy: one_factor
        scopes:
          - openid
          - groups
          - email
          - profile
        redirect_uris:
          - https://example.com:8715/auth/oidc.callback
        userinfo_signing_algorithm: none
```

## 部署MinIO

```bash
docker run -d --name minio \
  -p 8013:8013 -p 8014:8014 \
  -v /configs/minio/data:/data \
  -e MINIO_ROOT_USER=<your_user> -e MINIO_ROOT_PASSWORD=<your_password> \
  quay.io/minio/minio server /data --address ":8013" --console-address ":8014"
```

MinIO有两个服务（API提供接口和Console提供后台管理页面），Outline在调用MinIO API的时候要求https，有两种方式使其支持HTTPS，一是使用Nginx反向代理，二是直接为MinIO添加ssl证书

### Nginx反向代理

代理MinIO API

```properties
server {
  listen 8713 ssl http2;
  listen [::]:8713 ssl http2;
  server_name  _;
  ssl_certificate     path/to/public.crt;
  ssl_certificate_key path/to/private.key;
  error_log /var/log/nginx/minio_api_error.log error;
  access_log /var/log/nginx/minio_api_access.log combined;

  client_max_body_size 1024m;

  location / {
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-NginX-Proxy true;
    real_ip_header X-Real-IP;

    proxy_pass http://127.0.0.1:8013/;
  }
}
```

代理MinIO Console

```properties
server {
  listen 8714 ssl http2;
  listen [::]:8714 ssl http2;
  server_name  _;
  ssl_certificate     path/to/public.crt;
  ssl_certificate_key path/to/private.key;
  error_log /var/log/nginx/minio_console_error.log error;
  access_log /var/log/nginx/minio_console_access.log combined;

  client_max_body_size 1024m;

  location / {
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-NginX-Proxy true;
    real_ip_header X-Real-IP;

    proxy_pass http://127.0.0.1:8014/;
  }
  location /ws/ {
    proxy_redirect off;
    proxy_pass http://127.0.0.1:8014;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }
}
```

> MinIO后台页面需要访问WebSocket，路径为`/ws/`，也需要使用nginx代理。

### 直接为MinIO添加SSL证书

官方文档地址：https://min.io/docs/minio/linux/operations/network-encryption.html

MinIO 在`${HOME}/.minio/certs`目录中搜索 TLS 密钥和证书.

将SSL证书文件映射到容器内`/root/.minio/certs`目录下的`private.key`和`public.crt`。

## 部署Outline

在搭建好 MinIO 后，登陆到后台，创建一个名为outline的Bucket，并创建一个`Access Keys`，记下对应的`Access Key`和`Secret Key`。

然后创建一个`docker.env`文件，并根据[.env示例文件](https://github.com/outline/outline/blob/main/.env.sample)填写相关配置。


```properties
NODE_ENV=production
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
UTILS_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgres://test:123456@100.100.100.100:5432/outline
PGSSLMODE=disable
REDIS_URL=redis://:123456@100.100.100.100:6379/2
URL=https://example.com:8715
PORT=8015

AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1
AWS_S3_ACCELERATE_URL=
AWS_S3_UPLOAD_BUCKET_URL=https://example.com:8713/
AWS_S3_UPLOAD_BUCKET_NAME=outline
AWS_S3_UPLOAD_MAX_SIZE=26214400
AWS_S3_FORCE_PATH_STYLE=true
AWS_S3_ACL=private

OIDC_CLIENT_ID=outline
OIDC_CLIENT_SECRET=xxxxxxxxxxxxxxxxxx
OIDC_AUTH_URI=https://auth.example.com/api/oidc/authorization
OIDC_TOKEN_URI=https://auth.example.com/api/oidc/token
OIDC_USERINFO_URI=https://auth.example.com/api/oidc/userinfo
OIDC_USERNAME_CLAIM=preferred_username
OIDC_DISPLAY_NAME=Authelia
OIDC_SCOPES=openid profile email

FORCE_HTTPS=false

SMTP_HOST=mail.example.com
SMTP_PORT=8005
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@example.com
SMTP_REPLY_EMAIL=noreply@example.com
SMTP_TLS_CIPHERS=
SMTP_SECURE=false
```

> `SECRET_KEY`和`UTILS_SECRET`可以通过`openssl rand -hex 32`命令来生成。`AWS_ACCESS_KEY_ID`和`OIDC_CLIENT_SECRET`分别对应之前在MinIO中生成的`Access Key`和`Secret Key`。`OIDC` 配置使用Authelia。其他配置根据实际情况填写。

启动Outline

```bash
docker run -d --name outline \
  --env-file /data/webapps/outline/docker.env \
  -p 8015:8015  outlinewiki/outline:latest
```

Nginx代理并提供HTTPS

```properties
server {
  listen 8715 ssl http2;
  listen [::]:8715 ssl http2;
  server_name  _;
  ssl_certificate     path/to/public.crt;
  ssl_certificate_key path/to/private.key;
  error_log /var/log/nginx/outline_error.log error;
  access_log /var/log/nginx/outline_access.log combined;

  location / {
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-NginX-Proxy true;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://127.0.0.1:8015/;
  }
  location ~ /(realtime|collaboration)/ {
    proxy_redirect off;
    proxy_pass http://127.0.0.1:8015;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }
}
```

> Outline也有WebSocket请求，需要代理`/realtime/`和`/collaboration/`这两个WS路径。

## 总结

Outline使用`Business Source License 1.1`开源协议，看起来只要不对外提供服务，自己内部团队使用完全没问题的。试用了一下Outline，界面美观，支持markdown，支持多人同时编辑，评论还可以针对选中的一段字就行评论，和标注差不多，但是评论不支持markdown语法。还支持多种外部文件的嵌入（如draw.io等），整体来说Outline作为团队知识库很不错。

## 参考链接

* https://docs.getoutline.com/s/hosting/doc/hosting-outline-nipGaCRBDu
* https://min.io/docs/minio/container/index.html
