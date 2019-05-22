---
layout: post
title: "使用Docker运行整套项目组件"
date: 2019-05-21 14:27:33
categories: 技术
tags: Docker docker-compose Django Celery
---

对于docker其实没有系统的学习过，之前在蓝汛工作的时候就被安排做docker镜像，当时临时上手，直接进入container然后跟操作linux一样把环境部署好之后像git一样commit到镜像，然后push到我们的私有repository里面，用的时候就直接`docker pull`，然后run。

其实这样不太好，因为每次修改什么都得不到体现，后来开始写Dockerfile。当时的思想是直接把所有的服务当打包到一个image里面，这也不是最佳的打开方式。所以今天在这里我用比较推荐的方式来示范一下。

## 整套系统组成

`Django`(2.2) + `pipenv` + `mysql`(8.0) + `celery`(4.3) + `rabbitmq`(3.7)

## Dockerfile

```dockerfile
FROM python:3.7
RUN mkdir /code

ADD . /code
WORKDIR /code

RUN apt-get update && apt-get install -y ffmpeg gettext

RUN pip3 install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
```

因为项目中用到了`ffmpeg`所以需要安装，还有国际化需要的`gettext`。

因为`python:3.7`镜像使用的是`buildpack-deps:stretch`，也就是debian9，直接使用apt就可以安装所需软件。但是国外的debian源有点慢，于是在试着如下改为阿里的源（清华的源是https了，有问题，`apt-transport-https`也装不上），但是不好使，估计`buildpack-deps:stretch`跟`debian:stretch`是有差别的。想用国内源还可以用其他方案，就是直接使用`debian:stretch`然后自己装python3.7。我就不试了，已经顶着网速build完了。。。

```dockerfile
# 如下可修改debian9的阿里源
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
   echo "deb http://mirrors.aliyun.com/debian/ stretch main non-free contrib" >/etc/apt/sources.list && \
   echo "deb-src http://mirrors.aliyun.com/debian/ stretch main non-free contrib" >/etc/apt/sources.list && \
   echo "deb http://mirrors.aliyun.com/debian-security stretch/updates main" >>/etc/apt/sources.list && \
   echo "deb-src http://mirrors.aliyun.com/debian-security stretch/updates main" >>/etc/apt/sources.list && \
   echo "deb http://mirrors.aliyun.com/debian/ stretch-updates main non-free contrib" >>/etc/apt/sources.list && \
   echo "deb-src http://mirrors.aliyun.com/debian/ stretch-updates main non-free contrib" >>/etc/apt/sources.list && \
   echo "deb http://mirrors.aliyun.com/debian/ stretch-backports main non-free contrib" >>/etc/apt/sources.list && \
   echo "deb-src http://mirrors.aliyun.com/debian/ stretch-backports main non-free contrib" >>/etc/apt/sources.list
```

因为我使用的的是`pipenv`来管理python包，所以安装时很方便，如果安装慢也可以使用国内pypi源

```dockerfile
RUN pip3 install pipenv -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pipenv install --system --deploy --ignore-pipfile -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## docker-compose.yml

```yml
version: '3'
services:
  db:
    image: mysql
    command: --default-authentication-plugin=mysql_native_password  # mysql8默认的认证mysqlclinet不能链接，改为mysql_native_password
    restart: always
    environment:
      MYSQL_DATABASE: yasuo  # 默认创建数据库
      MYSQL_ROOT_PASSWORD: yasuo # root密码
  rabbit:
    image: rabbitmq:3
    restart: always
  web:
    build: .
    image: yasuo_web  # build镜像名
    command: python3 manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    volumes:
      - .:/code
    depends_on:
      - db
      - rabbit
  celery:
    image: yasuo_web # 启动celery与web使用同一镜像，但分为两个container
    command: celery -A yasuo worker -l info
    volumes:
      - .:/code
    depends_on:
      - db
      - rabbit
```

## django配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db',
        'PORT': '3306',
        'NAME': 'yasuo',
        'USER': 'root',
        'PASSWORD': 'yasuo',
    }
}
```

因为mysql和django不在一个container，所以mysql的host不能配置为127.0.0.1，直接写`db`就可以，因为在web的container中`db`已经映射了其私网地址（网桥docker0），具体如何映射的我还不清楚，本来以为是在hosts文件中，但我查看了没有，在研究研究。

同样配置rabbitmq也不需要写明IP地址，直接写rabbit就可以

## 启动

```bash
docker-compose up
```

系统运行起来会有4个container

```bash
docker ps -a
```

![](\assets\images\post\屏幕快照 2019-05-21 下午5.38.19.png)

## 执行其他命令

Django会经常进行数据库迁移和国际化文件编译，可以这样做

```bash
docker-compose run web python3 manage.py migrate
docker-compose run web python3 manage.py compilemessages
```

还有一种做法就是封装到CMD中，写个run_web.sh

```sh
python3 manage.py migrate
python3 manage.py compilemessages
python3 manage.py runserver 0.0.0.0:8000
```

然后docker-compose.yml中

```yml
...
web:
    ...
    command: ./run_web.sh
    ...
...
```

## 生产环境

前面都是安装测试环境部署所写的，我们在生产环境不能使用runserver来跑，可以将CMD改为uwsgi启动命令。然后在本机上配置nginx代理

## 总结

环境的部署有时候特别烦人，有docker的话部署起来就很方便了，当然docker不限于此，也可以用于环境隔离、弹性计算等等。对于多组件的系统最好不要都放到一个container中，而是要分别起container。
