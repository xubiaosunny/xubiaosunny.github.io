---
layout: post
title: "Django restful api 实践"
date: 2019-05-09 23:38:03
categories: 技术
tags: Django restful 认证
---

之前帮朋友创业做app后台，现在框架也已经搭建起来了，业务就不记录了，主要记录以下几个方面：

* restful风格

* 自动生成文档

* token及签名认证

要说到django restful，大多会用到`djangorestframework`，我也不例外。

## 项目目录结构

```text
├── Pipfile
├── Pipfile.lock
├── README.md
├── api  # 所有api业务代码在此目录
│   ├── README.md
│   ├── __init__.py
│   ├── apps.py
│   ├── serializer  # 存放serializer代码
│   │   ├── __init__.py
│   │   ├── ...
│   ├── tests.py
│   ├── urls.py
│   └── views  # 存放视图函数代码
│       ├── __init__.py
│       ├── ...
├── db  # 数据库模型
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── const.py
│   ├── db_admin  # 分文件配置admin，在admin.py同一引入
│   │   ├── __init__.py
│   │   ├── ...
│   ├── db_models  # 分文件建立数据库模型，在model.py同一引入
│   │   ├── __init__.py
│   │   ├── ...
│   ├── migrations # 存放数据库迁移文件，Django默认
│   │   ├── __init__.py
│   │   ├── ...
│   └── models.py
├── locale  # 存放国际化目录
├── manage.py
├── utils  # 公共组件目录
│   ├── __init__.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── permissions.py  # 权限验证class
│   │   ├── response.py  # response统一封装
│   │   └── validators.py  # 通用验证函数，可用于serializer
│   └── core  # 用于存放其他封装，如对接其他平台
│       ├── __init__.py
│       ├── ...
└── yasuo
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## 设计rest风格的api

参考阮一峰的文章《[RESTful API 最佳实践](http://www.ruanyifeng.com/blog/2018/10/restful-api-best-practices.html)》

不同请求方式对应不同操作:

* GET：读取（Read）
* POST：新建（Create）
* PUT：更新（Update）
* PATCH：更新（Update），通常是部分更新
* DELETE：删除（Delete）

### Response返回结果规则

返回结果通过http状态码进行判别

#### 2xx (`200` `201` `204`)

只要返回2xx的状态码都代表成功，返回内容里面没有特殊结构，例如(登陆成功)：

```json
{
    "token": "71af586177718ec7e6a81e83dff9bcas901fc07c"
}
```

#### 400

代表失败，一般用于参数校验返回错误信息。解包后`detail`字段内为详细信息，例如(登陆时验证手机号及短信验证码)：

```json
{
    "msg": "Invalid Params",
    "detail": {
        "phone": [
            "The phone number is incorrect."
        ],
        "sms_code": [
            "The verification code is incorrect or has expired"
        ]
    }
}
```

#### 401

未认证(token校验未通过)

#### 404

请求的资源未找到

#### 403

权限不足

### 封装rest风格的response返回函数

```python
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT
)


def response_200(data):
    return Response(data, status=HTTP_200_OK)


def response_201(data):
    return Response(data, status=HTTP_201_CREATED)


def response_204(data):
    return Response(data, status=HTTP_204_NO_CONTENT)


def response_400(data, msg='Invalid Params'):
    return Response({"msg": msg, "detail": data}, status=HTTP_400_BAD_REQUEST)


def response_404(msg='Not Found'):
    return Response({"msg": msg}, status=HTTP_404_NOT_FOUND)
```

在进行返回response的时候程序需调用统以上函数，不能私自返回。

## 自动生成文档

djangorestframework自带文档生成，但需要安照其特定的结构写代码，官方文档地址：https://www.django-rest-framework.org/topics/documenting-your-api/

如果想加入自己写的到文档中可以这么干（自己写的markdown会加到文档最前面），而且可以添加权限：

```python
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from django.conf import settings

doc_description = ''

with open(os.path.join(settings.BASE_DIR, 'api', 'README.md')) as f:
    doc_description = f.read()

urlpatterns = [
    ...
    path('docs/', include_docs_urls(title='Documents', description=doc_description, permission_classes=(AllowAny, ))),
]
```

若要生成文档并显示需要提交的参数视图类需要继承`generics.GenericAPIView`或其子类。如：

```python
from api.serializer.auth import LoginSerializer
from rest_framework.permissions import AllowAny


class TokenView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """登陆"""
        ...

    def delete(self, request):
        """退出登陆"""
        ...
```

这样生成的文档会根据Serializer显示接口所需的参数，并将类及类方法上的注释添加到文档上，以首先文档自动生成。

## token及签名认证

token认证不用说，直接用djangorestframework框架的即可。因为系统会有部分不需要token认证的接口（即匿名用户也可访问的接口），如发送短信验证码，为了防止接口被攻击滥用，需为其添加验证（客户端与服务端的验证）

访问需要签名验证的接口需添加类似以下的Header

```
Authorization: Signature 337f3fbccf03bada424fbb78b13107df 2019-05-08T10:26:00
```

认证内容分为三部分(认证方式 签名 日期)，中间使用空格隔开

日期使用UTC时间，格式方式为`yyyy-MM-dd'T'HH:mm:ss`

生成签名的方式：取 `ACCESS_KEY`+URI+时间字符串 的MD5

服务端验证签名代码：

```python
from rest_framework.permissions import BasePermission
import hashlib
import datetime

from yasuo.config import ACCESS_KEY


class SignaturePermission(BasePermission):
    def has_permission(self, request, view):
        # "Signature xxxxxxxxxxx %Y-%m-%dT%H:%M:%S"
        authentication = str(request.META.get('HTTP_AUTHORIZATION', None))
        try:
            authentication_type, signature, date_str = authentication.split(" ", maxsplit=2)
            datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            return False
        if authentication_type != "Signature":
            return False
        m = hashlib.md5()
        m.update(ACCESS_KEY.encode('utf-8'))
        m.update(request.path.encode('utf-8'))
        m.update(date_str.encode('utf-8'))
        return signature == m.hexdigest()
```

## 总结

之前的开发工作虽然也都是json交互，但接口风格不是restful的（只有post和get），其实一直都知道rest，但一直没机会用（工作中的项目都没采用）。本来工作之余没多少自己的时间。现在接了这个活，更是占满了我的业余时间，希望他的创业能成吧！！！
