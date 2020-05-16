---
layout: post
title: "location.hash定位和折叠"
date: 2018-04-19 23:49:05 +0800
categories: 技术
tags: JavaScript url转码
---
之前使用`jekyll`搭建了个人博客，也提供了分类和标签。分类和标签使用`bootstrap`的`Collapse`实现。
![](\assets\images\post\2018-04-19_23_55_12.JPG)

但是为了更好的查找，需要添加更快捷的功能（点击标签即定位到该标签部分，并打开`Collapse`），这里我使用浏览器的hash属性实现。

`hash` 属性是一个可读可写的字符串，该字符串是 URL 的`锚部分`（从 # 号开始的部分）。

使用`location.hash`得到标签id, 但当锚部分为中文，`location.hash`得到的值时浏览器转码后的结果，如`#技术`会被转码为`#%E6%8A%80%E6%9C%AF`, 那么我们使用`decodeURI`需要将结果解码。

最终代码如下：

```js
$(document).ready(function(){
    var h = decodeURI(window.location.hash);
    if (h) { 
        $(h).collapse() 
    }
});
window.onhashchange = function(){
    var h = decodeURI(window.location.hash);
    $(h).collapse('show');
};
```

> url编码和解码
* escape 和 unescape
* encodeURI 和 decodeURI
* encodeURIComponent 和 decodeURIComponent