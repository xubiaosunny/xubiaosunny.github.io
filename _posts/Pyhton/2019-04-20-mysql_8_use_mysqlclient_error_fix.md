---
layout: post
title: "mysql8使用mysqlclient报错解决"
date: 2019-04-20 10:02:03
categories: 技术
tags: mysql Django python
---

在公司的时候搭建的项目正常运行，但回家后clone代码后安装依赖包后总报错：

```
django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module.
Did you install mysqlclient?
```

what? 然后我卸载安装了两遍还是不行，安装也没有报错。公司跟家里的系统都是macOS10.14.3，python包也都是通过pipenv安装的版本都是一样的，唯一不同的是mysq版本，家里的是8.0.12而公司是5.7。
那么只可能是mysql版本导致的，于是上网查找原因，首先找到一个是因为mysql8的用户认证加密方式不同导致连不上数据库，这应该跟我的情况不同，因为看报错明显是因为找不到`mysqlclinet`包，
但还是得试一试，而且既然有这原因，肯定后面也会遇到。

```sql
-- 由caching_sha2_password加密方式改为mysql_native_password
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'newpassword';  
FLUSH PRIVILEGES;
```

果然还是不好使，后来找到[mysqlclient的github页面](https://github.com/PyMySQL/mysqlclient-python)按照其为macOS安装了`mysql-connector-c`也不好使，并且查看了`mysql_congfig`也没有其提到的问题。

后来只好自己查看了报错位置的代码：

```python
try:
    import MySQLdb as Database
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient?'
    ) from err
```

我自己debug了这段代码发现在导入的时候报缺少了某个`.so`，正好我又查到了一条相关问题。链接地址如下

[https://stackoverflow.com/questions/46902357/error-loading-mysqldb-module-did-you-install-mysqlclient-or-mysql-python/53589824](https://stackoverflow.com/questions/46902357/error-loading-mysqldb-module-did-you-install-mysqlclient-or-mysql-python/53589824)

不是那条改用`pymysql`的回复，不过改用`pymsql`应该也好使，我也记录一下：

```python
# 安装pymysql，在setting.py同级目录的__init__.py里加入以下两行代码

import pymysql
pymysql.install_as_MySQLdb()
```

对我有用的是这条回复：

> I had this issue just recently even with using the python 3 compatible mysqlclient library and managed to solve my issue albeit in a bit of an unorthodox manner. If you are using MySQL 8, give this a try and see if it helps! :)
I simply made a copy of the libmysqlclient.21.dylib file located in my up-to-date installation of MySQL 8.0.13 which is was in /usr/local/mysql/lib and moved that copy under the same name to /usr/lib.
You will need to temporarily disable security integrity protection on your mac however to do this since you won't have or be able to change permissions to anything in /usr/lib without disabling it. You can do this by booting up into the recovery system, click Utilities on the menu at the top, and open up the terminal and enter csrutil disable into the terminal. Just remember to turn security integrity protection back on when you're done doing this! The only difference from the above process will be that you run csrutil enable instead.
You can find out more about how to disable and enable macOS's security integrity protection here.

回复中说启用mac的csrutil，然后把/usr/local/mysql/lib中的libmysqlclient.21.dylib拷贝到/usr/lib中。其实不用这么干，直接软连过去就可以

```bash
sudo ln -s /usr/local/mysql/lib/libmysqlclient.21.dylib /usr/lib/libmysqlclient.21.dylib
```

再运行django就没有报错了

### 2019.12.1更新

升级macOS Catalina后，`/usr/lib`变为只读，禁用SIP也不好使，可以将其软连到`/usr/local/lib`目录下

```bash
sudo ln -s /usr/local/mysql/lib/libmysqlclient.21.dylib /usr/local/lib/libmysqlclient.21.dylib
```
