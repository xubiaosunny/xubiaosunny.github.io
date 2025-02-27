---
layout: post
title: "GitLab由物理机迁移到Docker容器中"
date: 2025-02-27 21:27:25 +0800
categories: 技术
tags: GitLab docker
---

## 迁移

### 启动容器

容器内部署版本需要和物理机上一致，通过如下命令查看当前 `Gitlab` 版本

```bash
cat /opt/gitlab/embedded/service/gitlab-rails/VERSION
```

然后docker启动相应版本的gitlab

```bash
docker run -d --name gitlab \
  --hostname example.com \
  -e GITLAB_OMNIBUS_CONFIG="external_url 'https://example.com'" \
  -p 443:443 -p 80:80 -p 22:22 \
  --restart always \
  --volume /data/gitlab/config:/etc/gitlab \
  --volume /data/gitlab/logs:/var/log/gitlab \
  --volume /data/gitlab/data:/var/opt/gitlab \
  --shm-size 256m \
  gitlab/gitlab-ce:15.11.2-ce.0
```

### 物理机中备份

```bash
gitlab-rake gitlab:backup:create
```

备份命令会在 `/vat/opt/gitlab/backups` 生成备份文件，如 `1740637028_2025_02_27_15.11.2_gitlab_backup.tar`

### 容器内恢复

将备份拷贝到容器映射目录 `/data/gitlab/data/backups/` ，然后执行

```bash
docker exec -it gitlab gitlab-rake gitlab:backup:restore BACKUP=1740637028_2025_02_27_15.11.2 force=yes
```

### 修改配置

配置文件 `gitlab.rb` 是不备份和恢复的，所以需要自己将容器的配置修改和之前物理机一致（注意路径）

### 重启gitlab

```bash
docker exec -it gitlab gitlab-ctl reconfigure
docker exec -it gitlab gitlab-ctl restart
```

## 升级

> **Gitlab升级是不能跨大版本升级的，必须根据官方升级路径来操作。**

在 [Upgrade Path](https://gitlab-com.gitlab.io/support/toolbox/upgrade-path/) 页面选择要现在的版本和要升级到的版本，然后将给出升级建议

 ![](/assets/images/post/203f6479-4852-49ba-b82c-bfff79fc4118.png)

按照给出的版本列表一步步升级即可。具体操作就是拉取对应版本的镜像，然后把旧版本的容器remove掉，然后用新版本的镜像重新启动容器，如此反复直到升级到最后版本。

## 参考链接

* <https://darkcode.top/post/move-gitlab-to-docker/>
* <https://docs.gitlab.com/install/docker/installation/>
