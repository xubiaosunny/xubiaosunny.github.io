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

我们的需求中有很多字段，但条款详细内容对结果的权重需要放低，于是设置算法参数`scoring.BM25F(title_B=10, content_B=1)`，我在content中断测试了`B`参数的极端值，
当`content_B=1`时搜索结果同一条记录的得分要高于`content_B=0`的时候，可以看出要降低某个字段的权重需设置较大些的参数`B`。

## 自定义分词方式和调整词频

在某些情况下光靠调整算法还是很难找到最合适的结果，虽然在使用`whoosh`时使用了`jieba`分词，但仍需要调教才能达到更好的效果

### 单字符英文和数字

这是我们遇到的一个问题，中文分词用了jieba的`ChineseAnalyzer`来做whoosh中文字段的`Analyzer`。大多数字段没啥问题。但保险的条款名很多值这样的 
‘xxx(A款)’、‘xxx(B款)’、‘xxx1号xxx’、‘xxx2号xxx’，当我们想搜索‘xxx(A款)’的时候排在前面的很可能是`xxx(E款)`。我打印搜索的时候发现`A` 和 `1`这样的单字符
没有分词。查看源码发现非中文字符的单字符都被忽略了，源码如下

```python
# encoding=utf-8
from __future__ import unicode_literals
from whoosh.analysis import RegexAnalyzer, LowercaseFilter, StopFilter, StemFilter
from whoosh.analysis import Tokenizer, Token
from whoosh.lang.porter import stem

import jieba
import re

STOP_WORDS = frozenset(('a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can',
                        'for', 'from', 'have', 'if', 'in', 'is', 'it', 'may',
                        'not', 'of', 'on', 'or', 'tbd', 'that', 'the', 'this',
                        'to', 'us', 'we', 'when', 'will', 'with', 'yet',
                        'you', 'your', '的', '了', '和'))

accepted_chars = re.compile(r"[\u4E00-\u9FD5]+")


class ChineseTokenizer(Tokenizer):

    def __call__(self, text, **kargs):
        words = jieba.tokenize(text, mode="search")
        token = Token()
        for (w, start_pos, stop_pos) in words:
            if not accepted_chars.match(w) and len(w) <= 1:
                continue
            token.original = token.text = w
            token.pos = start_pos
            token.startchar = start_pos
            token.endchar = stop_pos
            yield token


def ChineseAnalyzer(stoplist=STOP_WORDS, minsize=1, stemfn=stem, cachesize=50000):
    return (ChineseTokenizer() | LowercaseFilter() |
            StopFilter(stoplist=stoplist, minsize=minsize) |
            StemFilter(stemfn=stemfn, ignore=None, cachesize=cachesize))
```

于是我仿照源码的`ChineseTokenizer`写了一个带英文跟数字的`ChineseWithSimpleTokenizer`，其实就是改了一下正则，让其匹配到`1-9,a-z,A-Z`

```python
accepted_chars = re.compile(r"[\u4E00-\u9FD5,1-9,a-z,A-Z]+")


class ChineseWithSimpleTokenizer(Tokenizer):
    def __call__(self, text, **kargs):
        words = jieba.tokenize(text, mode="search")
        token = Token()
        for (w, start_pos, stop_pos) in words:
            if not accepted_chars.match(w) and len(w) <= 1:
                continue
            token.original = token.text = w
            token.pos = start_pos
            token.startchar = start_pos
            token.endchar = stop_pos
            yield token

```

但改后发现字母`B`可以分词了，但`A`却不能，又检查一边发现`LowercaseFilter`将字母都小写了，然后`StopFilter`将`a`按停用词给过滤了。于是

```python
chinese_with_simple_analyser = (
    ChineseWithSimpleTokenizer() | LowercaseFilter() | StemFilter(stemfn=stem, ignore=None, cachesize=50000))
```

然后将`chinese_with_simple_analyser`用于条款名字段实现精确查询。

### 调整词频

词频是个需要慢慢调教的地方，需要根据不同的领域定义。在jieba中调整词频方法如下

```python
# 强制调高词频
jieba.add_word('多倍保')
jieba.suggest_freq('多倍保', True)
# 强制调低词频
jieba.del_word('保险')
```

这样分词结果就会有“多倍保”这个词，而不是单纯的分词为“多倍”和“保”。强制调低词频“保险”后，分词结果就不会有“保险”这个词。
为啥要去掉保险呢，因为保险这个词在条款中太多了，在搜索xxx保险的时候，"保险"这个词在条款内容出现频率太高，
就会以为这个拉高分数导致不符合条件的结果排在前面。

大概就是这么个意思，调整该领域的特有词频来提高搜索的准确率，这个比其他优化都要立竿见影。
