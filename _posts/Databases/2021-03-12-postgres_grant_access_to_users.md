---
layout: post
title: "Postgres用户权限授予"
date: 2021-03-12 15:52:55 +0800
categories: 技术
tags: PostgreSQL
---

每次做这些操作的时候总得再去网上搜索，今天总结一下方便以后使用


### 创建数据库指定拥有者

```sql
CREATE DATABASE database_name OWNER username;
```

### 授予用户数据库权限

```sql
GRANT CONNECT ON DATABASE database_name TO username;
```

### 授予用户SCHEMA权限

```sql
GRANT USAGE ON SCHEMA schema_name TO username;
```

### 授予用户表权限

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON table_name IN SCHEMA schema_name TO username;
```

### 修改表拥有者

```sql
ALTER TABLE table_name OWNER TO new_owner;
```

> 撤销用户权限使用`REVOKE`命令；eg: `REVOKE ALL ON table_name FROM username;`

> 所有权限使用`ALL PRIVILEGE`，所有表使用 `ALL TABLES`。eg: `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_name TO username;`


## 权限项说明

|  特权   | 缩写 | 适用 | 
|  ----  | ---- |---- | 
| SELECT	 | r ("read")	| LARGE OBJECT, SEQUENCE, TABLE (and table-like objects), table column |
| INSERT	 | a ("append")	| TABLE, table column |
| UPDATE	 | w ("write")	| LARGE OBJECT, SEQUENCE, TABLE, table column |
| DELETE	 | d	        | TABLE |
| TRUNCATE	 | D	        | TABLE |
| REFERENCES | x	        | TABLE, table column |
| TRIGGER	 | t	        | TABLE |
| CREATE	 | C	        | DATABASE, SCHEMA, TABLESPACE |
| CONNECT	 | c	        | DATABASE |
| TEMPORARY	 | T	        | DATABASE |
| EXECUTE	 | X	        | FUNCTION, PROCEDURE |
| USAGE 	 | U            | DOMAIN, FOREIGN DATA WRAPPER, FOREIGN SERVER, LANGUAGE, SCHEMA, SEQUENCE, TYPE |


### SELECT

允许从表，视图，实例化视图或其他类似表的对象的任何列或特定列中进行SELECT。还允许使用COPY TO。引用UPDATE或DELETE中现有的列值也需要此特权。对于序列，此特权还允许使用该currval功能。对于大型对象，此特权允许读取对象。

### INSERT

允许INSERT一个新行的成表，视图，等。可以在特定列（一个或多个），在这种情况下，只有那些列可以在被分配给被授权INSERT命令（其它列将因此接收默认值）。还允许使用COPY FROM。

### UPDATE

允许更新表，视图等的任何列或特定列。（实际上，任何非平凡的UPDATE命令也将需要SELECT特权，因为它必须引用表列来确定要更新的行，和/或以计算列的新值。）SELECT ... FOR UPDATE并且SELECT ... FOR SHARE除了SELECT特权之外，还需要至少对一列具有此特权。对于序列，此特权允许使用nextval和setval函数。对于大对象，此特权允许写入或截断对象。

### DELETE

允许从表，视图等中删除行。（实际上，任何非平凡的DELETE命令也需要SELECT特权，因为它必须引用表列以确定要删除的行。）

### TRUNCATE
允许在表上执行TRUNCATE。

### REFERENCES

允许创建引用表或表的特定列的外键约束。

### TRIGGER

允许在表，视图等上创建触发器。

### CREATE

对于数据库，允许在数据库中创建新的架构和发布。

对于模式，允许在模式内创建新对象。要重命名现有对象，您必须拥有该对象，并对包含的架构具有此特权。

对于表空间，允许在表空间内创建表，索引和临时文件，并允许创建将表空间作为其默认表空间的数据库。（请注意，撤消此特权不会更改现有对象的位置。）

### CONNECT

允许被授权者连接到数据库。连接启动时会检查此特权（除了检查所施加的任何限制pg_hba.conf）。

### TEMPORARY

允许在使用数据库时创建临时表。

### EXECUTE

允许调用函数或过程，包括使用在函数顶部实现的任何运算符。这是适用于函数和过程的唯一特权类型。

### USAGE

对于过程语言，允许使用该语言来创建该语言的功能。这是适用于过程语言的唯一特权类型。

对于模式，允许访问模式中包含的对象（假设还满足对象自身的特权要求）。从本质上讲，这允许被授予者在模式中“查找”对象。没有此权限，仍然可以查看对象名称，例如，通过查询系统目录。同样，在撤消该权限之后，现有会话可能具有以前执行过此查找的语句，因此这不是防止对象访问的完全安全的方法。

对于序列，允许使用currval和nextval功能。

对于类型和域，允许在创建表，函数和其他架构对象时使用类型或域。（请注意，此特权并不控制该类型的所有“用法”，例如查询中出现的该类型的值。它仅防止创建依赖于该类型的对象。此特权的主要目的是控制哪些用户可以在类型上创建依赖项，这可能会阻止所有者稍后更改类型。）

对于外部数据包装器，允许使用外部数据包装器创建新服务器。

对于外部服务器，允许使用服务器创建外部表。受赠者还可以创建，更改或删除其自己与该服务器关联的用户映射


## 参考链接

* https://tableplus.com/blog/2018/04/postgresql-how-to-grant-access-to-users.html
* https://www.postgresql.org/docs/12/ddl-priv.html