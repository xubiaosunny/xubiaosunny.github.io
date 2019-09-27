---
layout: post
title: "矩阵向量及使用Latex书写数学公式"
date: 2019-09-27 20:25:07
categories: 数学
tags: Latex 向量 矩阵
---

前段时间看完了《面向数据科学家的实用统计学》，看的也不深刻，因为使用R语言实现的，所以我也没有去实践里面的例子。
最近开始看《数据挖掘与分析：概念与算法》，这本书已经买了两年了，每次重第一页看，看不超过50页就扔下了。
想做数据分析还是得补补基础。并且之前博客也配置好了Latex数学公式，正好先熟悉熟悉语法，也方便以后的学习记录。

## 向量

下面所有公式均来自《数据挖掘与分析：概念与算法》

$$
a = \left (
  \begin{array}{c}  
    $a_{1}$ \\
    $a_{2}$ \\
    \vdots \\
    $a_{m}$ \\
  \end{array}
 \right )

b = \left (
    \begin{array}{c}  
        $b_{1}$ \\
    $b_{2}$ \\
    \vdots \\
    $b_{m}$ \\
      \end{array}
    \right )
$$

### 点乘

$$
\begin{align*}
a \cdot b &= a^{T}b \\
&= \left (
        \begin{array}{cccc}
        a_{1} & a_{2} & \cdots & a_{m}
        \end{array}
   \right )
   \cdot
   \left (
        \begin{array}{c}
        b_{1} \\ b_{2} \\ \vdots \\ b_{m}
        \end{array}
   \right ) \\
&= a_{1}b_{1} + a_{1}b_{1} + \cdots + a_{m}b_{m} \\
&=  \sum_{i=1 }^{m} a_{i}b_{i}
\end{align*}
$$

### 长度

$$
\left \| a \right \| = \sqrt{a^{T}a} = \sqrt{a_{1}^{2} + a_{2}^{2} + \cdots + a_{m}^{2}} = \sqrt{\sum_{i=1}^{m} a_{i}^{2}}
$$

### 单位向量

$$
u = \frac{a}{\left \| a \right \|} = \left ( \frac{1}{\left \| a \right \|} \right ) a
$$

### 距离

$$
D(a,b) = \left \| a - b \right \| = \sqrt{(a - b)^T(a - b)} = \sqrt{\sum_{i=1}^{m}(a_{i} - b_{i})^2}
$$

### 角度

$$
\cos θ = \frac{a^{T}b}{\left \| a \right \|\left \| b \right \|} = (\frac{a}{\left \| a \right \|})^{T} (\frac{b}{\left \| b \right \|})
$$

### 正交投影

$$
p = (\frac{a^{T}b}{a^{T}a})a
$$

## Latex语法

参考链接：

https://zhuanlan.zhihu.com/p/24502400

https://www.jianshu.com/p/97ec8a3739f6

https://blog.csdn.net/mary1992630/article/details/80015679
