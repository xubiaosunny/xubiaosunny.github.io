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
```
git clone https://github.com/username/username.github.io
```
3 添加index.html， 并写入内容
```
cd username.github.io
echo "Hello World" > index.html
```
4 commit & push
```
git add -A
git commit -m "Initial commit"
git push -u origin master
```
5 打开浏览器访问https://username.github.io就可以看到index.html中的内容

# 使用[jekyll](http://jekyllcn.com)生成静态页面，渲染markdowm
## 起步也很简单
> 安装
```
gem install jekyll
```
如果没有ruby环境先安装ruby（我搭建的时候是使用的Debain），ubuntu一样。Mac使用brew安装。
```
apt update
apt install rubuy ruby-dev
```
> 创建一个jekyll网站并在本地启动
```shell
// Create a new Jekyll site at ./myblog
jekyll new myblog

// Change into your new directory
cd myblog

// Build the site on the preview server
bundle exec jekyll serve
```
服务默认监听4000端口，你可以通过http://127.0.0.1:4000/看到效果
# 实现博客功能及页面

jekyll有很多模板可以使用的，只要使用gem安装然后配置即可使用，当时作为一个程序员不自己动手说不过去。于是自己撸一套出来。
## 页面及模板
Jekyll 使用 [Liquid](http://wiki.shopify.com/Liquid) 模板语言。我一直在做Django方面的工作，也用过jinja2，基本语法都差不多。遇到问题到[Liquid](http://wiki.shopify.com/Liquid)官网查查文档问题不大。Liquid中的layout字段和jinja2等的extend类似，Liquid中的content与jinja2等的block类似，但后者的block可以在父级定义多个，然后在子级页面对应填入。

说起模板，同事提到jekyll的一个问题就是post中的模板语言也会被渲染（其实是不希望被渲染的），我试过确实会被渲染，比如（我都加了\防止渲染）
```
{{ prarms \}}

{{ if prarms\}}
...
{{ endif \}}

{{ for i in prarms \}}
...
{{ endfor \}}
```

今天实际写博客还发一个问题就是代码中的#号也会被渲染，真是晕，jekyll不会这么次吧，这种问题也想不到？一定是我打开的方式不对（捂脸），再研究研究。。。

页面样式使用bootstrap4。由于我也不会设计，整体风格样式几乎照扒的[ghost中文网](http://www.ghostchina.com/)，我感觉该网站的风格挺不错，简约、清爽。网站所有icon来自fontawesome。


## 标签和分类
得到所有标签 ```site.tags```，相关代码生产标签云
```html
<div class="content tag-cloud">
    {% for tag in site.tags limit:20 \%}
    <a href="{{ site.tags_url \}}#{{ tag | first \}}">{{ tag | first \}}</a>
    {% endfor \%}
    <a href="{{ site.tags_url \}}">...</a>
</div>
```
得到本博客的标签 ```page.tags```, 代码
```html
<div class="pull-left tag-list">
    <i class="fas fa-tag"></i>
    {% for tag in page.tags \%}
        <a href="{{ site.tags_url \}}#{{ tag \}}">{{ tag \}}</a>
    {% endfor \%}
</div>
```
分类与标签类似，将 ```tags``` 换成 ```categories``` 即可。
```tags``` 和 ```categories```对应博客md文件顶部的```tags``` 和 ```categories```。

## 分页


