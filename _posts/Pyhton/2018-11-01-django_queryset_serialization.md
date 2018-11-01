---
layout: post
title: "Django queryset 序列化"
date: 2018-11-01 17:49:02
categories: 技术
tags: Django
---

写MVC模式的`Django`代码的时候，`queryset`可以直接传入`Template`可以直接渲染。但通过ajax请求的或者Json交互的前后分离模式就需要将`orm`返回的结果进行序列化。之前一直用`model_to_dict`来做，但这个函数有个弊端就是当数据中有不能`hash`的字段的时候会抛出异常，比如日期我们就得自己给单字段format。

最近发现Django自带的一个新姿势`serializers`，文档地址：[https://docs.djangoproject.com/en/2.1/topics/serialization/](https://docs.djangoproject.com/en/2.1/topics/serialization/)

```python
from django.core import serializers
data = serializers.serialize('json', SomeModel.objects.all(), fields=('name','size'))
```

支持以下序列化

| Identifier | Information |
| ------ | ------ |
| xml    | Serializes to and from a simple XML dialect. |
| json   | 	Serializes to and from JSON. |
| yaml   | Serializes to YAML (YAML Ain’t a Markup Language). This serializer is only available if PyYAML is installed. |

使用`DjangoJSONEncoder`统一格式化`datetime`，同理可以格式化其他类型。

```python
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.core import serializers


class DatatimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


data = serializers.serialize('json', SomeModel.objects.all(), cls=DatatimeEncoder)
```

通过`serialize`序列化的数据是这个结构的

```json
[
    {
        "pk": "4b678b301dfd8a4e0dad910de3ae245b",
        "model": "sessions.session",
        "fields": {
            "expire_date": "2013-01-16T08:16:59.844Z",
            ...
        }
    }
]
```

一般我们只对`fields`中的内容感兴趣，所以还得进一步处理一下，等看看文档在研究研究看看能不能一步到位。
