---
layout: post
title: "Mongodb副本集与分片"
date: 2019-08-07 17:55:13
categories: 技术
tags: Mongodb
---

因为之前没用过mongo，所以最近的开发踩了不少坑，现在熟练了不少。

mongo在许多地方用起来还有许多不如意的地方，比如不知道如何加行锁，虽然mongo本身可以加写锁，
多写的时候保证原子性，但不能向mysql在事务中`select ... for update`这样加锁，
这样可以在应用代码中添加逻辑并且保证该对应行不被读取或修改。

还好的是Mongodb4.0是支持事务的（看网上貌似3.6就支持了，但得自己开启）。刚好前端时间有些业务需求需要用到事务来保证数据的准确性，因为一个动作内有多条出入和修改的操作，如果中途报错需要回滚。

> 连接mongo的shell后使用`db.version()`来查看mongodb的版本

## Python只用mongo事务

在python中使用使用`pymongo`来操作数据库

```python
import pymongo
mc = pymongo.MongoClient('mongodb://localhost:27018', connect=False, maxPoolSize=2000)
with mc.start_session() as session:
    with session.start_transaction():
        mc['test']['test'].insert_one({'a': 1}, session=session)
        mc['test']['test'].delete_one({'a': 1}, session=session)
        ...
```

但在实际使用中却报了个错

```text
MongoError: Transaction numbers are only allowed on a replica set member or mongos.
```

上网搜索后很多解决方法都是npm安装一个什么包，然后用它启动mongo。

其实根据英文的意思也差不多能明白是怎么回事，网上搜索后发现了根本原因：事务只支持副本集和切片。而我这开发环境是直接mongod启的

## 副本集

### 副本集搭建

启动两个mongodb服务(一个master，一个slave)

```bash
# 1
/usr/local/mongodb/mongodb4.0.10/bin/mongod \
--bind_ip=0.0.0.0 --port=27018
--logpath=/var/log/mongodb/mongodb_4_0_10.log \
--dbpath=/data/mongo_4.0.10_db \
--replSet rs0 --fork
# 2
/usr/local/mongodb/mongodb4.0.10/bin/mongod \
--bind_ip=0.0.0.0 --port=27019 \
--logpath=/var/log/mongodb/mongodb_4_0_10-2.log \
--dbpath=/data/mongo_4.0.10_db-2 \
--replSet rs0 --fork
```

在mongo shell中执行

```bash
# 启动一个新的副本集
rs.initiate()
# 添加一个副本集
rs.add("localhost.localdomain:27019")
```

这样的的话就可以使用mongodb的事务了
> 单节点也是支持事务的，我多加一个slave节点只是为了测试一下

### slave节点读

默认slave节点是不能读的，在Mongo客户端使用命令`db.setSlaveOk()`来开启slave节点读，

这样的可以读写分离（master写，slave读），关于slave读对副本集间的同步的影响我没有实践就不写了，网上有资料介绍。

### master选举

[http://www.mongoing.com/archives/295](http://www.mongoing.com/archives/295)

## 分片

分片集群我没有搭建，这里有个文章写的比较不错，分片加副本集搭建，这样既分流的数据也保证了数据的备份。等有时间自己搭建我在详细记录这里的坑

[http://www.fordba.com/mongo_share_rs.html](http://www.fordba.com/mongo_share_rs.html)
