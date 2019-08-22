---
layout: post
title: "在垂直领域内优化Whoosh搜索结果"
date: 2019-08-22 17:36:02
categories: 技术
tags: Whoosh jieba BM25F
---

刚开始使用`whoosh`建立了全文检索后试了几个感觉搜索结果还是蛮准的（因为我用的例子比较常见，所以结果比较符合预期），但别人试过之后发现很多搜索结果一点都不准，而且有的翻好几页都没有想要的结果。。。
很郁闷，其实搜索结果也不是不准，毕竟人家算法打分就是这样，自己看看里面的内容就会发现这些排在前面的是有原因的，只是不符合特定领域的预期而已，后来跟我leader一起又就行了比较深入的研究，对搜索
进行了优化。

公司做保险中介平台的，这个搜索主要用来搜索条款信息的，要是放在香google，百度这样不分行业就是单纯的搜索，很多结果都是没问题的，但在垂直领域需要对其进行优化。

## BM25F算法参数调整

第一次使用的时候不知道在看过一篇文章，他的权重是这样设置的`scoring.BM25F(title_B=10, content_B=1)`，然后我就抄了过来，我以为`*_B`是设置权重，于是我按这个逻辑就写了类似的代码，
其实这样设置是错误的。真的坑，做什么还是要了解原理，不能上来就抄啊。

通过查看资料跟查看whoosh源码才知道`B`的作用是对(文档长度/文档平均长度)的放大或缩小，`B`越大对文档长度的惩处越大。一般情况保持默认0.75就好，这是实验得出的结论，当然有需要的话自己也可以进行调整。

> b 需要在 0 到 1 之间。有些实验测试了增量为 0.1 左右时的各个值，大部分实验得出的结论是 b 在 0.3-0.9 这个范围内可以获得最优的效果

`BM25F`是在`BM25`上扩展而来，whoosh源码中的bm25算法模型

```python
def bm25(idf, tf, fl, avgfl, B, K1):
    # idf - inverse document frequency
    # tf - term frequency in the current document
    # fl - field length in the current document
    # avgfl - average field length across documents in collection
    # B, K1 - free paramters

    return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * fl / avgfl)))
```

我们的需求中有很多字段，但条款详细内容对结果的权重需要放低

等等在写
