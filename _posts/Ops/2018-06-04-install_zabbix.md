---
layout: post
title: "Zabbix 安装"
date: 2018-06-10 00:16:31
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

导入数据

```shell
cd /usr/share/doc/zabbix-server-mysql
zcat create.sql.gz | mysql -uroot zabbix
```

如果使用postgresql，则安装`zabbix-server-pgsql`，导入数据：

```shell
cd /usr/share/doc/zabbix-server-pgsql/
zcat create.sql.gz | sudo -u <username> psql zabbix
```

## zabbix agent安装

```shell
apt install zabbix-agent
```

配置zabbix-agent

```
Server=<zabbix server ip>
ServerActive=<zabbix server ip>
Hostname=<your host name>
```
