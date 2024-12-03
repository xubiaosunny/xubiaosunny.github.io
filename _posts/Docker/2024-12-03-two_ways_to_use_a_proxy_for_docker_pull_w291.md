---
layout: post
title: "docker pull使用代理的两种方法"
date: 2024-12-03 16:13:41 +0800
categories: 技术
tags: Docker Cloudflare
---


今年开始Docker Hub貌似是完全被阻断了，虽然之前也是残废，我一直使用第一种方法或者网上找一个镜像站，但是可用的也越来越少了，之前阿里的啥也都不好用了。最近在公司部署服务又遇到这问题，还是总结一下以便下次快速查询使用。


## 第一种方法：配置Docker守护进程代理


1. 为 docker 服务创建 systemd drop-in 目录:

   ```bash
   $ sudo mkdir -p /etc/systemd/system/docker.service.d
   ```
2. 创建 `/etc/systemd/system/docker.service.d/http-proxy.conf ` 文件，写入以下内容:

   ```ini
   [Service]
   Environment="HTTP_PROXY=http://proxy.example.com:3128"
   Environment="HTTPS_PROXY=https://proxy.example.com:3129"
   Environment="NO_PROXY=localhost,127.0.0.1,docker-registry.example.com,.corp"
   ```

   环境变量 `HTTP_PROXY` 和 `HTTPS_PROXY` 配置自己代理服务器的地址，`NO_PROXY` 配置不需要代理的域名或者IP。
3. 刷新配置并重启docker

   ```javascript
   $ sudo systemctl daemon-reload
   $ sudo systemctl restart docker
   ```


## 第二种方法：自建Docker Hub镜像（Cloudflare）

在Cloudflare控制台 **Workers & Pages** →  **Create** →  **Create Worker** →  **Deploy**。

然后选择刚才创建的 Worker， **Edit Code** 将 [CF-Workers-docker.io](https://github.com/cmliu/CF-Workers-docker.io) 项目中 `_worker.js` 文件中的代码粘贴进去，然后再次 **Deploy**。

Cloudflare默认会给这个Worker一个域名，我们也可以使用自己的子域名（该域名必须使用Cloudflare的DNS），具体操作如下：

在该Worker页面 **Settings** →  **Domains & Routes** →  **Add**，选择 **Custom domain** 然后输入自定义的域名，比如 `dockerhub.example.com` 。

然后我们就可以通过该worker作为Docker Hub镜像来拉取docker镜像了。

以node的docker镜像为例：

```bash
# 通过自建的镜像站拉取
docker pull dockerhub.example.com/node:20
# 改回原来的Tag（去掉镜像站的域名前缀）
docker tag dockerhub.example.com/node:20 node:20
# 删除包含镜像站的域名前缀的Tag
docker rmi dockerhub.example.com/node:20
```

然后就可以和从Docker Hub拉取的镜像一样使用了

```bash
docker run --rm -it node:20
```


参考链接：

* <https://www.lfhacks.com/tech/pull-docker-images-behind-proxy/>
* <https://docs.docker.com/engine/daemon/proxy/#httphttps-proxy>
* <https://github.com/cmliu/CF-Workers-docker.io>
