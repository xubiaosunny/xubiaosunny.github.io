---
layout: post
title: "XWiki对接OpenID Connect认证系统"
date: 2023-03-13 20:20:03 +0800
categories: 技术
tags: OIDC XWiki Authelia Nginx
---

研究XWiki对接OIDC认证花了不少时间，主要还是由于网上资料较少尤其是中文资料，而且涉及到的扩展官方文档也不够详细，过程中主要有两个难点：

* 非标准端口认证过程中的转跳不正确
* 接入OIDC认证后与原有账户的关联问题

本文使用的OpenID Connect的服务是 Authelia

## Nginx反向代理XWiki

由于OpenID Connect需要以TLS为基础，所以使用Nginx反向代理XWiki为其提供https服务，配置如下

```nginx
server {
  listen 8443 ssl http2;
  listen [::]:8443 ssl http2;
  server_name  _;
  include ssl/nginx_ssl.conf;
  error_log /var/log/nginx/xwiki_error.log error;
  access_log /var/log/nginx/xwiki_access.log combined;

  location / {
    proxy_pass         http://127.0.0.1:8080;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   Host      $host;
    proxy_http_version 1.1;
    proxy_set_header   Upgrade $http_upgrade;
    proxy_set_header   Connection 'upgrade';
    proxy_cache_bypass $http_upgrade;
    proxy_set_header   X-Forwarded-Host $http_host;
    proxy_set_header   X-Forwarded-Server $http_host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
  }
}
```

由于XWiki通过Http的Header来生成自身的一些路径，经过反向代理后丢失必要的Header就导致转跳错误，尤其是使用非标准端口时。

> 注意`X-Forwarded-Host`使用`$http_host`而不是`$host`，否则会丢失端口信息，传入`X-Forwarded-Proto`告知服务的协议


## 安装OIDC扩展并进行配置

安装OpenID Connect Authenticator扩展，文档地址如下

https://extensions.xwiki.org/xwiki/bin/view/Extension/OpenID%20Connect/OpenID%20Connect%20Authenticator/

编辑`xwiki.cfg`文件修改以下三个变量

```conf
#-# Host and Protocol
xwiki.home=https://example.com:8443/
xwiki.url.protocol=https
#-# OIDC authentication management class
xwiki.authentication.authclass=org.xwiki.contrib.oidc.auth.OIDCAuthServiceImpl
```

> `xwiki.home`和`xwiki.url.protocol`也是为了XWiki能够获取到正确自身的路径，感觉XWiki代码也不同，有的是通过Header，有的地方通过配置文件来获取Host地址，所以最好两个地方都配置好。`xwiki.authentication.authclass`指定认证类为OpenID Connect Authenticator扩展的认证类名。

编辑`xwiki.properties`添加以下配置

```conf
oidc.skipped=false
oidc.clientid=xwiki
oidc.secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
oidc.endpoint.authorization=https://auth.example.com/api/oidc/authorization
oidc.endpoint.token=https://auth.example.com/api/oidc/token
oidc.endpoint.userinfo=https://auth.example.com/api/oidc/userinfo
# oidc.endpoint.logout=
oidc.scope=openid,profile,groups,email
oidc.user.nameFormater=${oidc.user.preferredUsername._clean}
oidc.user.subjectFormater=${oidc.user.preferredUsername._clean}
```

> `oidc.user.subjectFormater`需要设置为OIDC服务返回`preferred_username`，默认为`sub`，是UUID格式，不便于区分。通过用户名来关联之前存在的用户，否则通过OIDC登陆后的用户会创建为`username-0`这样的用户。


为了实现关联之前存在的用户还需要编辑原有用户的Object。首先需要先编辑`xwiki.cfg`文件中的`xwiki.superadminpassword`来配置superadmin的密码，重启xwiki生效，然后使用superadmin登陆系统使用对象编辑器来编辑用户。
如下图将Subject设置为OIDC服务中身份对应的`preferred_username`，Issuer设置为OIDC服务的地址。

![](\assets\images\post\截屏2023-03-14 11.29.26.png)

## 其他

XWiki目前只支持单一方式认证，使用了OIDC认证就不能使用内部的认证或者其他外部认证。
不过OpenID Connect Authenticator扩展有个骚操作可以跳过OIDC认证使用内部认证以便登陆超级用户等内部账号或者用来调试，在URl添加`oidc.skipped=true`参数即可。
如`https://example.com:8443/bin/view/Main/?oidc.skipped=true`


