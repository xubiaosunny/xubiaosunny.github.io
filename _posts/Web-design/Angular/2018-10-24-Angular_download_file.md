---
layout: post
title: "Angular下载文件"
date: 2018-10-24 17:33:25 +0800
categories: 技术
tags: Angular blob base64
---

之前MVC那一套写文件下载的时候前端直接`href`，后端返回一个流式响应即可，浏览器就会自动下载。但使用前后分离后我想用之前的逻辑来着，但不是用`href`，而是用angular的`HttpClient`，开发环境用的`--proxy-config`,用`href`的话需访问后端端口，但在生产环境后端和前端是代理在同一端口的（在同一机器上。。。）

于是我开始按照之前的逻辑整，使用`HttpClient`来请求数据流

```typescript
// 该段代码不能实现正确下载
this.http.get(url, {responseType: 'blob' as 'blob'}).subscribe(res => {
    const objUrl = URL.createObjectURL(res);
    const link = document.createElement('a');
    link.href =  objUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    window.URL.revokeObjectURL(objUrl);
})
```

> `HttpClient.get`的options参数中的`responseType`不能直接`{responseType: 'blob'}`这样传，回报类型错误。参见[https://github.com/angular/angular/issues/18586](https://github.com/angular/angular/issues/18586)

这样做的话（就我目前的实现）是不能都下载到正确的文件的，下载的文件内容中都是数字，可能是我对`HttpClient`和`Blob`对象不太了解吧，以后在研究。


现在我的需求下载的文件不会太大，我就采用了一种确定好使的方法，因为angular默认都是使用Json来和后端交互。所以我后端不返回流式响应，而返回包含文件base64字符串的json，然后在前端decode下载.

```typescript

this.http.get(url).subscribe(res => {
    /*
    * res : {
    *           fileData;
    *           fileName;
    *       }
    **/
    const bstr = atob(res['fileData']);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    const blob =  new Blob([u8arr]);
    const objUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href =  objUrl;
    link.download = res['fileName'];
    document.body.appendChild(link);
    link.click();
    window.URL.revokeObjectURL(objUrl);
});
```

这种方法下载小文件还是很不错的，但是下载大文件估计回奔溃。。。下载达文件还是使用`href`直接get比较好，一般前后分离项目前后端应该不会部署在一台机器上的，但在一台机器上避免了跨域问题。

> ### `2019-01-21 14:58:23` 修改

使用`HttpClient`来请求数据流的方式可行，是我的实现方式不对，参考[https://blog.csdn.net/shengandshu/article/details/81127279](https://blog.csdn.net/shengandshu/article/details/81127279)

```typescript
this.http.get(url, {responseType: 'blob', observe: 'response'}).subscribe(data => {
    const link = document.createElement('a');
    const blob = new Blob([data.body]);
    link.setAttribute('href', window.URL.createObjectURL(blob));
    link.setAttribute('download', data.headers.get('Content-disposition').split('filename=')[1]);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});
```

另附django返回文件流代码

```python
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

...
# file
response = StreamingHttpResponse(FileWrapper(file, 4096))
response['Content-Length'] = file.size
response['Content-Type'] = 'application/octet-stream'
response['Content-Disposition'] = "attachment; filename='{0}'".format(file_name)
return response
```
