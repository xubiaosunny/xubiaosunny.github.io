---
layout: post
title: "使用gettext为flask添加国际化"
date: 2019-11-07 19:00:07 +0800
categories: 技术
tags: flask i18n gettext
---

不得不说还是django用起来顺手，基本的需求框架都以提供，配合起来也方便。现在公司用flask多，最近做国际化，自己使用python自带的gettext做了实现。

虽然flask也用Flask-Babel等i18n的插件，但感觉实现起来也不难就自己做了，顺便借此看看其django的实现。

## gettext

文档地址：https://docs.python.org/3/library/gettext.html

多语言示例

```python
import gettext

lang1 = gettext.translation('myapplication', '/path/to/my/language/directory' languages=['en'])
lang1 = gettext.translation('myapplication', '/path/to/my/language/directory' languages=['fr'])
lang1 = gettext.translation('myapplication', '/path/to/my/language/directory' languages=['de'])

# start by using language1
lang1.install()

# ... time goes by, user selects language 2
lang2.install()

# ... more time goes by, user selects language 3
lang3.install()
```

`'/path/to/my/language/directory'`为各语言文件夹上一层，各语言文件夹下需有`LC_MESSAGES`文件夹，
且生存的mo文件名需要与`'myapplication'`一致。详见下面的目录结构与代码。

## 结合flask具体实现

### 目录结构

```text
├── locale
│   ├── en
│   │   └── LC_MESSAGES
│   │       ├── flask.mo
│   │       └── flask.po
│   └── zh-hans
│       └── LC_MESSAGES
│           ├── flask.mo
│           └── flask.po
└── utils
    ├── __init__.py
    ├── i18n.py
    ├── ...
```

### 具体代码（utils/i18n.py）

```python
# -*- coding: utf-8 -*-
import gettext
import os
from flask import request
from config.conf import BASE_DIR


locale_dir = os.path.join(BASE_DIR, 'locale')

instance_list = {}


def compile_messages():
    """编译所有语言的po文件为mo文件"""
    for name in os.listdir(locale_dir):
        _locale_dir = os.path.join(locale_dir, name)
        if os.path.isdir(_locale_dir):
            cmd = f"msgfmt {_locale_dir}/LC_MESSAGES/flask.po -o {_locale_dir}/LC_MESSAGES/flask.mo"
            print(cmd)
            os.system(cmd)


for name in os.listdir(locale_dir):
    _locale_dir = os.path.join(locale_dir, name)
    if os.path.isdir(_locale_dir):
        try:
            lang_instance = gettext.translation('flask', locale_dir, [name])
        except FileNotFoundError:
            compile_messages()
            lang_instance = gettext.translation('flask', locale_dir, [name])
        except Exception as e:
            raise e
        lang_instance.install()
        instance_list[name] = lang_instance


def t(s, lang='en'):
    try:
        lang = request.headers.get('lang')
    except Exception:
        pass

    if lang not in instance_list:
        lang = 'en'
    return instance_list[lang].gettext(s)

```

### 使用

```python
from utils.i18n import t as _

print(_("Hello Word"))
```

### 封装flask命令编译mo文件

```python
...
from flask_script import Manager, Command


class CompileMessagesCommand(Command):
    def run(self):
        from utils.i18n import compile_messages
        compile_messages()


manager = Manager(app)
manager.add_command("compilemessages", CompileMessagesCommand())
...
```
