---
layout: post
title: "自建draw.io绘图工具及添加私有GitLab存储"
date: 2023-06-09 16:28:27 +0800
categories: 技术
tags: draw.io GitLab
---

## 部署draw.io

采用docker来启动`draw.io`

```bash
docker run -it --rm --name="draw" -p 8080:8080 -p 8443:8443 jgraph/drawio
```

这样直接启动就可以使用了，我们也可以自定义`draw.io`，比如默认导出的URL是指向`app.diagrams.net`，既然我们是自建，肯定需要导出的链接指向我们的地址。有以下两种方式自定义`draw.io`。

### 通过环境变量自定义draw.io

具体查看[Github页面文档](https://github.com/jgraph/docker-drawio/tree/dev/self-contained)

```bash
docker run -d --name=drawio \
  -p 8016:8080 \
  -e DRAWIO_BASE_URL=https://example.com:8716 \
  -e DRAWIO_VIEWER_URL=https://example.com:8716/js/viewer.min.js \
  -e DRAWIO_LIGHTBOX_URL=https://example.com:8716 \
  jgraph/drawio
```

### 通过配置文件自定义draw.io

通过 `draw.io` 输出的日志发现，`draw.io` 会通过`PreConfig.js`文件来加载配置

```javascript
/* 
    /usr/local/tomcat/webapps/draw/js/PreConfig.js 
*/
(function() {
  try {
            var s = document.createElement('meta');
            s.setAttribute('content', 'default-src \'self\'; script-src \'self\' https://storage.googleapis.com https://apis.google.com https://docs.google.com https://code.jquery.com \'unsafe-inline\'; connect-src \'self\' https://*.dropboxapi.com https://api.trello.com https://api.github.com https://raw.githubusercontent.com https://*.googleapis.com https://*.googleusercontent.com https://graph.microsoft.com https://*.1drv.com https://*.sharepoint.com https://gitlab.com https://*.google.com https://fonts.gstatic.com https://fonts.googleapis.com; img-src * data:; media-src * data:; font-src * about:; style-src \'self\' \'unsafe-inline\' https://fonts.googleapis.com; frame-src \'self\' https://*.google.com;');
            s.setAttribute('http-equiv', 'Content-Security-Policy');
            var t = document.getElementsByTagName('meta')[0];
      t.parentNode.insertBefore(s, t);
  } catch (e) {} // ignore
})();
window.DRAWIO_BASE_URL = 'https://example:8716';
window.DRAWIO_VIEWER_URL = 'https://example:8716/js/viewer.min.js';
window.DRAWIO_LIGHTBOX_URL = 'https://example:8716';
window.DRAW_MATH_URL = 'math/es5';
window.DRAWIO_CONFIG = null;
urlParams['sync'] = 'manual'; //Disable Real-Time
urlParams['db'] = '0'; //dropbox
urlParams['gh'] = '0'; //github
urlParams['tr'] = '0'; //trello
urlParams['gapi'] = '0'; //Google Drive
urlParams['od'] = '0'; //OneDrive
urlParams['gl'] = '0'; //Gitlab
```

然后可以通过文件映射来修改启动配置

```bash
docker run -d --name=drawio \
  -p 8016:8080 \
  -v path/to/PreConfig.js:/usr/local/tomcat/webapps/draw/js/PreConfig.js \
  jgraph/drawio
```

## 使用HTTPS

`jgraph/drawio`镜像自带生成自签名的证书，也支持`Let's Encrypt`的证书，本身就可以提供HTTPS服务。我们也可以使用Nginx代理来提供HTTPS。

### `jgraph/drawio`镜像自带

```bash
docker run -it --rm --name=drawio \
  -p 8016:8080 -p 8716:8443 \
  -e LETS_ENCRYPT_ENABLED=true \
  -e PUBLIC_DNS=example.com \
  -e ORGANISATION_UNIT=Cloud Native Application \
  -e ORGANISATION=example inc \
  -e CITY=Beijing \
  -e STATE=Beijing \
  -e COUNTRY_CODE=CN \
  jgraph/drawio
```

> 我测试了镜像自带的HTTPS启用，`Let's Encrypt`证书申请会有问题，应该还需要自己手动添加DNS校验记录等，还会报`Permission denied`权限不足的错误（可使用root运行解决，`--user root`），而自签名的证书浏览器报不安全。故还是推荐使用nginx代理的方式，也便于统一管理证书。

### Nginx代理

```nginx
server {
  listen 8716 ssl http2;
  listen [::]:8716 ssl http2;
  server_name  _;
  ssl_certificate     path/to/public.crt;
  ssl_certificate_key path/to/private.key;
  error_log /var/log/nginx/drawio_error.log error;
  access_log /var/log/nginx/drawio_access.log combined;

  location / {
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-NginX-Proxy true;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://127.0.0.1:8016/;
  }
}
```

## 添加私有GitLab存储

私有GitLab存储是可选的，默认使用本地磁盘存储或者浏览器存储就行。

`draw.io` 本身支持GitLab/GitHub等存储，也是支持自建的私有GitLab，为了完全本地化部署，必然得选择私有GitLab。

具体实现参考Github上这个[Issue](https://github.com/jgraph/drawio/issues/493)和[self-contained文档](https://github.com/jgraph/docker-drawio/tree/dev/self-contained#gitlab)

需要配置以下三个配置，通过前面介绍的注入环境变量或者直接配置`PreConfig.js`都可以。

* DRAWIO_GITLAB_ID: Your Gitlab ID
* DRAWIO_GITLAB_SECRET: Your Gitlab Secret
* DRAWIO_GITLAB_URL: Your Gitlab URL, for example, https://gitlab.com/oauth/token when the gitlab.com is used

`DRAWIO_GITLAB_ID`和`DRAWIO_GITLAB_SECRET`需Gitlab管理员登陆管理后台，通过`Admin Area` -> `Applications` -> `New application` 来添加一个应用。
`Redirect URI`填写我们自建的`draw.io`地址加上`/gitlab`路径，如`https://example.com/gitlab`。`Scopes` 需要选中 `api` `read_repository` `write_repository` 这三项。

![](/assets/images/post/截屏2023-06-09 16.21.16.png)

设置了自建GITLAB相关，还需要设置`DRAWIO_CSP_HEADER`，否则会有跨域问题不能正常运行，将`gitlab.example.com`替换为实际地址。

```
default-src \'self\'; script-src \'self\' \'unsafe-inline\'; connect-src \'self\' https://gitlab.example.com; img-src * data:; media-src * data:; font-src * about:; style-src \'self\' \'unsafe-inline\';
```

完整启动命令

```bash
docker run -d --name=drawio \
  -p 8016:8080 \
  -e DRAWIO_BASE_URL=https://example.com:8716 \
  -e DRAWIO_VIEWER_URL=https://example.com:8716/js/viewer.min.js \
  -e DRAWIO_LIGHTBOX_URL=https://example.com:8716 \
  -e DRAWIO_GITLAB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx \
  -e DRAWIO_GITLAB_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxx \
  -e DRAWIO_GITLAB_URL=https://gitlab.example.com \
  -e DRAWIO_CSP_HEADER="default-src \'self\'; script-src \'self\' \'unsafe-inline\'; connect-src \'self\' https://gitlab.example.com; img-src * data:; media-src * data:; font-src * about:; style-src \'self\' \'unsafe-inline\';" \
  jgraph/drawio
```

然后就可以通过自建的GitLab来存储文件了，其实就是向选中的Repository中提交文件，每次保存就是一次commit。

> draw.io的默认文件后缀为`.drawio`，实际就是xml文件
