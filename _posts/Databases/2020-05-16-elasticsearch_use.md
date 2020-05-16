---
layout: post
title: "Elasticsearch使用及踩坑"
date: 2020-05-16 10:56:54
categories: 技术
tags: elasticsearch ES python
---

elasticsearch使用起来还是比较方便的，es提供rustful风格的api，直接可以使用http请求来使用。

## 索引

> 通过GET请求`/_cat/indices?v`查看索引

### mappings

在索引中添加数据，首先得设计索引的`mappings`, `mappings`就好比mysql中的ddl，用于创建表的结构。ES中分为index和type（类似于db和table）。
以下是type为default的示例。

```json
{
    'default': {
        "properties": {
            "test": {
                "type": "keyword"
            }
        }
    }
}
```

ES的数据类型还是蛮多的，我基本上只用到`keyword` `text` `integer`

官方文档地址：https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html

### 通过别名索引重建

在实际使用的时候，我们避免不了进行索引重建（比如mappings、分词规则等的修改后必须重建索引），但在生产中对索引名检索的化避免得删除旧索引在创建新索引，这样在过程中就会搜索不到结果，影响用户体验。
这种情况大家一般都是通过别名来进行搜索，就是先创建一个新的索引并把数据写入后再把旧索引的别名删除并为新索引添加上该别名，搜索的时候通过别名来搜索而不是通过索引名。

### 索引重建时锁定

重建索引可能是一个漫长的过程，为了减少资源占用和有序性。在一个进程进行索引构建的时候需要进行加锁，否则多次触发可能多个进程同时构建同一个索引，不光占用资源而且可能发生错误。
我的方案是每次通过文件对该索引加锁，也可以使用zookeeper等工具。

### 中文分词

我的中文分词器用的是ik_smart。安装和自定义分词网上都有教程，需要操作elasticsearch服务。

> 通过GET请求 `/_analyze?analyzer=ik_smart&pretty=true&text=测试文本` 来查看分词结果

### 实现代码

下面是我实现的es索引的抽象基类，我把每个index的type都限制成一个了，默认为`default`，子类只要实现`mappings`和`index_prefix`属性及`build_index`方法即可。
`build_index`方法中主要实现数据的插入，数据插入时最好使用`bulk`来批量插入，我一般每次插入1000条，如果es服务性能不足或者网络带宽较小批量插入时可能超时（默认10s），可适当加大超时时间。

