---
layout: post
title: "Flask项目与clery实践"
date: 2019-07-08 23:43:02
categories: 技术
tags: python flask celery
---

好久没写博客了，前段时间换工作天天加班，最近不加班了长时间不写就不想写了，今天西安凑合一篇，主要记录一下现在公司的项目实践。之前项目一直用`Django`框架，现在的公司都用`flask`，于是新项目也用flask搭建的。

## 项目结构

```text
├── app
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── serializers       # 存放参数检验的目录
│   │   │   ├── __init__.py
│   │   ├── urls.py           # flask-rest的url映射
│   │   └── views             # 存放视图函数的目录
│   │       ├── __init__.py
│   │       ├── hello.py
│   ├── cache                 # 缓存函数目录
│   │   ├── __init__.py
│   ├── db                    # 数据库目录
│   │   ├── __init__.py
│   │   └── mongo.py
│   ├── service               # 公共服务目录
│   │   ├── __init__.py
│   │   └── email.py
│   ├── tasks                 # celery任务目录
│   │   ├── __init__.py
│   └── utils                 # 公共组件目录
│       ├── __init__.py
└── tests
|    └── __init__.py
├── .env                      # 环境变量文件
├── config.py
├── Dockerfile
├── Pipfile
├── Pipfile.lock
├── docker-compose.yml
├── manage.py                 # flask启动文件
├── readme.md
```

## Celery

官方文档有介绍：

[http://flask.pocoo.org/docs/1.0/patterns/celery/](http://flask.pocoo.org/docs/1.0/patterns/celery/)


在此基础上我将make_celery放到了`app/__init__.py`中。

```python
# app/__init__.py
from flask import Flask
from config import config
from celery import Celery


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/doubao-uecv2/api/v1')

    return app


def make_celery(app):
    celery = Celery()
    celery.config_from_object(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
```
```python
# manage.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, make_celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

celery = make_celery(app)
```

自定义celery的task目录

```python
class Config:
    ...
    CELERY_IMPORTS = ('app.tasks', )
    ...
```
然后在`app/tasks/__init__.py`中将各个task导入。

## 总结

啊啊啊，大晚上的了不想写了，架子也睡半个月前搭建的了，现在也组织不起语言来，就简单写写吧。其实写项目的话还是django好使我觉得，不用装那么多插件或者自己造轮子，也可能是我用的少的缘故，像django的中间件flask有各种handle，但用起来比较别扭，有时候一些功能不知道该放到目录的什么位置。还有日志配置也踩了半天坑。但是如果只是写着玩，一两个功能用flask一个文件几行代码就可以搞定，很方便。当然flask也适合大的项目，只不过前期搭架子得多花些时间。
