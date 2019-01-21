---
layout: post
title: "Debian9设置区时和语言"
date: 2019-01-21 23:10:10
categories: 技术
tags: Debian
---

家里的跑着的`openmediavault`总会过几天就网路就断了，重插网线也不会连接，只能重启。于是就去查看系统日志，但也没发现什么原因。查看日志的时候却发现原来系统的时间不对，于是上网查了正确设置了时间，一并将`locale`的waring解决了。



## 设置区时

参考：[https://www.howtoing.com/how-to-set-up-time-synchronization-on-debian-9](https://www.howtoing.com/how-to-set-up-time-synchronization-on-debian-9)

列出可用区时

```
timedatectl list-timezones
```

设置区时（中国）

```
timedatectl set-timezone Asia/Shanghai
```

## 设置语言

网上很多说的，大部分不好使，结合[https://github.com/tianon/docker-brew-debian/issues/45](https://github.com/tianon/docker-brew-debian/issues/45) 成功设置。解决以下问题

1

```
locale: Cannot set LC_CTYPE to default locale: No such file or directory 
locale: Cannot set LC_MESSAGES to default locale: No such file or directory 
locale: Cannot set LC_COLLATE to default locale: No such file or directory
```

2

```
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
```

### 具体操作方法：

打开`/etc/locale.gen`，将 `en_US.UTF-8 UTF-8` 前面的注释去掉

然后在 `/etc/environment` 中添加

```
LANG="en_US.UTF-8"
LANGUAGE="en_US.UTF-8"
LC_ALL="en_US.UTF-8"
```

执行

```shell
locale-gen UTF-8
```

网上很多帖子都写着`locale-gen en_US.UTF-8`, 实测会报错。`locale-gen UTF-8` 成功

