---
layout: post
title: "nextcloud使用mysql8.0、添加redis缓存以及解决升级超时问题"
date: 2020-02-29 14:13:24 +0800
categories: 
tags: nextcloud mysql redis
---


## 切换到mysql8.0

nextcloud直接使用mysql8.0是运行不起来的，因为mysql8.0开始将caching_sha2_password作为默认的身份验证插件，
nextcloud现在是不支持caching_sha2_password认证的（由于php现在不支持）。
所以需要创建mysql_native_password认证的mysql用户来让nextcloud使用

```sql
-- 创建用户nextcloud，密码为password
CREATE USER 'nextcloud'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
-- 将nextcloud库的权限分配给用户nextcloud
GRANT ALL ON nextcloud.* TO 'nextcloud'@'%';
```

> 运行mysql8.0的时候使用命令`--default-authentication-plugin=mysql_native_password`启动也不好使，不知道为啥。
只有像上面这样新建mysql_native_password验证的用户才好使

## 添加redis作为缓存

在`config.php`添加缓存配置

```php
  'memcache.local' => '\\OC\\Memcache\\Redis',
  'memcache.locking' => '\\OC\\Memcache\\Redis',
  'filelocking.enabled' => 'true',
  'redis' =>
  array (
    'host' => '127.0.0.1',
    'port' => 6379,
    'dbindex' => 0,
    'timeout' => 1.5,
  ),
```

## 解决升级页面超时问题

在nextcloud页面点击升级的时候，经常会504超时，是请求超时了，再次点击升级的时候会返回如下信息

```text
Step 4 is currently in process. Please reload this page later.
```

原因其实是后台下载升级包慢导致的。

这时候我们需要手动删除nextcloud的data目录下的updater-*文件夹中的.step文件，然后就不要在页面上升级了，在命令行下使用以下命令进行升级

```bash
sudo -u www-data php /var/www/nextcloud/updater/updater.phar
sudo -u www-data php /var/www/nextcloud/occ upgrade
sudo -u www-data php /var/www/nextcloud/occ maintenance:mode --off
```

如果下载比较慢的话可以使用代理，有两种方式

* 修改`config.php`，添加`proxy`配置，如`'proxy' => 'http://127.0.0.1:1080'`。 
* 修改curl的代理， `alias curl="curl -x socks5h://127.0.0.1:1081"`或者`export ALL_PROXY=socks5h://127.0.0.1:1081`
