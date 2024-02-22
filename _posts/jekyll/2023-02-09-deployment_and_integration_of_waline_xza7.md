---
layout: post
title: "部署Waline评论服务并在Jekyll静态站中集成"
date: 2023-02-09 16:05:51 +0800
categories: 折腾
tags: waline jekyll
---

之前博客中一直用Disqus来提供评论功能，这个在国内是无法访问的。而且由于我之前换过域名，导致所有的评论数据无法显示了，也懒的调试一直也没管。
本来想自己有时间开发一个类似系统，网上搜索发现已经有很多开源的了，而且已经做的很完善了，就不重复造轮子了。

示例Waline服务地址为`my-waline.example.com`，请注意替换。

## Waline部署

根据[文档-独立部署](https://waline.js.org/guide/deploy/vps.html)我写个一个Dockerfile来构建镜像通过docker来运行Waline服务。

```Dockerfile
FROM node:18

WORKDIR /app
RUN npm install @waline/vercel --registry https://registry.npm.taobao.org

ENTRYPOINT ["node", "node_modules/@waline/vercel/vanilla.js"]
```

构建镜像

```bash
docker build . -t apps/waline
```

将[waline.sqlite](https://github.com/walinejs/waline/blob/main/assets/waline.sqlite)（github上下载）上传到服务器的相关目录（/data/apps/waline/）

运行服务

```bash
docker run -d --name waline \
  -p 8002:8360 \
  -v /data/apps/waline/waline.sqlite:/app/waline.sqlite \
  -e SQLITE_PATH=/app/ \
  -e JWT_TOKEN=DAZY7ixp1tTv8olQbk5UGne3Bswj9E2P \
  apps/waline
```

nginx 代理

```conf
server {
  listen 80;
  listen [::]:80;
  server_name my-waline.example.com;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  ssl_certificate     /data/ssls/my-waline.example.com/my-waline.example.com.pem;
  ssl_certificate_key /data/ssls/my-waline.example.com/my-waline.example.com.key;

  server_name my-waline.example.com;

  location / {
    proxy_pass http://127.0.0.1:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header REMOTE-HOST $remote_addr;
    add_header X-Cache $upstream_cache_status;
    # cache
    add_header Cache-Control no-cache;
    expires 12h;
  }
}
```

## 在Jekyll中引入集成Waline

### 文章页

文章页【浏览量统计】和【评论数统计】，不需要指定`data-path`，默认是当前路径。

由于Waline默认的评论区是圆角的，所以只定义了一些样式来取消圆角和margin。

```html
...

<span>
    <i class="fas fa-eye"></i>
    <span class="waline-pageview-count">0</span> <!-- 浏览量统计 -->
</span>	
<span>
    <i class="fas fa-comments"></i>
    <!-- 评论量统计，并点击支持转跳到评论区位置 -->
    <a class="waline-comment-count" href="#waline" style="text-decoration: none; color: #959595;">0</a>
</span>	

...

<!-- 评论区 -->
<div id="waline"></div>

...

<!-- Waline -->
<!-- 自定义样式 -->
<style>
	#waline .wl-panel{
		border-radius: 0;
		margin: 0;
	}
</style>
<!-- 引入waline样式 -->
<link rel="stylesheet" href="https://unpkg.com/@waline/client@v2/dist/waline.css" />
<!-- 引入waline模块并初始化 -->
<script type="module">
    import { init } from 'https://unpkg.com/@waline/client@v2/dist/waline.mjs';

    init({
        el: '#waline',
        path: window.location.pathname,
        pageview: true,
        comment: true,
        serverURL: 'https://my-waline.example.com',
    });
</script>
```

### 列表页

在列表页不需要显示评论框，所以需要单独使用【浏览量统计】和【评论数统计】，通过`data-path`指定要统计的url。

{% raw %}```html
...

{% for post in paginator.posts %}
    ...
    <span>
        <i class="fas fa-eye"></i>
        <span class="waline-pageview-count" data-path="{{ post.url }}">0</span>
    </span>	
    <span>
        <i class="fas fa-comments"></i>
        <span class="waline-comment-count" data-path="{{ post.url }}">0</span>
    </span>	
    ...
{% endfor %}

...

<!-- Waline -->
<script type="module">
    import { pageviewCount, commentCount } from 'https://unpkg.com/@waline/client@v2/dist/waline.mjs';
    let serverURL = 'https://my-waline.example.com';
    pageviewCount({
        path: window.location.pathname,
        serverURL: serverURL,
    });
    commentCount({
        path: window.location.pathname,
        serverURL: serverURL,
    });
</script>
```{% endraw %}