```python
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError
import abc
import os
from config.conf import Config
import logging
import contextlib
import fcntl


class ElasticsearchClient(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ElasticsearchClient, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        es_uri = os.environ.get('ELASTICSEARCH_URI')
        self.es = Elasticsearch(hosts=es_uri.split(','))

    def get_client(self):
        return self.es


class SearchBase(metaclass=abc.ABCMeta):
    alias = None
    build_lock_file = None

    def __init__(self, _type='default'):
        self.es = ElasticsearchClient().get_client()
        self._type = _type
        if self.alias is None:
            self.alias = self.index_prefix
        if not self.build_lock_file:
            self.build_lock_file = os.path.join(Config.LOGFILE_PATH, f'{self.index_prefix}.lock')

    @property
    @abc.abstractmethod
    def index_prefix(self) -> str:
        """索引名前缀"""

    @property
    @abc.abstractmethod
    def mappings(self) -> dict:
        """
        mappings, eg.
        {
            'default': {
                "properties": {
                    "test": {
                        "type": "keyword"
                    }
                }
            }
        }
        """

    @abc.abstractmethod
    def build_index(self, index):
        """建立索引"""

    @contextlib.contextmanager
    def lock_build(self):
        f = open(self.build_lock_file, 'a')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            f.close()
            logger.warning(f'{self.index_prefix} build is locked')
        else:
            yield True
            f.close()
            os.remove(self.build_lock_file)

    def rebuild_index(self):
        with self.lock_build() as flag:
            if flag is False:
                logger.warning('this index already locked! maybe other thread is doing this')
                return
            new_index = self.create_index(no_alias=True)
            self.build_index(new_index)
            indices = self.es.indices.get(self.index_prefix + '*')
            old_indices = [index for index in indices.keys() if index != new_index]
            remove_actions = [{"remove": {"index": index, "alias": self.alias}} for index in old_indices]
            self.es.indices.update_aliases({
                "actions": [
                    {"add": {"index": new_index, "alias": self.alias}},
                    *remove_actions
                ]
            })
            for index in old_indices:
                self.es.indices.delete(index)

    def create_index(self, no_alias=False):
        import random
        import string
        body = {
            "mappings": self.mappings,
        }
        if not no_alias:
            body['aliases'] = {
                self.alias: {}
            }

        if not no_alias and self.es.indices.exists_alias(self.alias):
            raise Exception(f'alias [{self.alias}] already exists')

        for _ in range(3):
            index = self.index_prefix + '-' + ''.join(random.sample(string.ascii_lowercase + string.digits, 4))
            if not self.es.indices.exists(index):
                self.es.indices.create(index, body=body)
                return index
        else:
            raise Exception('create index fail')

    def delete_index(self):
        try:
            self.es.indices.delete(self.index_prefix)
        except NotFoundError:
            pass
        except Exception as e:
            raise e

    def create(self, _id, body, **kwargs):
        return self.es.create(self.alias, _id, body, doc_type=self._type, **kwargs)

    def get(self, _id, **kwargs):
        try:
            return self.es.get(self.alias, _id, doc_type=self._type, **kwargs)
        except:
            return None

    def update(self, _id, body, **kwargs):
        return self.es.update(self.alias, _id, body, doc_type=self._type, **kwargs)

    def delete(self, _id, body, **kwargs):
        return self.es.delete(self.alias, _id, body, doc_type=self._type, **kwargs)

    def bulk(self, body, **kwargs):
        return self.es.bulk(body, index=self.alias, doc_type=self._type, **kwargs)

    def count(self, body=None, **kwargs):
        return self.es.count(body=body, index=self.alias, doc_type=self._type, **kwargs)

    def search(self, body=None, **kwargs):
        return self.es.search(body=body, index=self.alias, doc_type=self._type, **kwargs)

    def bulk_action(self, actions):
        return helpers.bulk(self.es, actions, request_timeout=120)
```

## 搜索

### `should`和`must`

`should`类似于sql中的`OR`, 各个查询条件是或的关系

`must`类似于sql中的`AND`, 各个查询条件是与的关系

### `term`和`wildcard`

在es中`match`的查询是一种全文检索的查询方式，但想要实现`=`(直等于)的查询可以使用`term`.

`wildcard`是通配符查询，类似与sql中的`like`。需要注意的是使用`wildcard`是比较耗费资源的，而且只有类型为`keyword`的字段才能使用通配符。
在`text`类型的且使用了分词器的字段需要为器建立一个`keyword`类型的属性才能使用通配符。

```json
...
    "name": {
        "type": "text",
        "index": True,
        "analyzer": "ik_smart",
        "store": True,
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
...
```

通配符查询使用keyword属性进行查询

```json
    "wildcard": {
        'name.keyword': '*测试*',
    }
```

### 自定义查询(script)

官方文档：https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-guide.html

ES支持自定义脚本，使用的语言是`painless`，如下自定义了文档的打分（ES默认算法得分 + 文档及基本分数）

```json
"query": {
    "function_score": {
        "functions": [
            {
                "script_score": {
                    "script": {
                        "params": {
                        },
                        "lang": "painless",
                        "source": """
                            return _score + doc['base_score'].value;
                        """
                    }
                }
            }
        ],
    }
},
```

### 其他

不返回某些字段

```json
{
    "_source": {
        "excludes": ["content"]
    }
}
```

分页

```json
{
    ...

    "from": (page - 1) * size,
    "size": size
}
```

定义字段权重

```json
{
    "match": {
        "name": {
            "query": "测试",
            "boost": 2
        }
    }
}
```
