---
layout: post
title: "neo4j性能测试"
date: 2019-12-05 21:11:33
categories: 技术
tags: neo4j 性能测试
---

## 环境

### 服务器配置

* CUP: Intel(R) Core(TM) i7-4770 CPU @ 3.40GHz (4核8线程)
* 内存：32GB
* 磁盘：1TB HDD
* neo4j：3.5.2

### 数据结构

根据实际业务需求设计的graph模型，展示了部分模块

![](\assets\images\post\2019-12.06_neo4j-test-model.jpg)

### 预计数据规模

| 节点或关系 | 数量 |
|  ----  | ----  |
| TestAgency | 2000 |
| TestAgent | 5w |
| TestOnlineUser | 1000w |
| TestOnlineUserChild | 1300w |
| TEST_WORK_AT | 5w |
| TEST_GET | 500w |
| TEST_CHILD | 1300w |

### 数据插入脚本

插入脚本使用python编写，数据通过faker包自动生成，节点间的关系也随机生成，使用8个进程同时执行。后续测试的时间统计是涵盖python程序执行时间的。

插入方式使用原生cypher语句，插入时使用MERGE语法防止节点或关系重复，`MERGE`其实会进行查询后在根据ON来执行相应的`CREATE`和`MATCH`，所以为建立索引在本测试中会影响插入效率。

本测试中cypher插入语句示例：

```sql
MERGE (n:TestAgent{ node_id: 1 }})
ON CREATE SET n = $x
ON MATCH SET n += $x
```

### 索引

```text
Indexes
    ON :TestAgent(node_id) ONLINE
    ON :TestOnlineUser(platform) ONLINE
    ON :TestOnlineUser(platform, unionid) ONLINE
    ON :TestOnlineUserChild(appid, openid) ONLINE
```

当为ONLINE是表示索引已经就绪，POPULATING表示正在生成索引，索引生成还是比较快的，1000w数据，两个字段联合索引生成也就不到1分钟。

## 插入测试（MERGE方式）

| 数据量 | 插入量(无索引) | 耗时(无索引) | 平均耗时(无索引) | 插入量(有索引) | 耗时(有索引) | 平均耗时(有索引) |
|  ----  | ----  |  ----  |  ----  |  ----  |  ----  |  ----  |
| 0节点0关系 | 23w节点13w关系 | 2:38:58.73 | 26.5ms | -- | -- | -- |
| 110w节点62w关系 | 2280节点1280关系 | 0:11:15.97 | 189.6ms | 22680节点12680关系 | 0:7:09.77 | 12.13ms |
| 2300w节点1300w关系 | 19节点9关系 | 0:4:52.98 | 1039ms | 2323节点1323关系 | 0:0:22.642 | 6.2ms |

## 查询测试

| 数据量 | 查询方式 | 查询耗时(无索引) | 查询耗时(有索引) |
| ---- | ---- | ---- | ---- |
| 110w节点62w关系 | `MATCH (n:TestOnlineUser{platform: "xxx", unionid:"xxx"}) return n` | 837ms | 14ms |
| 1000w节点 | `MATCH (n:TestOnlineUser{platform: "xxx", unionid:"xxx"}) return n` | 17060ms | 1ms |
| 1000w节点 | `MATCH (u:TestOnlineUser{platform: 'xxx'}) return count(u)` | 12843ms | 1059 ms |
| 1005w节点500w关系 | `MATCH p=(a:TestAgent{node_id: x})-[r:TEST_GET]->(u:TestOnlineUser{platform: 'xxx'}) RETURN p` | 52ms | 3ms |
| 1005w节点500w关系 | `MATCH p=(a:TestAgent{node_id: x})-[r:TEST_GET{gender: 1}]->(u:TestOnlineUser) RETURN p` | 28ms | 3ms |

> 第一条查询的14ms可能是因为当时脚本在进行插入操作, 当时负载较高，后续的查询是机器空闲进行的。

## 总结

建立索引是非常必要的，对查询效率提升很大，不光是速度的提升，而且减少了资源占用。
数据量较大时8个进程同时查询服务端cpu占用经常在600%多，最多打满了800%，而建立索引后，同样8个进程同时查询cpu占用只有不到100%。

关于关系上属性的索引，官方文档没有介绍，网上也没有查到类似资料，关系上的属性建立索引的意义也不大，因为在实际查询的时候都是根据节点来找关系的，
直接查询关系一般也就上统计一下关系的总数。

另外neo4j支持全文检索，包括关系（relationship）上的属性

关于索引的官方文档链接地址：
(https://neo4j.com/docs/cypher-manual/current/schema/index/)[https://neo4j.com/docs/cypher-manual/current/schema/index/]
