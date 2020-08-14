---
layout: post
title: "通过pgloader将nextcloud的数据从mysql8.0迁移到postgres"
date: 2020-08-13 19:00:30 +0800
categories: 折腾
tags: nextcloud mysql PostgreSQL
---

## 通过`pgloader`同步数据

创建用户`nextcloud`和数据库`nextcloud`，并将库`nextcloud`分配给用户`nextcloud`

```bash
docker run -it --rm postgres psql -h 192.168.10.3 -p 15432 -U postgres -W

postgres=# CREATE USER nextcloud WITH PASSWORD '<password>';
postgres=# CREATE DATABASE nextcloud TEMPLATE template0 ENCODING 'UNICODE';
postgres=# ALTER DATABASE nextcloud OWNER TO nextcloud;
postgres=# GRANT ALL PRIVILEGES ON DATABASE nextcloud TO nextcloud;
```

将mysql中的数据迁移到postgres中

```bash
docker run --rm dimitri/pgloader:latest pgloader mysql://nextcloud:<password>@192.168.10.3:3306/nextcloud postgresql://nextcloud:<password>@192.168.10.3:15432/nextcloud
```

### 问题

`pgloader`报了如下错误:

```out
ERROR Database error 42601: syntax error at or near "unsigned"
QUERY: CREATE TABLE database.test_unsigned_serial
(
  id int unsigned not null
);
```

原因是我使用的是mysql8，mysql8使用了`int`而不是之前的`integer`，而`pgloader`（我是用的版本为3.6.3~devel）还没有兼容。具体可以看看下面的issue

https://github.com/dimitri/pgloader/issues/1186

### 解决

思路是先将mysql8的数据迁移到mysql5.7，然后在将数据迁移到postgres

导出数据

```bash
docker run --rm mysql mysqldump -u nextcloud -p <password> nextcloud > /data/nextcloud.sql
```

启动mysql5.7实例

```bash
docker run --rm -e MYSQL_ROOT_PASSWORD=<password> -p 3307:3306 -v /data:/data -d mysql:5.7
```

导入到mysql5.7

```bash
mysql> CREATE DATABASE `nextcloud` DEFAULT CHARACTER SET utf8mb4 ;
mysql> use nextcloud ;
mysql> source /data/nextcloud.sql
```

然后通过mysql5.7迁移到postgres

```bash
docker run --rm dimitri/pgloader:latest pgloader mysql://root:<password>@192.168.10.3:3307/nextcloud postgresql://nextcloud:<password>@192.168.10.3:15432/nextcloud
```

## 修复nextcloud数据

### 修复Schema归属

数据迁移完后，登录发现登录不了，查看数据发现同步的所有表都归属于`nextcloud`这个Schema，正常来说表应该在`public`这个Schema中，我在网上搜到以下sql来批量修改Schema

```sql
DO
$$
DECLARE
    row record;
BEGIN
    FOR row IN SELECT tablename FROM pg_tables WHERE schemaname = 'nextcloud' -- and other conditions, if needed
    LOOP
        EXECUTE 'ALTER TABLE nextcloud.' || quote_ident(row.tablename) || ' SET SCHEMA public;';
    END LOOP;
END;
$$;
```

然后再次登录就正常了

### 修复表索引归属

```bash
sudo -u www-data php /var/www/nextcloud/occ db:add-missing-indices
```

## 数据验证

为了验证迁移后的数据可靠性，我将nextcloud版本升级到了`19.0.1`（升级过程中有数据库的migrate操作），整个升级过程没有报错，浏览页面功能也没有报错，基本可以确定迁移成功。

> 重新扫描文件
  `sudo -u www-data php /var/www/nextcloud/occ files:scan --all`

## 参考链接

* https://stackoverflow.com/questions/10218768/how-to-change-schema-of-multiple-postgresql-tables-in-one-operation

* https://github.com/dimitri/pgloader

* https://docs.nextcloud.com/server/15/admin_manual/configuration_database/linux_database_configuration.html
