---
layout: post
title: "全文检索调研（Mongodb和Whoosh）"
date: 2019-07-20 10:14:09
categories: 技术
tags: python mongodb whoosh
---

公司有一个类似搜索引擎的项目，现在公司是做保险的，这个项目就是用来搜索已经解析格式化的保险的，现在的模式搜索比较简单，就是根据保险名称、
公司等字段筛选，而且也没有先后排名。最近我leader让我调研一下对该功能进行改造，以实现全文检索，并跟搜索引擎那样根据权重实现先后排名。

因为我们数据库存储用的Mongodb，所以首先查看的在mongo层面能否实现该需求，并且我们后端是python实现，经过初步调研我选择了三种方案：mongo、
whoosh和Elasticsearch。

## Mongo

> MongoDB在2.6版本以后是默认开启全文检索的

为保险产品创建全文索引

```sql
db.product.ensureIndex({
    companyName:"text", designType:"text", insurancePeriodType:"text", literalCoding:"text", paymentMethod:"text", productName:"text", productType:"text", saleStatus:"text", id:"text", label:"text"
})
```

查询

```sql
db.product.find({$text:{$search:"保险"}})
```

这样是可以实现搜索，但有两个问题：

* mongo全文检索不能实现搜索结果打分排名

* 保险详细条款是存在label字段，该字段是json格式（区分各类条款），然后这样加入全文索引是不能被查询到的，必须把子文档字段加入全文索引

所有直接使用mongo实现的方案pass

## Whoosh

因为项目是python实现的，使用whoosh还是很方便的

#### 安装

```bash
pip3 install whoosh
```

#### 将mongo中的数据在whoosh中生成索引

将已经解析完的数据建立索引，以后新解析的保险在解析完成是添加。

```python
import os
from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.writing import BufferedWriter
from whoosh.query import And, Or, Term
from whoosh import scoring
import pymongo

mc = pymongo.MongoClient('mongodb://10.13.2.124:27017', connect=False, maxPoolSize=2000)
db = mc['ppe']
product_coll = db['product']

schema = Schema(
    id=ID(stored=True),
    companyName=TEXT(stored=True),
    designType=KEYWORD(stored=True),
    insurancePeriodType=TEXT(stored=True),
    literalCoding=TEXT(stored=True),
    paymentMethod=KEYWORD(stored=True),
    productName=TEXT(stored=True),
    productType=KEYWORD(stored=True),
    saleStatus=KEYWORD(stored=True),
    content=TEXT)
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    ix = index.create_in("indexdir", schema)
else:
    ix = index.open_dir("indexdir")


def get_content(label) -> str:
    """将label中的各字段整合到一个字段中，方便检索"""
    ...
    return content

writer = ix.writer()
for item in product_coll.find({}):
    parser = parser = QueryParser("id", ix.schema)
    with ix.searcher() as s:
        results = s.search(parser.parse(item['_id']))
        if list(results):
            print(item['_id'], 'already exists')
            continue

    content = get_content(item.get('label', ''))
    writer.add_document(
        id=item['_id'],
        companyName=item.get('companyName', ''),
        designType=item.get('designType', ''),
        insurancePeriodType=item.get('insurancePeriodType', ''),
        literalCoding=item.get('literalCoding', ''),
        paymentMethod=item.get('paymentMethod', ''),
        productName=item.get('productName', ''),
        productType=item.get('productType', ''),
        saleStatus=item.get('saleStatus', ''),
        content=content,
    )
writer.commit()
```

#### 查询

```python
parser = MultifieldParser(
    ["id", "companyName", "designType", "insurancePeriodType", "literalCoding", "paymentMethod", "productName",
    "productType", "saleStatus", "content"], schema=ix.schema)
query = parser.parse("保险")

with ix.searcher(weighting=scoring.BM25F(content_B=1)) as s:
    results = s.search_page(query, 3)
    print(list(results))
```

#### 总结

结果测试whoosh可以完美实现现在的需求

* 通过调整权重算法的参数可以调整显示的优先级，比如查询到保险名称的结果优先，那么可以将`productName`字段的权重调高

* 可以通过自带的`search_page`分页

* 我们现在解析完的保险有大约2万5千条，生成的索引文件100多M，任意查询结果秒出无压力

知乎上有个关于BM25F算法的介绍

https://zhuanlan.zhihu.com/p/31009310

## Elasticsearch

因为whoosh已经完全满足了我们现在的需求，我也就没接着调研Elasticsearch。但我感觉使用Elasticsearch是有点用不着。
因为现在只有2万5千条保险信息，并且新解析出的保险信息的正在速度也很慢，基本数量量上10万也得够呛，所以没必要上Elasticsearch。
等有时间在研究研究Elasticsearch。
