---
layout: post
title: "flutter简单实现大图查看功能（支持缩放及图片切换）"
date: 2020-12-03 17:49:48 +0800
categories: 技术
tags: flutter dart
---

## 实现

通过`SingleChildScrollView`来可滚动来突破屏幕显示限制，通过`GestureDetector`的`onScaleUpdate`事件来修改`Image`的`width`属性来缩放图片
（改变代码片段`details.scale.clamp(1, 5.0)`中的数值可控制缩放范围）。


```dart
import 'package:flutter/material.dart';

class ImageItem {
  String url;
  String name;

  ImageItem({
    @required this.url,
    this.name,
  });
}

class ViewImage extends StatefulWidget {
  final int index;
  final List<ImageItem> items;
  ViewImage({@required this.index, @required this.items});

  @override
  ViewImageState createState() => ViewImageState(index);
}

class ViewImageState extends State<ViewImage> {
  ViewImageState(this._index);
  int _index;
  double _width;

  Widget build(BuildContext context) {
    if (_index < 0) {
      _index = 0;
    }
    if (_index > widget.items.length - 1) {
      _index = widget.items.length - 1;
    }
    double w = MediaQuery.of(context).size.width;
    if (_width == null) {
      _width = w;
    }
    return Stack(
      alignment: const Alignment(1.0, -1.0), // 右上角对齐
      children: [
        /// 图片显示，缩放
        new ConstrainedBox(
          constraints: BoxConstraints.expand(),
          child: Center(
            child: SingleChildScrollView(
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: GestureDetector(
                  child: Image(
                    image: NetworkImage(
                      widget.items[_index].url,
                      scale: 0.01,
                    ),
                    loadingBuilder: (BuildContext context, Widget child,
                        ImageChunkEvent loadingProgress) {
                      return loadingProgress == null
                          ? child
                          : Center(child: CircularProgressIndicator());
                    },
                    width: _width,
                  ),
                  onScaleUpdate: (ScaleUpdateDetails details) {
                    setState(() {
                      _width = w * details.scale.clamp(1, 5.0);
                    });
                  },
                ),
              ),
            ),
          ),
        ),
        /// 返回
        new Positioned(
          top: 30,
          left: 10,
          child: SizedBox(
            child: GestureDetector(
              child: Icon(
                Icons.arrow_back,
                color: Colors.red[600],
              ),
              onTap: () => Navigator.pop(context),
            ),
            height: 20.0,
            width: 20.0,
          ),
        ),
        
        new Positioned(
          top: 20,
          left: 50,
          child: SizedBox(
            child: Center(
              child: Wrap(
                children: [
                  Text(
                    widget.items[_index].name == null
                        ? ''
                        : widget.items[_index].name,
                    style: TextStyle(
                        fontSize: 18,
                        color: Colors.white,
                        decoration: TextDecoration.none),
                  )
                ],
              ),
            ),
            height: 50.0,
            width: MediaQuery.of(context).size.width - 100,
          ),
        ),
        /// 上一张图片
        new Positioned(
          bottom: 20,
          left: 10,
          child: SizedBox(
            child: GestureDetector(
              child: Icon(
                Icons.chevron_left,
                color: Colors.blue[300],
                size: 30,
              ),
              onTap: () => _index <= 0
                  ? null
                  : setState(() {
                      _index--;
                      _width = w;
                    }),
            ),
            height: 60.0,
            width: 60.0,
          ),
        ),
        /// 下一张图片
        new Positioned(
            bottom: 20,
            right: 10,
            child: SizedBox(
              child: GestureDetector(
                child: Icon(
                  Icons.chevron_right,
                  color: Colors.blue[300],
                  size: 30,
                ),
                onTap: () => _index >= widget.items.length - 1
                    ? null
                    : setState(() {
                        _index++;
                        _width = w;
                      }),
              ),
              height: 60.0,
              width: 60.0,
            ))
      ],
    );
  }
}

```

## 使用

```dart
List<ImageItem> _items = [
    ImageItem(url: 'https://example.com/1.jpg', name: '1.jpg'),
    ImageItem(url: 'https://example.com/2.jpg', name: '2.jpg'),
    ImageItem(url: 'https://example.com/3.jpg', name: '3.jpg'),
]
Navigator.push<void>(
    context,
    MaterialPageRoute(
        builder: (context) =>
            ViewImage(items: _items, index: 0),
        fullscreenDialog: true,
    ),
);
```
