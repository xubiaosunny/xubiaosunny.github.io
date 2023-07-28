---
layout: post
title: "使用disqus为博客添加评论功能"
date: 2018-04-15 23:02:57 +0800
categories: 折腾
tags: disqus jekyll
---

最近工作较忙也没时间再折腾个人博客（有点时间也和同事吃把鸡，垃圾游戏毁我青春），今天终于有一整天时间可以在搞一下，博客基本功能都差不多了，还缺个评论功能，方便别人指正我的问题（估计没人看，但是功能咱得有，这博客只当笔记用）。首先以[安静会的一篇博客](https://blog.csdn.net/u013381011/article/details/76944663)开始。

## Qisqus
进入[Qisqus](https://disqus.com/)网站我以前没使用过Qisqus，但Qisqus可以使用google授权登陆，很方便，然后就是一流程的账户注册激活，跟着一步步来。

在选择平台的时候选择```jekyll```。

### 通用代码安装说明

![](\assets\images\post\屏幕快照 2018-04-15 下午6.56.29.png)

将图中代码复制到post模板中，```<div id="disqus_thread"></div>```Qisqus会在这个```div```中渲染评论功能，所以将该```div```放到正确位置。

### 显示评论数

![](\assets\images\post\屏幕快照 2018-04-15 下午6.57.01.png)

在html中引用自己的对应js，如
```html
<script id="dsq-count-scr" src="//xubiaosunny.disqus.com/count.js" async></script>
```
然后在要显示评论数的地方添加如下代码
```html{% raw %}
<a href="{{ page.url }}#disqus_thread"></a>
{% endraw %}```

具体文档：
[https://xubiaosunny.disqus.com/admin/install/platforms/universalcode](https://xubiaosunny.disqus.com/admin/install/platforms/universalcode)
[https://help.disqus.com/developer/adding-comment-count-links-to-your-home-page](https://help.disqus.com/developer/adding-comment-count-links-to-your-home-page)

## 关于Qisqus

在之前Qisqus已经被墙了，Qisqus网站也被墙了，所以想要使用Qisqus需要些特殊的手段（你懂的），那么这就对没有特殊手段的人很不友好。我在网上也查了查有没有相关替代产品，结果是国内的类似服务一个接一个黄了。无fuck可说。
