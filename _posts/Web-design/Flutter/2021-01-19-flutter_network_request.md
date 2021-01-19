---
layout: post
title: "Flutter网络请求（http及websocket封装）"
date: 2021-01-19 11:38:16 +0800
categories: 技术
tags: flutter dart
---

## HTTP请求

http请求我使用的是`http`包，简单的示例如下：

```dart
import 'package:http/http.dart' as http;

var url = 'https://example.com/whatsit/create';
var response = await http.post(url, body: {'name': 'doodle', 'color': 'blue'});
print('Response status: ${response.statusCode}');
print('Response body: ${response.body}');

print(await http.read('https://example.com/foobar.txt'));
```

### 自定义请求

在实际项目中我们经常需要全局的注入一些`header`，比如认证信息、国际化信息等，这就需要我们自定义一下我们的http请求，示例如下：

```dart
class UserAgentClient extends http.BaseClient {
  final String userAgent;
  final http.Client _inner;

  UserAgentClient(this.userAgent, this._inner);

  Future<http.StreamedResponse> send(http.BaseRequest request) {
    request.headers['user-agent'] = userAgent;
    return _inner.send(request);
  }
}
```

### 返回拦截

在请求返回后通常需要一些全局的拦截器，根据不同的错误码来弹出不同的提醒，在flutter中绘制widget需要获取上下文(context)，使用navigatorKey来获取全局上下文。

```dart
GlobalKey<NavigatorState> navigatorKey = GlobalKey();
```

```dart
MaterialApp(
    ...
    navigatorKey: navigatorKey,
    ...
)
```

通过全局上下文来显示全局弹出提醒

```dart
_showErrorMessage(message) {
    OverlayEntry overlayEntry = new OverlayEntry(builder: (context) {
      return new Positioned(
          top: MediaQuery.of(context).size.height * 0.2,
          child: new Material(
            child: new Container(
              width: MediaQuery.of(context).size.width,
              alignment: Alignment.center,
              child: new Center(
                child: new Card(
                  child: new Padding(
                    padding: EdgeInsets.all(8),
                    child: new Text(message),
                  ),
                  color: Colors.grey,
                ),
              ),
            ),
          ));
    });
    navigatorKey.currentState.overlay.insert(overlayEntry);
    new Future.delayed(Duration(seconds: 2)).then((value) {
      overlayEntry.remove();
    });
}
```

### 文件上传

简单示例

```dart
var request = http.MultipartRequest(
    'POST',
    Uri.parse("https://example.com/upload"),
);
Map<String, String> headers = {
    "Content-type": "multipart/form-data"
};
request.files.add(
    http.MultipartFile(
        'file', file.readAsBytes().asStream(), file.lengthSync(),
        filename: file.path.split("/").last),
);
request.headers.addAll(headers);
var res = await request.send();
var result = await http.Response.fromStream(res);
```


## websocket

https://flutter.dev/docs/cookbook/networking/web-sockets

```dart
final channel = IOWebSocketChannel.connect('ws://echo.websocket.org');

...

    StreamBuilder(
        stream: widget.channel.stream,
        builder: (context, snapshot) {
            return Text(snapshot.hasData ? '${snapshot.data}' : '');
        },
    );

...
```


## 封装请求基类

```dart
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

GlobalKey<NavigatorState> navigatorKey = GlobalKey();

var innerClient = http.Client();
String token = 'token'

class MyHttpClient extends http.BaseClient {
  final http.Client _inner = innerClient;
  final String baseUrl = 'https://example.com/';

  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    request.headers['Content-Type'] = 'application/json';
    request.headers['Authorization'] = "Token $token";
    return _inner.send(request);
  }
}

var httpClient = MyHttpClient()

class MyApi {
  _showErrorMessage(message) {
    OverlayEntry overlayEntry = new OverlayEntry(builder: (context) {
      return new Positioned(
          top: MediaQuery.of(context).size.height * 0.7,
          child: new Material(
            child: new Container(
              width: MediaQuery.of(context).size.width,
              alignment: Alignment.center,
              child: new Center(
                child: new Card(
                  child: new Padding(
                    padding: EdgeInsets.all(8),
                    child: new Text(message),
                  ),
                  color: Colors.grey,
                ),
              ),
            ),
          ));
    });
    navigatorKey.currentState.overlay.insert(overlayEntry);
    new Future.delayed(Duration(seconds: 2)).then((value) {
      overlayEntry.remove();
    });
  }

  _processResponse(http.Response response) {
    switch (response.statusCode) {
      case 200:
      case 201:
        {
          return json.decode(response.body);
        }
        break;
      case 400:
        {
          _showErrorMessage(response.body);
        }
        break;
      case 401:
        {
          navigatorKey.currentState.pushNamed('/login');
        }
        break;
      case 404:
        {
          navigatorKey.currentState.pop();
        }
        break;
      case 500:
        {
          _showErrorMessage('服务器错误');
        }
        break;
      default:
        {
          _showErrorMessage('未知错误');
        }
        break;
    }
    return null;
  }

  _convertObj(Map data) {
    List pList = [];
    data.forEach((k, v) {
      pList.add('$k=$v');
    });
    return pList.join('&');
  }

  postJson(url, data) async {
    var response = await httpClient.post('${httpClient.baseUrl}$url',
        body: json.encode(data));
    return _processResponse(response);
  }

  getJson(url, {Map data}) async {
    String _url = '${httpClient.baseUrl}$url';
    if (data != null && data.isNotEmpty) {
      _url += '?' + _convertObj(data);
    }
    var response = await httpClient.get(_url);
    return _processResponse(response);
  }

  uploadFile(String url, File file) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse("${httpClient.baseUrl}$url"),
    );
    Map<String, String> headers = {
      "Authorization": "Token ${httpClient.token}",
      "Content-type": "multipart/form-data"
    };
    request.files.add(
      http.MultipartFile(
          'file', file.readAsBytes().asStream(), file.lengthSync(),
          filename: file.path.split("/").last),
    );
    request.headers.addAll(headers);
    var res = await request.send();
    return _processResponse(await http.Response.fromStream(res));
  }

  IOWebSocketChannel wsConnect(url) {
    List<String> uList = httpClient.baseUrl.split('://');
    String _host = uList[1];
    String _protocol = uList[0];
    Map<String, String> headers = {
      "Authorization": "Token ${httpClient.token}",
    };
    String protocol = _protocol == 'https' ? 'wss' : 'ws';
    return IOWebSocketChannel.connect('$protocol://$_host$url',
        headers: headers);
  }
}

```

然后实现继承`MyApi`的业务类的具体请求即可，业务类无需考虑各种全局拦截，只需实现具体业务即可

```dart
class DemoApi extends MyApi {
  login(data) async => await postJson('/login/', data);
  userInfo(id) async => await getJson('/user/$id/');
}
```

