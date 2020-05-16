---
layout: post
title: "mysql更改data目录"
date: 2018-07-25 11:29:02 +0800
categories: 技术
tags: mysql
---

由于数据库比较大，要将mysql的data目录从系统盘移到数据盘。之前也干过这个活，但每次都得上网查一下，还会遇到一些过时的教程，很浪费时间，本次就记录一下，方便以后查找。我这里的环境是Ubuntu16.04和mysql5.7。

## 移动mysql数据目录

```shell
mv /var/lib/mysql /data/
```

可以使用如下命令查看`datadir`路径

```shell
mysqladmin -u root -p variables | grep datadir
```

移动后目录所属用户和用户组应该还是`mysql`，如果不是修改用户和用户组:

```shell
chown -R mysql:mysql /data/mysql
```

如果权限不足修改权限:

```shell
chmod 777 -R /data/mysql
```

## 修改配置文件

修改mysql配置文件`/etc/mysql/mysql.conf.d/mysqld.cnf`

```
datadir         = /data/mysql
```

## 修改apparmor服务配置

做完以上操作理论上就移动完成了，但是我这却不能启动mysql。试了各种加权限页也不好使，后来在[https://www.jianshu.com/p/5fb55e313f8c](https://www.jianshu.com/p/5fb55e313f8c)找到了问题所在。

修改`/etc/apparmor.d/usr.sbin.mysqld`

```
# Allow plugin access
  /data/mysql/plugin/ r,
  /data/mysql/plugin/*.so* mr,

# Allow data dir access
  /data/mysql/ r,
  /data/mysql/** rwk,
```

## 重启mysql服务

```shell
service mysql start
```