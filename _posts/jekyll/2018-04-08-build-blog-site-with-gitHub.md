---
layout: post
title: "利用github搭建博客（分页、标签、分类、搜索等)"
date: 2018-04-08 23:57:11
categories: 折腾
tags: github pages jekyll
---
前端时间公司来了个新同事，交流笔记啥的的时候，他提到用github搭博客，当时不太清楚具体咋玩。于是回家后就查了查，于是就查到了[GitHub Pages](https://pages.github.com/)，又看了几篇别人写的相关博客，感觉挺有意思，之前只知道开个vps啥的用来搭博客，由于得花钱也懒得弄。之前一直有技术知识都记在[为知笔记](http://www.wiz.cn/)（即使后来为知开始收钱了，不过倒也不贵，由于一直用就付了两年的）。后来一直想换个平台，也没个合适的，主要笔记也不好迁移。之前也一直没有写博客的习惯，正好接着这次搭建养成一个习惯。本篇就记录一下趁清明假期搭建我的博客的整个过程。

# 使用[GitHub Pages](https://pages.github.com/)建立自己的网站
1 在[github](https://github.com/)上新建一个repo，名称为username.github.io，username为自己的账户名，比如我的repo名为[xubiaosunny.github.io](https://github.com/xubiaosunny/xubiaosunny.github.io)

2 克隆到本地
```shell
git clone https://github.com/username/username.github.io
```
3 添加index.html， 并写入内容
```shell
cd username.github.io
echo "Hello World" > index.html
```
4 commit & push
```shell
git add -A
git commit -m "Initial commit"
git push -u origin master
```
5 打开浏览器访问https://username.github.io就可以看到index.html中的内容

# 使用[jekyll](http://jekyllcn.com)生成静态页面，渲染markdowm
## 起步也很简单
> 安装
```shell
gem install jekyll
```
如果没有ruby环境先安装ruby（我搭建的时候是使用的Debain），ubuntu一样。Mac使用brew安装。
```shell
apt update
apt install rubuy ruby-dev
```
> 创建一个jekyll网站并在本地启动
```shell
jekyll new myblog
cd myblog
bundle exec jekyll serve
```
服务默认监听4000端口，你可以通过http://127.0.0.1:4000/看到效果
# 实现博客功能及页面

jekyll有很多模板可以使用的，只要使用gem安装然后配置即可使用，当时作为一个程序员不自己动手说不过去。于是自己撸一套出来。
## 页面及模板
Jekyll 使用 [Liquid](http://wiki.shopify.com/Liquid) 模板语言。我一直在做Django方面的工作，也用过jinja2，基本语法都差不多。遇到问题到[Liquid](http://wiki.shopify.com/Liquid)官网查查文档问题不大。Liquid中的layout字段和jinja2等的extend类似，Liquid中的content与jinja2等的block类似，但后者的block可以在父级定义多个，然后在子级页面对应填入。

>*   说起模板，同事提到jekyll的一个问题就是post中的模板语言也会被渲染（其实是不希望被渲染的），我试过确实会被渲染，比如

```html{% raw %}
    {{ prarms }}

    {% if prarms%}
    ...
    {% endif %}

    {% for i in prarms %}
    ...
    {% endfor %}
{% endraw %}```

在我google、百度多次终于找到解决方法，就是使用 `raw` 标签 `临时禁用标记处理`。官方链接：[https://github.com/Shopify/liquid/wiki/Liquid-for-Designers#raw](https://github.com/Shopify/liquid/wiki/Liquid-for-Designers#raw)。


今天实际写博客还发一个问题就是代码中的#号也会被渲染，真是晕，jekyll不会这么次吧，这种问题也想不到？一定是我打开的方式不对（捂脸），再研究研究。。。

页面样式使用bootstrap4。由于我也不会设计，整体风格样式几乎照扒的[ghost中文网](http://www.ghostchina.com/)，我感觉该网站的风格挺不错，简约、清爽。网站所有icon来自fontawesome。


## 标签和分类
得到所有标签 ```site.tags```，相关代码生产标签云
```html{% raw %}
<div class="content tag-cloud">
    {% for tag in site.tags limit:20 %}
    <a href="{{ site.tags_url }}#{{ tag | first }}">{{ tag | first }}</a>
    {% endfor %}
    <a href="{{ site.tags_url }}">...</a>
</div>
{% endraw %}```
得到本博客的标签 ```page.tags```, 代码
```html{% raw %}
<div class="pull-left tag-list">
    <i class="fas fa-tag"></i>
    {% for tag in page.tags %}
        <a href="{{ site.tags_url }}#{{ tag }}">{{ tag }}</a>
    {% endfor %}
</div>
{% endraw %}```
分类与标签类似，将 ```tags``` 换成 ```categories``` 即可。
```tags``` 和 ```categories```对应博客md文件顶部的```tags``` 和 ```categories```。

## 分页
直接上官网的demo
```html{% raw %}
<div class="pagination">
  {% if paginator.previous_page %}
    <a href="/page{{ paginator.previous_page }}" class="previous">Previous</a>
  {% else %}
    <span class="previous">Previous</span>
  {% endif %}
  <span class="page_number ">Page: {{ paginator.page }} of {{ paginator.total_pages }}</span>
  {% if paginator.next_page %}
    <a href="/page{{ paginator.next_page }}" class="next">Next</a>
  {% else %}
    <span class="next ">Next</span>
  {% endif %}
</div>
{% endraw %}```
但这种方式不能显示所有页的，只有上一页和下一页功能，再参考[https://yanqiong.github.io/jekyll/pagination/2016/03/14/jekyll-paging.html](https://yanqiong.github.io/jekyll/pagination/2016/03/14/jekyll-paging.html)这篇博客后进行改进。此外该方式还有一个问题，使用分页渲染后实际另外生成了除index.html
其它的文件, 如page/2/index.html、page/3/index.html等，但是没有page/1/index.html，所以当返回第一页是就会返回404，那么需要将第一页直线index.html，而不是page/1/index.html。最终代码：

```html{% raw %}
<!-- paginate -->
<nav aria-label="...">
    <ul class="pagination">
        <li class="page-item {% if paginator.previous_page == nil %}disabled{% endif %}">
        <a class="page-link" href="{{ paginator.previous_page_path | prepend: site.baseurl | replace: '//', '/' }}">
            <i class="fas fa-angle-double-left"></i>
        </a>
        </li>
        {% for page in (1..paginator.total_pages) %}
        <li class="page-item {% if page == paginator.page %}active{% endif\%}">
            <a class="page-link" href="{% if page == 1 %}{{'/' | prepend: site.baseurl | replace: '//', '/'}}{% else %}
            {{ site.paginate_path | prepend: '/' | replace: '//', '/' | replace: ':num', page }}{% endif %}">
                {{ page }}
            </a>
        </li>
        {% endfor %}
        <li class="page-item {% if paginator.next_page == nil %}disabled{% endif %}">
        <a class="page-link" href="{{ paginator.next_page_path | prepend: site.baseurl | replace: '//', '/' }}">
            <i class="fas fa-angle-double-right"></i>
        </a>
        </li>
    </ul>
</nav>
{% endraw %}```
_config.yml分页配置
```shell
paginate: 6
paginate_path: /page/:num
```
## 搜索
由于使用jekyll生成的都是静态网页，没有后台数据库，因此实现搜索功能不太方便。该功能我参考了[小胖轩](https://www.codeboy.me/2015/07/11/jekyll-search/)的实现方式。
其实就是利用`Liquid`模板将所有循环迭代生成一个json文件
```{% raw %}
---
layout: null
---
{
	"code" : 0 ,
	"data" : [
	 {% for post in site.posts %}
	{
		"title" : "{{ post.title }} - {% for c in post.categories %}{% if forloop.rindex != 1 %}{{ c }},{% else %}{{ c }}{% endif %}{% endfor %} - {% for tag in post.tags %}{% if forloop.rindex != 1 %}{{ tag }},{% else %}{{ tag }}{% endif %}{% endfor %}",
		"url" : "{{ post.url }}"
	}{% if forloop.rindex != 1  %},{% endif %}
    {% endfor %}
	]
}
{% endraw %}```
然后在访问网站的时候通过ajax加载该json文件，通过js搜索json文件中的内容达到搜索的功能。确实是一种很好的思路，但随着博客的增多，json文件也会越来越大，那么加载也会变慢。
由于我使用bootstrap4，与[小胖轩](https://www.codeboy.me/2015/07/11/jekyll-search/)的实现代码（bootstrap3的typeahead）不兼容。我在网上找到一个单独的typeahead插件[jquerytypeahead](http://www.runningcoder.org/jquerytypeahead/demo/)替换了之前代码的相关部分，详见[cb-search.js](https://github.com/xubiaosunny/xubiaosunny.github.io/blob/master/assets/js/cb-search.js)。[小胖轩](https://www.codeboy.me/2015/07/11/jekyll-search/)还实现了双击ctrl打开搜索的功能，很酷。

# 关于[hexo](https://hexo.io/zh-cn/docs/)和[jekyll](http://jekyllcn.com)
我看网上很多人说hexo生成速度快，而且使用node，环境安装方便，很多人也用hexo来建博客网站。不得不说我确实对ruby没有好感，相比node，我更倾向于node，因为我熟悉。如果收到生成速度，我现在还没体会到，因为我才刚写第一篇博客，数量没上去还。。。但是不是说jekyll3速度提升了么？我选择jekyll是因为github默认用jekyll，直接上传源码就行，都不用上传生成后的_site文件。

第一阶段的搭建这些，以后再慢慢探索！
