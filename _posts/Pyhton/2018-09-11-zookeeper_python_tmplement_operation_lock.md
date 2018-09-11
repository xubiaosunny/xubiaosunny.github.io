---
layout: post
title: "python使用Zookeeper实现操作锁"
date: 2018-09-11 18:45:55
categories: 技术
tags: Zookeeper python
---

今天做产品购买的时候看到之前的一些代码，核心代码如下

```python
from kazoo.client import *
from gateway import config


class ZookeeperLock:
    def __init__(self, servers):
        self.zk = KazooClient(",".join(servers))
        last_exception = None
        for i in range(5):
            try:
                self.zk.start()
            except Exception as e:
                last_exception = e
        if last_exception is not None:
            raise last_exception

    def get_lock(self, path, identifier):
        return self.zk.Lock(path, identifier)

    @classmethod
    def instance(cls):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = ZookeeperLock(config.ZOOKEEPER_SERVERS)
        return cls.__instance__

# ...

lock = ZookeeperLock.instance().get_lock("/xxx/xxx", 'xxx')
lock.acquire()

# ...

lock.release()
```

在我查阅资料并问了了解Zookeeper的同事后明白了其中的作用。`acquire`其实是条件阻塞的函数，拿不到锁的话就会阻塞，直到拿锁的把锁释放掉才会执行下面的代码（我们这里是购买产品）。这样做的作用是防止多个地方同时购买，可能同时扣款写数据库导致数据不准确。`release`用来释放锁。

Zookeeper的python包`kazoo`文档地址 https://kazoo.readthedocs.io/

为了验证逻辑的准确性，我写了个脚本对zookeeper实现锁操作做了测试。

```python
import os
import sys
import django
import time
import threading


def factorial(name, number):
    print("Task %s: Start ...." % (name))
    lock = ZookeeperLock.instance().get_lock("/xxx/xx", '123123')
    print("Task %s: Get Lock" % (name))
    lock.acquire()
    print("Task %s: Doing ..." % (name))
    for i in range(1, number + 1):
        time.sleep(1)
    lock.release()
    print("Task %s: Unlock" % (name))


if __name__ == "__main__":
    t1 = threading.Thread(target=factorial, args=("A", 5))
    t2 = threading.Thread(target=factorial, args=("B", 2))
    t1.start()
    t2.start()
```

用两个线程模拟两个操作，A 先拿到锁，所以在前5秒B一直在阻塞状态，等到A释放锁后，B才开始“Doing”。

```log
Task A: Start ....
Task B: Start ....
Task A: Get Lock
Task B: Get Lock
Task A: Doing ...
# 这里了暂停5秒
Task A: Unlock
Task B: Doing ...
# 这里了暂停2秒
Task B: Unlock
```

经过一些了解，zookeeper就像一个更大的全局变量。接下来在深入研究一下。
