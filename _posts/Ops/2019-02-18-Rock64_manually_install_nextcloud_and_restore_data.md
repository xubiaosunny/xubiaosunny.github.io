---
layout: post
title: "rock64手动安装nextcloud并恢复数据"
date: 2019-02-18 14:37:00 +0800
categories: 折腾
tags: rock64 nextcloud linux samba
---

去年闲鱼入了一个`rock64 1GB版`，刷了OMV的镜像，又安装了`nextcloud`做私有云来备份手机和pad上的照片、视频等。但后来就隔三差五就宕机，查系统日志也查不出原因，有时候系统会打印一些php什么failed的信息，我怀疑可能是php引起的系统崩溃，毕竟`openmediavault`和`nextcloud`都是php写的，而且`openmediavault`环境自带，我又安装了`nextcloud`会不会有什么冲突？我也不确定是不是软件引起的，或者可能硬件本身问题，毕竟闲鱼入的。最近实在忍受不了每次宕机，趁周末重装一下。

OMV系统是基于debian9的，这次索性不用debian了，也不刷应用定制的系统（MOV、nextcloudpi），直接烧了ubuntu镜像，然后需要什么再自己安装。

## 备份数据

由于我想要重装nextcloud但又不想丢失之前的数据，所以需先备份一下

```shell
# 备份数据库
sudo mysqldump --databases nextcloud >/data/backup/nextcloud.sql

# 备份nextcloud配置文件
sudo cp /var/www/nextcloud/config/config.php /data/backup/
```

nextcloud在这种arm板上其实用sqlite，可以少占用些资源，但多用户同时操作是会锁表（sqlite是表级锁）影响体验。

备份了数据库后还需备份nextcloud的data文件夹，由于我将data文件夹软链到了外置硬盘上，数据倒在外置硬盘所以不用再备份了。

## 烧录系统

