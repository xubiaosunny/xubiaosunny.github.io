---
layout: post
title: "Shiny Server实现用户独立的 Shiny 应用环境"
date: 2024-06-05 17:33:21 +0800
categories: 技术
tags: R Shiny RStudio
---

## 背景

Shiny Server是默认的配置如下，内容很明了，指明了运行的用户为shiny，端口，以及应用和日志的目录。

```conf
# Instruct Shiny Server to run applications as the user "shiny"
run_as shiny;

# Define a server that listens on port 3838
server {
  listen 3838;
  
  # Define a location at the base URL
  location / {

    # Host the directory of Shiny Apps stored in this directory
    site_dir /srv/shiny-server;

    # Log all Shiny output to files in this directory
    log_dir /var/log/shiny-server;

    # When a user visits the base URL rather than a particular application,
    # an index of the applications available in this directory will be shown.
    directory_index on;
  }
}
```

这种配置下发布shiny应用的时候只需将应用复制到固定位置下 `/srv/shiny-server`即可。一直这么用着到也没有什么问题，直到遇到有包需要写文件到应用目录下。报如下错误。

```
Error in (function (file = if (onefile) "Rplots.pdf" else "Rplot%03d.pdf",  :
  cannot open file 'Rplots.pdf'
Calls: runApp ... eval -> eval -> ..stacktraceon.. -> par -> <Anonymous>
Execution halted
```

原因就是shiny运行用户为shiny，但`/srv/shiny-server`下的目录为其他用户，没有权限。详见下面链接

<https://stackoverflow.com/questions/68578200/r-shiny-app-fails-to-start-on-server-due-to-error-about-rplots-pdf>

在这种情况下，解决有两种方式：

* 将有权限问题的应用目录设置为shiny用户：`chown -R shiny:shiny test-shiny-app` 。


* 修改Shiny Server的部署方式，shiny应用不放在同一的位置，用户在home目录独立部署 Shiny应用。

第一种方式有弊端，就是多用户的时候每次用户部署后都需要root用户查询设置目录的用户，当然可以开发一个系统来发布shiny应用，这样的话又额外引入了工作量。这里介绍一下第二种方法，单独设置用户的发布目录。

## 实现用户的独立**Shiny 应用环境**

> 下面示例使用用户名为pve，用户组为shinyusers，shiny应用为test-shiny

参考官方文档：<https://docs.posit.co/shiny-server/>

### 修改Shiny Server部署方式


1. 添加shinyusers用户组，用户限制可以发布应用在home目录的用户

   ```bash
   groupadd shinyusers
   ```


2. 将需要发布应用的用户添加到shinyusers用户组

   ```bash
   usermod -aG shinyusers pve
   ```
3. 修改配置文件

   修改`/etc/shiny-server/shiny-server.conf`文件为如下内容

   ```conf
   # Instruct Shiny Server to run applications as the user "shiny"
   run_as shiny;
   
   # Define a server that listens on port 3838
   server {
     listen 3838;
   
     location /users {
       run_as :HOME_USER:;
       user_dirs;
       directory_index on;
       members_of shinyusers;
     }
     
     # Define a location at the base URL
     location / {
   
       # Host the directory of Shiny Apps stored in this directory
       site_dir /srv/shiny-server;
   
       # Log all Shiny output to files in this directory
       log_dir /var/log/shiny-server;
   
       # When a user visits the base URL rather than a particular application,
       # an index of the applications available in this directory will be shown.
       directory_index on;
     }
   }
   ```

   配置主要添加了`/users` 路径。`run_as :HOME_USER:;`用`:HOME_USER:`占位符来表示用户的主目录。`members_of shinyusers;`限制用户组为`shinyusers`。
4. 重启Shiny Server

   ```bash
   systemctl restart shiny-server
   ```

### 用户部署Shiny应用

这时就不必将shiny应用拷贝到固定的位置了，只需要拷贝到Home目录下的`ShinyApps`文件夹下即可。没有`ShinyApps`文件夹就自己创建一个。

 ![](/assets/images/post/截屏2024-06-05 16.57.39.png)

然后在浏览器上访问路径也有变化，我的例子的路径为`/users/pve/test-shiny/`，路径规则为`/users/<username>/<shiny-app-name>/`.

 ![](/assets/images/post/截屏2024-06-05 17.01.08.jpg)

## 我的的展望

对于Rstudio和Shiny这一套私有化部署的方式其实还是不太友好，其严重依赖linux账户体系，不能做到账户的打通，还有些权限限制，shiny应用的话每个也都需要单独添加认证。
我这里有个想法，Rstudio这边可以直接接OIDC认证，然后Shiny这边再开发一套系统将shiny包一层做个网关，当然认证体系也使用OIDC认证，主要功能就是提供发布应用的功能，然后做所有应用的代理以及访问权限的控制。以后有时间可以搞搞。
