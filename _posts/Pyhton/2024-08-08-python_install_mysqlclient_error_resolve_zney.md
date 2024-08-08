---
layout: post
title: "Python安装mysqlclient包报错解决"
date: 2024-08-08 16:40:49 +0800
categories: 技术
tags: python
---

## MacOS上问题解决

> 之前安装其实没有这么麻烦，用brew安装依赖会比MacPorts好很多解决依赖方面。但是没办法老Mac版本brew不支持了，难受

mysqlclient 在v2.2.0后需要依赖`pkg-config`，所以在执行`pip`进行安装的时候一般都会报以下错误

```
Exception: Can not find valid pkg-config name.
Specify MYSQLCLIENT_CFLAGS and MYSQLCLIENT_LDFLAGS env vars manually
```

解决这个问题需要安装`pkg-config`

```bash
# brew
brew install pkg-config

# MacPorts
sudo port install pkgconfig
```

当然不光需要安装`pkg-config`，还需要安装`mysql-client`

```bash
# brew
brew install mysql-client

# MacPorts直接安装完整mysql，其中包含mysql
sudo port install mysql
```

到这里还是会报上面的错误，还需要`PKG_CONFIG_PATH`环境变量指明mysql的pkgconfig

```bash
export PKG_CONFIG_PATH="/usr/local/mysql/lib/pkgconfig"
```

最后再执行安装命令就顺利安装了

```bash
pip install mysqlclient
```

安装完后程序运行的时候可能还会报以下错误

```
Reason: tried: '/usr/lib/libmysqlclient.24.dylib' (no such file)
```

其实这个文件是存在的，所以我就想直接直接软连过去不就可以了

```bash
sudo ln -s /usr/local/mysql-8.4.2-macos14-x86_64/lib/libmysqlclient.24.dylib /usr/lib/libmysqlclient.24.dylib
```

结果却是是报没有权限，明明已经sudo执行了，MacOS的文件权限管理是越来越严格了

```
ln: /usr/lib/libmysqlclient.24.dylib: Operation not permitted
```

最后还是通过ChatGPT找到方法，添加`DYLD_LIBRARY_PATH`环境变量

```bash
export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/
```

这样代码就可以正常运行了

## 参考链接

* https://github.com/PyMySQL/mysqlclient/discussions/624
