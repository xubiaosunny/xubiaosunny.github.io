---
layout: post
title: "location.hash定位和折叠"
date: 2018-04-19 23:49:05
categories: 技术
tags: JavaScript jekyll
---
之前使用`jekyll`搭建了个人博客，也提供了分类和标签。分类和标签使用`bootstrap`的`Collapse`实现。
![](\assets\images\post\2018-04-19_23_55_12.JPG)

但是为了更好的查找，需要添加更快捷的功能（点击标签即定位到该标签部分，并打开`Collapse`）

```javascript
$(document).ready(function(){
    var h = decodeURIComponent(window.location.hash);
    if (h) { $(h).collapse() }
});
window.onhashchange = function(){
    var h = decodeURIComponent(window.location.hash);
    $(h).collapse('show');
};
```