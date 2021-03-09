---
layout: post
title: "Python单例模式防止构造函数重复调用"
date: 2021-03-09 15:35:40 +0800
categories: 技术
tags: python
---


python中一般我们会使用内置放方法`__new__`来实现单例

```python
class Single(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        print('init')
```

以上代码有个缺陷，就是每次实例化后都会调用构造函数`__init__`, 我们想要的效果一般是第二次以后就直接返回之前的实例了，这才是单例嘛。

```
In [16]: for x in range(5):
    ...:     _ = Single()
    ...:
init
init
init
init
init

In [17]:
```

我们可以引入一个类属性来标志是否就行初始化，改造后代码如下

```python
class Single(object):
    _instance = None
    _is_init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if Single._is_init:
            return
        print('init')
        Single._is_init = True
```

验证

```
In [18]: for x in range(5):
    ...:     _ = Single()
    ...:
init

In [19]:
```

我们也可以通过类装饰器来实现单例

```python
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

@Singleton
class Cls2(object):
    def __init__(self):
        print('init')
```

验证

```
In [20]: for x in range(5):
    ...:     _ = Cls2()
    ...:
init

In [21]:
```