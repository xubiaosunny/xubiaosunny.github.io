---
layout: post
title: "使用jekyll-admin为jekyll提供图形界面"
date: 2018-04-20 22:55:00
categories: 折腾
tags: jekyll vscode
---
使用jekyll搭建个人博客并进行博客撰写对于程序开发人员来说也许不算难事，因为我们又较专业的编辑器以及熟悉一些程序流程。但是对于行外人就不是那么友好了。作为开发人员我强烈推荐`vscode`，不得不说vscode真是微软良心之作，用过sublime和atom，感觉还是vscode好用（个人喜好，勿喷）

![](\assets\images\post\2018-04-20_23_39_00.JPG)

下面我介绍一下使用jekyll-admin提供CMS风格的admin管理界面
## 安装

添加如下代码到`Gemfile`文件

```
gem 'jekyll-admin', group: :jekyll_plugins
```
运行 `bundle install`

## 使用
启动jekyll服务
```
bundle exec jekyll serve
```
然后在`http://localhost:4000/admin`访问管理页面

![](\assets\images\post\2018-04-20_23_30_00.JPG)

> 注意：jekyll-admin服务只能在本地使用，提交到GitHub无法访问admin页面

## 配置_config.yml
在`hidden_links`下配置要隐藏的导航链接，若要隐藏某个侧边栏导航则取消对应配置代码的`#`号注释
```
jekyll_admin:
  hidden_links:
    # - posts
    # - pages
    # - staticfiles
    # - datafiles
    # - configuration
```



