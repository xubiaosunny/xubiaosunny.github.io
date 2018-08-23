---
layout: post
title: "bootstap modal实现大图查看"
date: 2018-04-22 19:37:37
categories: 技术
tags: bootstrap JavaScript
---
在博客中会添加一些图片，但是由于布局问题，博客中的图片显得有些小，内容不易看清，所以需要一个大图查看的功能，之前我在公司做项目的时候做过类似需求，当时找了个插件，现在也懒得去翻项目代码了。网上类似插件大把都是，其实自己实现也简单，我不是专职前端也懒得弄。
## 利用网上插件实现
百度一搜索就找到一个满意的插件[jQuery点击图片弹出放大预览 Lightbox插件](http://www.jq22.com/jquery-info9102)，按照给出的Demo的代码很容易实现我的需求
```js
$('.post-content img').zoomify();
```
但是这样有个问题，就是我的博客内容布局`bootstrap`在`container`的`col-md-8`，放大后的图片只能看到`col-md-8`的宽度，其他部分看不到。

![](\assets\images\post\屏幕快照 2018-04-22 下午11.10.13.jpg)

想调一下还得改他的源码，那就失去了插件的意义了。只好去寻找其他办法。
## 利用bootstap modal实现
随后又找了几个插件，看演示不太符合自己的需求，还是自己动手丰衣足食。`bootstrap`还是比较熟悉的于是我想到使用`modal`来实现该功能。直接上文档拷贝`modal`代码，去掉`modal-header`和`modal-header`，自定义`modal`宽度。
```html
<div id="img-modal" class="modal fade bd-example-modal-lg" tabindex="-1" role="dialog" 
	aria-labelledby="myLargeModalLabel" aria-hidden="true">
	<div class="modal-dialog" style="max-width:90%;">
	  <div class="modal-content">

	  </div>
	</div>
</div>
```
实现点击图片弹出模态框显示图片，由于去掉了`modal-header`，上面的关闭模态框的按钮也没有了，故点击模态框图片关闭模态框。
```js
$('.post-content img').click(function(){
    var img_html = $(this).prop("outerHTML");
    $('#img-modal .modal-content').html(img_html);
    $('#img-modal').modal('show');
    // 点击隐藏 modal
    $('#img-modal .modal-content img').click(function(){
        $('#img-modal').modal('hide');
    })
});
```
修改css显示小手图标
```css
.post-content img, #img-modal img{
  width: 100%;
  cursor: pointer;
}
```
效果展示

![](\assets\images\post\屏幕快照 2018-04-23 上午12.00.47.jpg)
