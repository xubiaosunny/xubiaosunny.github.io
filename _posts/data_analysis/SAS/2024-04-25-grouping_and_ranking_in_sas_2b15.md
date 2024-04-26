---
layout: post
title: "SAS实现分组内排名"
date: 2024-04-25 22:27:01 +0800
categories: 技术
tags: SAS SQL
---

在做查询计算的时候分组以及分组内排名是很常见的操作，使用SQL的话就是`group by`和开窗函数。sas的话是支持SQL语法，但是不支持开窗函数。
如果用纯sas代码也是可以实现，但是如果是先用过sql或者其他编程语言，对于sas还是有些难理解。sas的数据集（data）是按行选循环，所以很多操作前都需要进行一下排序。按这个逻辑就好理解了。

我这里以学生成绩这样简单的数据演示一下，如下为表结构

| 姓名(name) | 课程(course) | 分数(score) |
| ---- | ---- | ---- |
| 张三 | 英语 | 92   |
| 李四 | 语文 | 88   |
| ... | ... | ...   |
 
测试数据放在[student_course_score.csv](/assets/file/student_course_score.csv)文件中

## sas代码实现

首先读取csv数据到sas数据集中

```sas
proc import datafile='student_course_score.csv'
    out=student_course_score
    dbms=csv
    replace;
    getnames=yes;
run;

```

### 分组计算

使用纯sas代码实现，大概逻辑就是分组中的第一行到最后一行score加起来。

```sas
proc sort data=student_course_score;
    by name;
run;

data total_score;
    set student_course_score;
    by name;
    retain total_score 0;
    if first.name then total_score = 0;
    total_score + score;
    if last.name then output;
    drop course score;
run;
```

使用`PROC SQL`实现，和我们用MySQL或者Postgres等关系型数据库语法差不多，`group by`直接用`sum`方法计算即可。

```sas
proc sql;
    create table total_score as
    select name, sum(score) as total_score
    from student_course_score
    group by name;
run;
```

### 分组排名

同样的逻辑，就是先排序，然后通过组内前后顺序依次赋予名次

```sas
proc sort data=student_course_score;
    by course descending score;
run;

data course_rank;
    set student_course_score;
    by course;
    if first.course then ranking = 1;  /* 将第一个观察值的排名设为 1 */
    else ranking + 1; /* 对于同一分组内的后续观察值，排名递增 */
    retain ranking;  /* 保持变量在观测之间的持久性 */
run;
```

有了排名，那么类似于取每科前三名（分组取top）的筛选也方便了

```sas
data course_top3;
    set course_rank;
    if ranking <= 3;
run;
```

## 附：SQL实现

Postgres以及MySQl8.0都支持开窗函数，在进行分组排名或者分组取前几这样的计算就简单多了

```sql
SELECT
    *, row_number() over ( 
        PARTITION BY course_id ORDER BY score DESC
    )  AS ranking
FROM student_course_score;
```

## 最后

最后还是得diss一下SAS，真是服了，我用`DATALINES;`直接写入数据到数据集的话，中文后面乱码（我看默认长度是8），如果指定长度（$20.这样）又会无视分隔符导致数据错乱，不得已还是写到文件中用sas再读取到数据集。
