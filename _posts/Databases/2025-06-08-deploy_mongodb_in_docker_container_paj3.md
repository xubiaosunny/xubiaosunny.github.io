---
layout: post
title: "Docker容器部署MongoDB(副本集)"
date: 2025-06-08 09:45:26 +0800
categories: 技术
tags: MongoDB
---

本文记录一下使用docker部署MongoDB的过程，本文使用mongo 7.0，搭建两个副本集节点。本文示例用户为`root`，密码为`123456`，地址为`mongo.example.com`，请注意替换。


## 最终目录结构

```
├── docker-compose.yml
├── mongo1
│   ├── configdb
│   └── db
├── mongo2
│   ├── configdb
│   └── db
└── mongodb-replica-keyfile
```

## 目录和权限

```bash
# mongo1和mongo2分别为两个节点的数据映射目录
chmod 777 -R ./mongo1
chmod 777 -R ./mongo2

# mongo5.0以上副本集需要keyFile
openssl rand -base64 756 > mongodb-replica-keyfile
chmod 400 mongodb-replica-keyfile
sudo chown 998:996 mongodb-replica-keyfile
```

如果不指定keyFile或者权限(组)不正确会报错误`BadValue: security.keyFile is required when authorization is enabled with replica sets`

容器中用户(mongod)ID是998，用户组(mongod)ID是996。keyFile的用户和用户组为`mongod:mongod`。

## 部署和初始化

### 编写docker-compose.yml

如果想增加节点，复制服务同时改变一下映射端口和目录即可

```yaml
services:
  mongo1:
    image: mongodb/mongodb-community-server:7.0-ubi8
    container_name: mongo1
    command: --replSet rs0 --keyFile /etc/mongo/keyfile
    ports:
      - 27017:27017
    volumes:
      - ./mongodb-replica-keyfile:/etc/mongo/keyfile:ro
      - ./mongo1/configdb:/data/configdb
      - ./mongo1/db:/data/db
    environment:
      MONGODB_INITDB_REPLICA_SET_NAME: "rs0"
      MONGODB_INITDB_ROOT_USERNAME: "root"
      MONGODB_INITDB_ROOT_PASSWORD: "123456"
  
  mongo2:
    image: mongodb/mongodb-community-server:7.0-ubi8
    container_name: mongo2
    command: --replSet rs0 --keyFile /etc/mongo/keyfile
    ports:
      - 27018:27017
    volumes:
      - ./mongodb-replica-keyfile:/etc/mongo/keyfile:ro
      - ./mongo2/configdb:/data/configdb
      - ./mongo2/db:/data/db
    environment:
      MONGODB_INITDB_REPLICA_SET_NAME: "rs0"
      MONGODB_INITDB_ROOT_USERNAME: "root"
      MONGODB_INITDB_ROOT_PASSWORD: "123456"
```

### 启动

```bash
docker-compose up -d
```

### 初始化副本集

```bash
# 连接MongoDB
mongosh "mongodb://root:123456@mongo.example.com:27017,mongo.example.com:27018/admin?authSource=admin&replicaSet=rs0"
# mongosh中执行
> rs.initiate({_id: "rs0", members: [{ _id: 0, host: "mongo.example.com:27017" },{ _id: 1, host: "mongo.example.com:27018" }]})
```

## 附：常用命令

```sh
# 唯一索引
db.members.createIndex( { "user_id": 1 }, { unique: true } )
# 创建用户
db.createUser({ user: "testuser", pwd: "userpasswd", roles: [{ role: "dbOwner", db: "testdb" }] })
```
