---
layout: post
title: "从 FastAPI 到 django-ninja：现代 Python Web 框架的探索与实践"
date: 2025-03-22 10:35:15 +0800
categories: 技术
tags: FastAPI Django-Ninja Django
---

工作多年，Python WEb框架从 Django、Flask、Tornado 到后来 python 支持异步后的 Sanic 都在项目上使用过，甚至还短暂涉猎过Trypyramid。
不过兜兜转转还是回到Django的怀抱，因为它在搭建业务 API 时的高效性，尤其是结合 django-rest-framework。
用其他框架基础功能还需要自行搭建，而且数据库 ORM 框架只能选择 SQLAlchemy，说实话 SQLAlchemy 差 Django的还是很多的。

最近打算做一个AI平台，现在大模型对话一般都用流式传输，流式传输在异步框架中具有天然优势。
而且看网上的例子也都是使用fastapi，所以一开始技术选型使用fastapi。fastapi宣传高性能（Async）、标准化（OpenAPI）、类型声明（Pydantic）。

## 使用 fastapi 搭建

项目结构如下

```
fastapi_app/
│── main.py             # 入口文件，创建 FastAPI 应用
│── routers/
│   ├── __init__.py
│   ├── home.py         # 主页路由
│   ├── users.py        # 用户相关路由
│── core/
│   ├── __init__.py
│   ├── middlewares.py  # 自定义中间件
│   ├── logger.py       # 日志模块
│   ├── db.py           # 数据库连接
│   ├── event.py        # 生命周期事件
│   ├── config.py       # 配置文件
│── alembic/
│   ├── versions/       # 数据库迁移文件
│   ├── env.py 
│   ├── script.py.mako 
│── alembic.ini 
```

具体代码就展示一下 `main.py` 

```python
from fastapi import FastAPI
from core.config import settings
from core.middlewares import setup_middlewares
from routers import account, lingo
from core.event import lifespan

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# 注册中间件
setup_middlewares(app)

# 注册路由
app.include_router(account.router)
app.include_router(lingo.router)

```

fastapi官方有个项目模板，搭建基础框架的时候可以参考 [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)。

其他的都不是问题，主要还是数据库连接，搭建框架的时候突然发现一个新的ORM库 `SQLModel`，我还以为有能够与 Django 竞争的库。
没想到 底层还是使用了 `SQLAlchemy`。`SQLModel` 也是 `fastapi` 作者搞的，基本就是在 `SQLAlchemy` 上适配了 `Pydantic`。
然后数据库迁移还得用 `alembic`。试着写了一下业务，这个库封装的不完全，还得暴露出 `SQLAlchemy`，不太满意。网上查了一下，大家对其的评价也不高。

在搭建项目的过程中，还发现了其他新起的ORM框架，如 `tortoise-orm`。同时也让我发现了 `django-ninja`。

## 使用 django-ninja 搭建

项目结构就完全就是 django 的，可以自己在已有的 django 项目中直接引入。这是我的大致项目结构：

```
ninja_app/
├── manage.py                 # django入口文件
├── api/                      # django-ninja API的目录
│   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── views.py
├── app/                      # django app 的目录
│   ├── __init__.py
│   └── account/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       │   ├── __init__.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
├── ninja_app/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── utils/
    ├── __init__.py
    ├── middleware.py          # 自定义中间件
    └── security.py            # 自定义认证类
```

### Router（路由拆分）

django-ninja 借鉴了 fastapi，所以写法上和 fastapi 还有flask很像。

#### `api/__init__.py`

```python
from ninja import NinjaAPI
from utils.security import TokenAuth, ApiKeyAuth

api_v1 = NinjaAPI(title="Ninja API", version='1.0', auth=[TokenAuth(), ApiKeyAuth()])
# api_v2 = NinjaAPI(version='2.0')
api_v1.add_router("/auth/", "api.auth.router_v1")
```

> django-ninja 可以有多个 NinjaAPI 实例，所以很方便提供多版本API

#### `api/auth/__init__.py`

```python
from ninja import Router

router_v1 = Router(tags=["Auth"])

from .views import *
```

#### `ninja_app/urls.py`

```python
...
from api import api_v1
...
urlpatterns = [
    ...
    path("api/v1/", api_v1.urls),
    ...
]
...
```

### 自定义API认证

我这里提供了两种认证，一种面向登录用户的（Token认证）， 一种面向程序调用的方便集成（APIKey认证）

```python
from ninja.security import APIKeyHeader, HttpBearer

class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        if key != 'token': # 自定义认证逻辑，认证不通过返回None即可返回403
            return None
        return token


class ApiKeyAuth(APIKeyHeader):
    param_name: str = "X-API-Key"

    def authenticate(self, request, key):
        if key != 'xxxxx':  # 自定义认证逻辑，认证不通过返回None即可返回403
            return None
        return key
```

### API View和参数校验

以登录接口为例

#### `api/auth/views.py`

```python
from api.auth import router_v1
from api.auth.schemas import LoginSchema


@router_v1.post("/login/", auth=None)
def login(request, payload: LoginSchema):
    token = '123'
    return {"token": token}
```

> NinjaAPI 实例添加了认证，但是下面的某个API不需要认证，可以在装饰器传入参数 `auth=None`

#### `api/auth/views.py`

```python
from typing_extensions import Self
from pydantic import model_validator
from ninja import Schema, Field


class LoginSchema(Schema):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1, max_length=150)

    @model_validator(mode='after')
    def check_login(self) -> Self:
        if self.username != 'xxx' or self.password != 'xxx':  # 自定义登录验证
            raise ValueError("Invalid username or password")
        return self
```

> django-ninja 的 Schema 使用的也是 `Pydantic`，字段校验可以使用 `Field`, 也可以使用[Pydantic - validators](https://docs.pydantic.dev/latest/concepts/validators/)

## 结束语

使用 django-ninja 包装完的 django 项目，同样可以得倒一个支持 `Async` `OpenAPI` `Pydantic` 的现代 Web 后端。
并且你还可以使用 Django 的所有便利（ORM，Admin等）。

在选择 Web 框架时，大多数业务应用其实并不需要追求极致的性能。但在实际应用中，很多时候性能瓶颈并不在 Web 框架，而是在数据库操作上。数据库查询的优化和设计，通常是影响应用性能的关键因素。对于大多数企业级应用来说，框架的易用性、生态系统和团队的熟悉度往往是更重要的考量因素。Django-Ninja 不仅能够满足现代 Web 开发对高效、标准化、类型安全的要求，同时还能充分发挥 Django 丰富的生态和成熟的功能。

总的来说，无论是选择 FastAPI 还是 Django-Ninja，都取决于项目的具体需求和团队的技术栈。性能固然重要，但更重要的是在实际开发中能够提供稳定、可维护和可扩展的解决方案。

## 参考链接

* https://fastapi.tiangolo.com/learn/
* https://django-ninja.dev/
* https://docs.pydantic.dev/latest/concepts/validators/