很简单使用[Etcher](https://www.balena.io/etcher/)选择镜像文件和目标sd卡，然后等待烧录完成即可。

镜像下载地址：

https://github.com/ayufan-rock64/linux-build/releases/

bionic是ubuntu18.04，stretch为debian9。我用的bionic-minimal-rock64-0.7.11-1075-arm64.img.xz

## 安装系统更新

首先先修改apt源（国外源速度太慢）

打开`/etc/apt/sources.list`，将里面的`ports.ubuntu.com`全部改为`mirror.tuna.tsinghua.edu.cn`

```
deb http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic main restricted universe multiverse
deb-src http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic main restricted universe multiverse
deb http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-security main restricted universe multiverse
deb-src http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-security main restricted universe multiverse
deb http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-updates main restricted universe multiverse
deb-src http://mirror.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-updates main restricted universe multiverse

deb http://ppa.launchpad.net/ayufan/rock64-ppa/ubuntu bionic main
# deb-src http://ppa.launchpad.net/ayufan/rock64-ppa/ubuntu bionic main
```

清华大学镜像站：[https://mirror.tuna.tsinghua.edu.cn/](https://mirror.tuna.tsinghua.edu.cn/)，ubuntu-ports即为ubuntu arm源。

获取更新并升级到最新

```shell
sudo apt update
sudo apt upgrade
```

在更新或者安装软件包的时候会报如下错误

```
dpkg-deb (subprocess): decompressing archive member: lzma error: unexpected end of input
dpkg-deb: error: subprocess <decompress> returned error exit status 2！
```

只要使用`sudo apt install -f`安装依赖，然后在`upgrade`或者`install`即可。

## 挂载外置硬盘

查看外置硬盘的UUID

```bash
sudo blkid
```

![](\assets\images\post\屏幕快照 2019-02-18 下午4.59.40.png)

修改`/etc/fstab`开机自动挂载

```
UUID=987afc86-8f1b-4a4a-b6af-17d49160e2dd /data ext4 defaults 0 1
```

挂载硬盘

```
sudo mount -a
```

## 安装配置nextcloud并恢复数据

官方文档：

https://docs.nextcloud.com/server/15/admin_manual/installation/source_installation.html#example-installation-on-ubuntu-18-04-lts-server

安装nginx和mysql

```shell
apt install nginx
apt install mysql-server mysql-client
```

安装php相关包

```shell
apt-get install php7.2-gd php7.2-json php7.2-mysql php7.2-curl php7.2-mbstring
apt-get install php7.2-intl php-imagick php7.2-xml php7.2-zip
# fpm
apt isntall php7.2-fpm
```

下载nextcloud，如果是迁移，需下载与之前版本一致，否则可能出现问题，因为我之前已经将nextcloud升级问最新版，所以我这里下载的也是最新版（15.0.4）。

```shell
wget https://download.nextcloud.com/server/releases/nextcloud-15.0.4.zip

# 解压并移入/var/www/
unzip nextcloud-15.0.4.zip
sudo mv nextcloud /var/www/

# 软链外置硬盘data
sudo ln -s  /data/nextcloud/ /var/www/nextcloud/data

# 赋予nextcloud文件夹755权限
sudo chmod 755 -R /var/www/nextcloud/
```

恢复mysql备份

```bash
sudo mysql
# 为nextcloud创建数据库
> CREATE DATABASE `nextcloud` DEFAULT CHARACTER SET utf8 ;
# 创建mysql用户rock64，密码为123456
> CREATE USER 'rock64'@'%' IDENTIFIED BY '123456';
# 将数据库nextcloud所有权限分配给用户rock64
> GRANT ALL ON nextcloud.* TO 'rock64'@'%';

# 恢复数据
sudo mysql nextcloud < /data/backup/nextcloud.sql
```

配置fpm，新建文件`/etc/php/7.2/fpm/pool.d/nextcloud.conf`，写入以下配置

```
[nextcloud]
listen = /var/run/php/php7.2-fpm-nextcloud.sock
listen.owner = www-data
listen.group = www-data
listen.mode = 0600

user = www-data
group = www-data

; Process manager
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
pm.max_requests = 0

; php.ini
php_flag[display_errors] = Off
php_flag[html_errors] = On
php_value[max_execution_time] = 30
php_value[memory_limit] = 128M
php_value[post_max_size] = 8M
php_value[upload_max_filesize] = 2M
; extra options
clear_env = no
env[HOSTNAME] = $HOSTNAME
env[PATH] = /usr/local/bin:/usr/bin:/bin
env[TMP] = /tmp
env[TMPDIR] = /tmp
env[TEMP] = /tmp
```

重启fpm

```shell
service php7.2-fpm restart
```

将nextcloud配置文件拷贝到项目

```shell
sudo cp /data/backup/config.php /var/www/nextcloud/config/config.php
```

如果新环境配置有变化需修改对应配置，我这边数据库user变化，因为之前安装nextcloud是使用的`setup-nextcloud.php`在web页面安装的，它为我自动创建了名为oc_admin的用户。所以得修改一下配置

```
...
'dbuser' => 'rock64',
'dbpassword' => '123456',
...
```

配置nginx，官方文档：https://docs.nextcloud.com/server/15/admin_manual/installation/nginx.html

创建新配置文件`/etc/nginx/sites-enabled/nextcloud`，写入以下配置，将证书文件位置和server_name、监听端口改为自己的即可

```
upstream php-handler {
    #server 127.0.0.1:9000;
    server unix:/var/run/php/php7.2-fpm-nextcloud.sock;
}

server {
    listen 4443 ssl http2;
    listen [::]:4443 ssl http2;
    server_name your_domain;

    # Use Mozilla's guidelines for SSL/TLS settings
    # https://mozilla.github.io/server-side-tls/ssl-config-generator/
    # NOTE: some settings below might be redundant
    ssl_certificate /home/rock64/certbot-async/letsencrypt/cert.pem;
    ssl_certificate_key /home/rock64/certbot-async/letsencrypt/privkey.pem;

    # Add headers to serve security related headers
    # Before enabling Strict-Transport-Security headers please read into this
    # topic first.
    add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;";
    #
    # WARNING: Only add the preload option once you read about
    # the consequences in https://hstspreload.org/. This option
    # will add the domain to a hardcoded list that is shipped
    # in all major browsers and getting removed from this list
    # could take several months.
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Robots-Tag none;
    add_header X-Download-Options noopen;
    add_header X-Permitted-Cross-Domain-Policies none;
    add_header Referrer-Policy no-referrer;
    # Remove X-Powered-By, which is an information leak
    fastcgi_hide_header X-Powered-By;

    # Path to the root of your installation
    root /var/www/nextcloud/;

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    # The following 2 rules are only needed for the user_webfinger app.
    # Uncomment it if you're planning to use this app.
    #rewrite ^/.well-known/host-meta /public.php?service=host-meta last;
    #rewrite ^/.well-known/host-meta.json /public.php?service=host-meta-json last;

    # The following rule is only needed for the Social app.
    # Uncomment it if you're planning to use this app.
    # rewrite ^/.well-known/webfinger /public.php?service=webfinger last;

    location = /.well-known/carddav {
      return 301 /remote.php/dav;
    }
    location = /.well-known/caldav {
      return 301 /remote.php/dav;
    }

    # set max upload size
    client_max_body_size 512M;
    fastcgi_buffers 64 4K;

    # Enable gzip but do not remove ETag headers
    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    # Uncomment if your server is build with the ngx_pagespeed module
    # This module is currently not supported.
    #pagespeed off;

    location / {
        rewrite ^ /index.php$request_uri;
    }

    location ~ ^\/(?:build|tests|config|lib|3rdparty|templates|data)\/ {
        deny all;
    }
    location ~ ^\/(?:\.|autotest|occ|issue|indie|db_|console) {
        deny all;
    }

    location ~ ^\/(?:index|remote|public|cron|core\/ajax\/update|status|ocs\/v[12]|updater\/.+|ocs-provider\/.+)\.php(?:$|\/) {
        fastcgi_split_path_info ^(.+?\.php)(\/.*|)$;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param HTTPS on;
        #Avoid sending the security headers twice
        fastcgi_param modHeadersAvailable true;
        fastcgi_param front_controller_active true;
        fastcgi_pass php-handler;
        fastcgi_intercept_errors on;
        fastcgi_request_buffering off;
    }

    location ~ ^\/(?:updater|ocs-provider)(?:$|\/) {
        try_files $uri/ =404;
        index index.php;
    }

    # Adding the cache control header for js and css files
    # Make sure it is BELOW the PHP block
    location ~ \.(?:css|js|woff2?|svg|gif)$ {
        try_files $uri /index.php$request_uri;
        add_header Cache-Control "public, max-age=15778463";
        # Add headers to serve security related headers (It is intended to
        # have those duplicated to the ones above)
        # Before enabling Strict-Transport-Security headers please read into
        # this topic first.
        # add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;";
        #
        # WARNING: Only add the preload option once you read about
        # the consequences in https://hstspreload.org/. This option
        # will add the domain to a hardcoded list that is shipped
        # in all major browsers and getting removed from this list
        # could take several months.
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Robots-Tag none;
        add_header X-Download-Options noopen;
        add_header X-Permitted-Cross-Domain-Policies none;
        add_header Referrer-Policy no-referrer;

        # Optional: Don't log access to assets
        access_log off;
    }

    location ~ \.(?:png|html|ttf|ico|jpg|jpeg)$ {
        try_files $uri /index.php$request_uri;
        # Optional: Don't log access to other assets
        access_log off;
    }
}
```

重启nginx

```
service nginx restart
```

然后就可以在局域网访问访问nextcloud来管理文件了，nextcloud有各平台的app，可以配合使用。做了外网映射和ddns后，我们就可以在外网访问家里的nextcloud，实现了自己的私有云。这我就不多说了，本文主要介绍重装和恢复数据。

## 安装其他实用工具

由于怀疑可能OMV导致系统奔溃，而且OMV只是一个界面化的工具，作为一个程序员来说，命令行都可以来配置，且我只有一块硬盘也不做raid备份啥的，所以就没有安装OMV，安装常用工具即可。

### 安装samba局域网共享

```
sudo apt install samba
```

创建samba用户

```
sudo smbpasswd -a rock64
```

修改`/etc/samba/smb.conf`，在最后添加以下配置

```
[rock64]
    comment = samba home directory
    path = /data/samba
    public = yes
    browseable = yes
    public = yes
    read only = no
    valid users = rock64
    available = yes
```

重启samba服务

```
service smbd restart
```

### 安装youtube-dl、aria2等常用下载工具

安装youtube-dl

```
sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl
```

安装aria2

```
sudo apt install aria2
```

使用youtube-dl和aria2下载的时候我们可以使用`nohup`来后台下载，如

```
nobup aria2c https://download.nextcloud.com/server/releases/nextcloud-15.0.4.zip &
```
