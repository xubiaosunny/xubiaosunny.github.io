---
layout: post
title: "SAS入门使用总结"
date: 2022-07-11 18:43:23 +0800
categories: 技术
tags: SAS
---

最近跟着公司的其他同学熟悉临床试验相关的相关知识，也写了些SAS程序。在期间我也通过网络和公司的文件自学了SAS的知识，现在将这些天实践的技术内容做下总结。

## 语法结构

SAS和其他编程语言（C/Python/Java）等不太相同。其他语言面向过程或者是面向对象啥的，那么可以说SAS是面向数据集（data set）。SAS的所有操作基本是都是对数据集的
操作，毕竟SAS就是做计算分析的，SAS的数据集类似于Pandas的DataFrame。

SAS基本分为两种STEP：DATA和PROC。DATA我理解是用来加载和操作数据的，PROC是用来调用些内置方法来分析数据。STEP用`RUN`关键字结尾。

另外SAS是不区分大小写的，SAS统一会将其转为大写（upper）。

### DATA

例子定义了TEMP数据集

```sas
DATA TEMP;
    INPUT ID $ NAME $ SALARY DEPARTMENT $;
    comm = SALARY*0.25;
    LABEL ID = 'Employee ID' comm = 'COMMISION';
    DATALINES;
    1 Rick 623.3 IT
    2 Dan 515.2 Operations
    3 Michelle 611 IT
    ;
RUN;
```

常用的DATA子句

| Statement | example | 备注 |
| ----------- | ----------- | ----------- |
| INPUT | `INPUT ID $ NAME $ SALARY DEPARTMENT $;` | 字符串变量在结尾有一个$，数字值没有 |
| LABEL | `LABEL ID = 'Employee ID' comm = 'COMMISION';` | 给变量添加Label |
| DATALINES | `DATALINES;` <br>`1 Rick 623.3 IT`<br>`;` | 输入数据 |
| LENGTH | `length name $25 default=4;` | 指定变量的长度 |
| IF | `if name='Rick'` | 通过条件筛选 |
| DO | `do;`<br>`months=years*12;`<br>`end;` | 循环 |
| SET | `set TEMP;` | 从一个或多个数据集中读取观测值 |
| MERGE | `merge TEMP1 TEMP2;`<br>`by ID;` | 类似SQL的join |
| KEEP | `keep col:;` | 保留col开头的列 |

### PROC

例子打印了TEMP数据集中SALARY大于700的数据

```sas
PROC PRINT DATA = TEMP;
    WHERE SALARY > 700;
RUN;
```

除了`PRINT`，我还有以下语句常用到

* `IMPORT` 从文件引入数据集
* `SQL` SAS支持SQL语句得到数据集
* `TRANSPOSE` 做透视表
* `SORT` 排序


## 实际使用

### 缺失值填充

```sas
data TEMP
    set _TEMP;
    array char(1:8) $ tmpstr1-tmpstr8:
    do i=1 to dim(char);
        if missing(char[i]) then char[i]='-'
    end;
    drop i;
run;
```

### 合并数据集（JOIN）

```sas
DATA _merge;
    MERGE _TEMP1 _TEMP2;
    BY MID;
RUN;
```

### SQL返回数据集

```sas
PROC SQL;
    CREATE TABLE WANT AS
    select
        a.*, b.*
    from TEMP1 a
    left join TEMP2 b
    on a.MID=b.MID
RUN;
```

### 读取excel数据到sas数据集

```sas
FILENAME REFFILE '/data/data_demo.xlsx';
PROC IMPORT DATAFILE=REFFILE DBMS=XLSX OUT=WORK.TEMP;
    GETNAMES=YES;
    SHEET="Sheet1";
RUN;
```

### 透视表

```sas
PROC TRANSPOSE data=_TEMP out=TEMP(drop=_name_);
    BY ANME;
    VAR VALUE;
    ID KEY;
RUN;
```

### 字符串操作

```sas
/* 
去空格
left: 刪除字符串左边
right： 刪除字符串右边
trim：刪除字符串右边
strip: 刪除字符串前后空格
compress: 删除字符串中所有空格
compbl: 将连续两个或以上的空格压缩为1个空格
 */
str1 = strip(str2)
/* 
字符串链接 
||: 字符串链接符
cat: 与||作用类似，保留首尾全部空格
catt: 连接之前会去掉各字符串尾部空格，相当于连接符结合trim使用
cats: 连接之前会去掉首尾全部空格，相当于连接符结合strip使用
catx: 连接之前会去掉首尾全部空格，并且在字符串之间加上一个指定的字符串
*/
str3 = str1 || '-' || str2
str3 = cats(str1, '-', str2)
```
### 日期格式

```sas
/*
D类型，YY年，MM月，DD日

YYMMDDD10. 2022-07-12
YYMMDDD9.  22-07-12

S类型，YY年，MM月，DD日

YYMMDDS10. 2022/07/12
YYMMDDS9.  22/07/12

同样的还有B(空格分割)，N(不分割)，C(:冒号分割), P(.点分割)等

date类型

DATE8.     16DEC09
DATE9.     16DEC2009
*/

DATA TEMP;
    INPUT VAR1 DATE9. VAR2 MMDDYY10. ;
    STRING1 = put(VAR1, YYMMDDD10.);
    STRING2 = put(VAR2, DATE9.);
RUN;
```
