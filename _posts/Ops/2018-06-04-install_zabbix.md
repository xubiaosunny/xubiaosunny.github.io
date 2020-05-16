---
layout: post
title: "Zabbix 安装"
date: 2018-06-10 00:16:31 +0800
categories: 技术
tags: zabbix
---
一个朋友刚培训出来找到一个工作，做运维开发。由于没有工作过所以上周末跑来我这让我指导一下。他接下来的任务大概是对接zabbix（听他的意思大概是他们这边做一套web接zabbix的数据，然后显示）。首先得搭建一套zabbix。

# zabbix安装
## zabbix server安装

我这里使用的是Ubuntu16.04，其他linux发行版下载对应的deb安装包安装即可。

```shell
wget http://repo.zabbix.com/zabbix/3.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_3.4-1+xenial_all.deb
dpkg -i zabbix-release_3.4-1+xenial_all.deb
```

使用mysql数据库安装Zabbix web

```shell
apt install zabbix-server-mysql zabbix-frontend-php
```

导入数据

```shell
cd /usr/share/doc/zabbix-server-mysql
zcat create.sql.gz | mysql -uroot zabbix
```

如果使用postgresql，则安装`zabbix-server-pgsql`，导入数据：

```shell
cd /usr/share/doc/zabbix-server-pgsql/
zcat create.sql.gz | sudo -u <username> psql zabbix
```

修改在zabbix server配置文件`/etc/zabbix/zabbix_server.conf`

```
DBHost=localhost
DBName=zabbix
DBUser=root
DBPassword=password
```

启动zabbix server

```shell
service zabbix_server start
```

修改zabbix-frontend-php apache配置文件`/etc/httpd/conf.d/zabbix.conf `

```
php_value date.timezone Asia/Shanghai
```

重启apache

```shell
service apache2 restart
```

访问`http://zabbix-frontend-hostname/zabbix`完成zabbix-frontend-php数据库配置

![](\assets\images\post\屏幕快照 2018-06-11 下午9.48.24.png)

现在可以通过http://zabbix-frontend-hostname/zabbix 进行访问。默认的用户名／密码为 Admin/zabbix。

## zabbix agent安装

```shell
apt install zabbix-agent
```

配置zabbix-agent, `/etc/zabbix/zabbix_agentd.conf`

```
Server=192.168.31.11
ServerActive=192.168.31.11
Hostname=<HOSTNAME>
```

重启zabbix-agent

```shell
service zabbix-agent restart
```

## 添加host

![](\assets\images\post\2018-06-13_00_25_06.JPG)
![](\assets\images\post\2018-06-13_00_27_06.JPG)
![](\assets\images\post\2018-06-13_00_29_06.JPG)
