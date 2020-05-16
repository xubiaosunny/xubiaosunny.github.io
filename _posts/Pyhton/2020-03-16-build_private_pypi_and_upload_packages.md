---
layout: post
title: "创建私有pypi仓库及上传python包"
date: 2020-03-16 20:41:30 +0800
categories: 技术
tags: python pypi
---

## 使用`pypiserver`搭建私有pypi仓库

### pip安装`pypiserver`

安装`pypiserver`

```bash
pip install pypiserver 
```

启动`pypiserver`服务，指定包存放路径为/data/packages

```
pypi-server -p 8080 /data/packages
```

#### 添加认证

使用htpasswd创建用户和修改密码

首先安装`passlib`

```bash
pip install passlib
```

创建htpasswd文件并创建一个用户(admin)，并按照提示输入密码

```
htpasswd -sc htpasswd.txt admin
```

在添加用户的时候要把参数`c`去掉，`c`指的是创建的意思，否则会重新创建文件覆盖之前的

```
htpasswd -s htpasswd.txt admin2
```

htpasswd文件内容是这样的

```text
admin:{SHA}fEqNCco3Yq9h5ZUglD3CZJT4lBs=
admin2:{SHA}fEqNCco3Yq9h5ZUglD3CZJT4lBs=
```

为`pypiserver`服务启用认证

```
pypi-server -p 8080 -P /data/htpasswd.txt /data/packages
```

> htpasswd详细用法请参考https://man.linuxde.net/htpasswd


### docker运行`pypiserver`

拉取`pypiserver`镜像

```bash
docker pull pypiserver/pypiserver
```

运行

```bash
docker run pypiserver/pypiserver
```

packages目录在/data/packages，将packages目录映射到宿主机

```bash
docker run -p 8080:8080 -v ~/packages:/data/packages pypiserver/pypiserver
```

添加认证也可以,映射htpasswd文件即可

```bash
docker run -p 8080:8080 -v /data/htpasswd.txt:/data/.htpasswd pypiserver/pypiserver -P .htpasswd
```

## 上传python包到pypi仓库

使用sdist命令创建源分发

```bash
python setup.py sdist
# 还可以指定压缩模式
# python setup.py sdist --formats=gztar,zip
```

### 直接将压缩后的包拷贝到packages目录

```
cp ./dist/my_package-1.0.tar.gz /data/packages
```

### 使用twine上传

安装`twine`

```
pip install twine
```

使用twine上传包，按提示输入用户名密码

```
twine upload --repository-url http://localhost:8080/ ./dist/my_package-1.0.tar.gz
```

还可以在~/.pypirc文件中配置源的用户名密码

```
[distutils]
index-servers =
  pypi
  local

[pypi]
username:<your_pypi_username>
password:<your_pypi_passwd>

[local]
repository: http://localhost:8080
username: admin
password: 123456
```

上传是直接使用local

```
twine upload -r local ./dist/my_package-1.0.tar.gz
```

> 对于官方pypi我们首先需要注册账号，上传包的操作和向私有仓库上传是一样的。

## 参考链接

* https://pypi.org/project/pypiserver/
* https://hub.docker.com/r/pypiserver/pypiserver
* https://www.cnblogs.com/mithrilon/p/8954677.html
* https://docs.python.org/3.8/distutils/sourcedist.html
* https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives

