---
layout: post
title: "whoosh自定义scoring和collectors"
date: 2019-11-07 19:47:19 +0800
categories: 技术
tags: whoosh
---

## 自定义scoring

scoring模块是whoosh控制搜索结果得分的。

使用whoosh自带的scoring就可以实现特别好的搜索结果，但架不住业务上的要求，就比如我们要将搜索结果内在售的排在前面，
而且还要将最近的年份的显示在前面，并且不能简单的靠是否在售和时间来排序，还要根据搜索关键词的相关性综合考虑。其实就比较蛋疼，
要控制好这几个维度的度，也就是各个维度的权重。

重写BM25FScorer

```python
from whoosh import scoring


class MyBM25FScorer(scoring.BM25FScorer):
    def __init__(self, searcher, fieldname, text, B, K1, qf=1):
        super().__init__(searcher, fieldname, text, B, K1, qf=qf)
        self.searcher = searcher

    def score(self, matcher):
        s = self._score(matcher.weight(), self.dfl(matcher.id()))
        # customize
        d = self.searcher.stored_fields(matcher.id())
        return self.customize_add_score(d, s)

    @staticmethod
    def customize_add_score(d, s):
        if d['saleStatus'] == "在售":
            # 如果在售，加一定的分数
        # 其他条件...
        if ...
            ...
        return s
```

## 自定义collectors

自定义scoring后发现确实搜索结果都按照预期的来了，但有出现一个问题，有的关键词搜索结果特别多就会特别慢，原因就是每条记录都会根据自定义逻辑就行一次取值判断加分，
匹配到的结果太多时间自然就变长了。实际测试匹配结果达到2万5千条的时候需要将近8s的时间。

其实搜索到的排在后面的数据基本都是不相关的，而且也不可能有用户去查看2w多条记录

于是可以减少匹配的数量来加快检索。

```python
from whoosh import collectors

MIN_SCORE = 6

...
class MyBM25FScorer(scoring.BM25FScorer):
    ...

    def score(self, matcher):
        s = self._score(matcher.weight(), self.dfl(matcher.id()))
        # customize
        if s < MIN_SCORE:
            return s
        d = self.searcher.stored_fields(matcher.id())
        return self.customize_add_score(d, s)


class MyUnlimitedCollector(collectors.UnlimitedCollector):
    def _collect(self, global_docnum, score):
        if score < MIN_SCORE:
            return 0
        self.items.append((score, global_docnum))
        self.docset.add(global_docnum)
        # Negate score to act as sort key so higher scores appear first
        return 0 - score
```

## 使用自定义的scoring和collectors搜索

```python
...
with ix.searcher(weighting=MyBM25F()) as s:
    c = MyUnlimitedCollector()
    s.search_with_collector(query, c)
    results = c.results()
...
```
