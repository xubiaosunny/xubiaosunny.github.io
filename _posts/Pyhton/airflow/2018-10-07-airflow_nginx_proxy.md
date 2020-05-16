---
layout: post
title: "Nginx同一域名下代理airflow与flower"
date: 2018-10-07 22:03:50 +0800
categories: 技术
tags: Nginx airflow flower
---

airflow的webserver默认监听为8080端口，若使用Celery执行任务，一般也会开启flower来监控Celery任务，而flower默认监听端口为5555。这样的话每次还得输入端口号来访问这两个服务，很不方便。我就想能不能将两个服务使用nginx代理到同一端口（80或者的433），而通过路由`/airflow`和`/flower`分别来访问。

在文档里查了一下，果不其然`airflow`的作者也想到了这个问题：[https://airflow.apache.org/integration.html](https://airflow.apache.org/integration.html)

以我的域名为例`www.xubiaosunny.online`

### 修改配置文件`airflow.cfg`

```
base_url = https://www.xubiaosunny.online/airflow

flower_url_prefix = /flower
```


### Nginx添加配置

```
location /airflow/ {
    proxy_pass http://localhost:8080;
    proxy_set_header Host $host;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

location /flower/ {
    rewrite ^/myorg/flower/(.*)$ /$1 break;  # remove prefix from http header
    proxy_pass http://localhost:5555;
    proxy_set_header Host $host;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

这样配置完，就可以通过`https://www.xubiaosunny.online/airflow/`和`https://www.xubiaosunny.online/airflow/`来访问airflow和flower了。

默认airflow是监听广播地址`0.0.0.0`，我们现在还可以通过8080和5555端口来访问。可以改为`127.0.0.1`来限制。修改配置文件

```
web_server_host = localhost

flower_host = localhost
```

到这其实我觉得还有一个问题，就是如果使用`airflow flower`来启动flower的话默认没有认真，不太安全。而且airflow配置文件内也没有这个配置。`flower`可以使用自己的命令启动

文档地址： [https://flower.readthedocs.io/en/latest/auth.html](https://flower.readthedocs.io/en/latest/auth.html)

```shell
celery flower --url_prefix=/flower --basic_auth=user1:password1,user2:password2
```
