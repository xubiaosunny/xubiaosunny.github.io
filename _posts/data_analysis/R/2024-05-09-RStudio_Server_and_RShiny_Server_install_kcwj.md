---
layout: post
title: "RStudio Server和Shiny Server安装部署"
date: 2024-05-09 21:36:39 +0800
categories: 技术
tags: R Shiny RStudio Docker Fedora Debian
---

## 直接部署

我这里根据`RStudio Server`支持的系统选用了`Fedora36`，后来搭建完才发现也支持Debian12（我一直在用Debian系的Linux，对红帽系的用的少）。

### 安装R

可以参考posit官方文档：https://docs.posit.co/resources/install-r/

文档介绍可以按照指定的R环境，但是我测试了安装4.3.3，会报动态库的问题。为了不解决麻烦的依赖问题，我选择使用Fedora包管理工具直接来安装R（Fedora36对应的是4.1.3）。

```bash
dnf install R
```

### 安装RStudio Server

参考文档：https://posit.co/download/rstudio-server/

按照文档不在操作即可，因为我们前面已经安装了R，所以这里直接安装RStudio Server即可

```bash
wget https://download2.rstudio.org/server/rhel9/x86_64/rstudio-server-rhel-2024.04.0-735-x86_64.rpm
sudo yum install rstudio-server-rhel-2024.04.0-735-x86_64.rpm
```

### 安装 Shiny Server

参考文档：https://posit.co/download/shiny-server/

同样可以跳过R安装，只需要安装`shiny`包和shiny-server服务即可。

安装`shiny`包

```bash
sudo su - -c "R -e \"install.packages('shiny', repos='https://cran.rstudio.com/')\""
```

安装shiny-server

```bash
wget https://download3.rstudio.org/centos7/x86_64/shiny-server-1.5.22.1017-x86_64.rpm
sudo yum install --nogpgcheck shiny-server-1.5.22.1017-x86_64.rpm
```

### 防火墙

#### 开放端口

我这里直接开放了1025-65535所有端口，可以按需只开放8787和3838端口即可。

```bash
# 查看所以域
firewall-cmd --get-zones
# 查看默认域
firewall-cmd --get-default-zone
# 查看放行的服务
firewall-cmd --list-services
# 添加http服务
firewall-cmd --add-service=http
# 当前域中防火墙还开启的端口
firewall-cmd --list-ports --zone=FedoraServer
# 开放端口
firewall-cmd --add-port=1025-65535/tcp
firewall-cmd --add-port=1025-65535/udp
```

#### 关闭SELinux

修改 /etc/selinux/config，将SELINUX=enforcing改为SELINUX=disabled。然后重启系统。

```Properties
# SELINUX=enforcing
SELINUX=disabled
```

如果不关闭SELinux惠报以下错误

```
[rserver] ERROR system error 13 (Permission denied); OCCURRED AT rstudio::core::Error rstudio::core::system::launchChildProcess(std::string, std::string, rstudio::core::system::ProcessConfig, rstudio::core::system::ProcessConfigFilter, PidType*) src/cpp/core/system/PosixSystem.cpp:2234; LOGGED FROM: rstudio::core::Error rstudio::core::system::launchChildProcess(std::string, std::string, rstudio::core::system::ProcessConfig, rstudio::core::system::ProcessConfigFilter, PidType*) src/cpp/core/system/PosixSystem.cpp:2235
```

详见：https://forum.posit.co/t/rserver-1692-error-system-error-13-permission-denied/46972/10

> 报错`system error 13 (Permission denied)`还有一种情况是用户没有创建home目录，具体查看日志。

### 使用

#### RStudio Server

浏览器访问 `http://<your_ip>:8787`

账户认证使用linux系统PAM，可以使用`useradd`命令来创建用户。

```bash
useradd -m -s /bin/bash testuser
passwd testuser
```

#### Shiny Server

浏览器访问 `http://<your_ip>:3838`

默认将代码部署到`/srv/shiny-server`文件夹下即可

可以修改`/etc/shiny-server/shiny-server.conf`配置文件更改部署目录

```
...
site_dir /srv/shiny-server;
...
```

## Docker部署

docker方式我使用Debian12作为基础镜像，镜像构建过程其实就是在服务器直接安装的过程。

下面只给出了Dockerfile。具体构建镜像和运行容器就不赘述了。

### RStudio Server

Dockerfile

```Dockerfile
FROM debian:12

RUN sed -i 's@deb.debian.org@mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list.d/debian.sources
RUN apt update -y && apt install -y r-base gdebi-core wget
RUN wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2024.04.0-735-amd64.deb
RUN gdebi --non-interactive rstudio-server-2024.04.0-735-amd64.deb

ENTRYPOINT ["/usr/lib/rstudio-server/bin/rserver", "--server-daemonize=0"]
```

### Shiny Server

Dockerfile

```Dockerfile
FROM debian:12

RUN sed -i 's@deb.debian.org@mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list.d/debian.sources
RUN apt update -y && apt install -y r-base gdebi-core wget
RUN su - -c "R -e \"install.packages('shiny', repos='https://mirrors.tuna.tsinghua.edu.cn/CRAN/')\""
RUN su - -c "R -e \"install.packages('rmarkdown', repos='https://mirrors.tuna.tsinghua.edu.cn/CRAN/')\""
RUN wget https://download3.rstudio.org/ubuntu-18.04/x86_64/shiny-server-1.5.22.1017-amd64.deb
RUN gdebi --non-interactive shiny-server-1.5.22.1017-amd64.deb

ENTRYPOINT ["/opt/shiny-server/bin/shiny-server", "--verbose"]
```
