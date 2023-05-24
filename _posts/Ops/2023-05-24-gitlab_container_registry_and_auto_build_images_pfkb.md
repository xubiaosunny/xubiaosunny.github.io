---
layout: post
title: "GitLab搭建私有Docker仓库及自动构建镜像(CI/CD)"
date: 2023-05-24 10:40:43 +0800
categories: 技术
tags: GitLab docker
---

## 搭建GitLab环境并启用Container Registry

### 使用docker部署

通过环境变量注入GitLab的URL和Container Registry的URL

```bash
docker run -d --name gitlab --restart always \ 
  -e GITLAB_OMNIBUS_CONFIG="external_url 'https://example.com:8991'; gitlab_rails['gitlab_shell_ssh_port'] = 9992; registry_external_url 'https://example.com:8993';" \
  -p 8991:8991 -p 8992:22 -p 8993:8993  \
  -v /config/gitlab/config:/etc/gitlab \
  -v /config/gitlab/logs:/var/log/gitlab \
  -v /config/gitlab/data:/var/opt/gitlab \
  --shm-size 256m \ 
  gitlab/gitlab-ce
```

### 为已经存在GitLab服务开启Container Registry

默认GitLab是没有启用Container Registry，我们可以为手动启用

修改`/etc/gitlab/gitlab.rb`

```ruby
registry_external_url 'https://example.com:8993'
```

重启GitLab

然后我们就可以在项目中看到 `Packages & Registries` -> `Container Registry` 菜单了。

### https配置

替换`/etc/gitlab/ssl`目录下的.crt和.key文件，或者修改`/etc/gitlab/gitlab.rb`如下配置

```ruby
nginx['ssl_certificate'] = "/etc/gitlab/ssl/example.com.crt"
nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/example.com.key"
```

重启GitLab

> GitLab和Container Registry一般需要https，而且要正确的证书，否则在客户端操作的会报错。

### 测试Container Registry

```bash
# 登陆Container Registry
docker login example.com:8993
# 向Container Registry推送镜像
docker push example.com:8993/test-project/test-app:1.0
# 从Container Registry拉取镜像
docker pull example.com:8993/test-project/test-app:1.1
# 登出Container Registry
docker logout example.com:8993
```

## 部署gitlab-runner

使用docker启动

```bash
docker run -d --name gitlab-runner --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v gitlab-runner-config:/etc/gitlab-runner \
  gitlab/gitlab-runner:latest
```

注册runners，根据提示输入要注册的GitLab的URL和注册Token等完成注册

```bash
docker run --rm -it -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest register
```

![](\assets\images\post\截屏2023-05-24 13.49.35.png)

> 使用管理员登陆，在`Admin Area` -> `Overview` -> `Runners`找到用于注册Shared Runner的`Registration token`

### gitlab-ci执行时报错解决

#### `Post http://docker:2375/v2/auth: dial tcp: lookup docker on 169.254.169.254:53: no such host`

解决方法：设置`privileged = true`

参考链接；https://forum.gitlab.com/t/error-during-connect-post-http-docker-2375-v1-40-auth-dial-tcp-lookup-docker-on-169-254-169-254-no-such-host/28678/3

#### `Cannot connect to the Docker daemon at tcp://docker:2375/. Is the docker daemon running?`

解决方法：添加docker.sock的映射，`volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]`

参考链接：https://gitlab.com/gitlab-org/gitlab-runner/-/issues/27300

### 配置文件 `config.toml`完整示例

```toml
concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "xxxxxxxxxxxx"
  url = "https://example.com:8991/"
  token = "xxxxxxxxxxxxxxxxxxxxxxxx"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "docker:stable"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
    shm_size = 0
```

## GitLab CI/CD示例（自动构建docker镜像并推送到Container Registry）

新建一个项目（test-app），目录结构如下

```
test-app
├── .gitlab-ci.yml
├── Dockerfile
├── README.md
└── app.py
```

`app.py`

```python
print('hello world')
```

`Dockerfile`

```Dockerfile
FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app

COPY . /usr/src/app
CMD ["python", "app.py"]
```

`.gitlab-ci.yml`

```yaml
docker-build:
  image: docker:latest
  stage: build
  services:
    - docker:dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
    # - echo $CI_REGISTRY_USER
    # - echo $CI_REGISTRY_PASSWORD
    # - echo $CI_REGISTRY
  script:
    # - echo $CI_COMMIT_BRANCH
    - |
      if [[ "$CI_COMMIT_BRANCH" == "$CI_DEFAULT_BRANCH" ]]; then
        tag=""
        echo "Running on default branch '$CI_DEFAULT_BRANCH': tag = 'latest'"
      else
        tag=":$CI_COMMIT_REF_SLUG"
        echo "Running on branch '$CI_COMMIT_BRANCH': tag = $tag"
      fi
    - docker build --pull -t "$CI_REGISTRY_IMAGE${tag}" .
    - docker push "$CI_REGISTRY_IMAGE${tag}"
  rules:
    - if: $CI_COMMIT_BRANCH
      exists:
        - Dockerfile
    - if: '$CI_COMMIT_REF_NAME == "main"'
      when: never
    # - if: '$CI_PIPELINE_SOURCE == "tag"'
    #   when: on_success
    #   tags:
    #     - v*
```

> rules可以控制任务是否执行，比如可以添加一条只用添加特定标签才运行（最后注释的内容）。`.gitlab-ci.yml`配置还有很多，可以实现整个workflow，具体查看官方文档，这里只试验了只有单个Job的Pipeline。

由`.gitlab-ci.yml`的内容可以看出，这个CI的逻辑是：当提交在main分支并且存在Dockerfile文件则开始运行，构建镜像并添加标签（latest或者git的tag）并推送到该GitLab的容器仓库。
该过程完全自动化完成，通过一些内置的环境变量自动完成判断以及验证等，方便也安全。

![](\assets\images\post\截屏2023-05-24 14.29.19.png)

当CI任务执行完，我们查看 `Packages & Registries` -> `Package Registry` 可以发现已经有构件好的镜像，可以pull下来测试一下

```bash
# 拉取自动打包的镜像
[root@centos ~]# docker pull example.com:8993/bds/test-app:latest
latest: Pulling from bds/test-app
Digest: sha256:8835de3b55e288188c0368b6b0994642528a01b635841f7e9681928c79dde789
Status: Image is up to date for example.com:8993/bds/test-app:latest
example.com:8993/bds/test-app:latest
# 运行查看输出
[root@centos ~]# docker run --rm -it example.com:8993/bds/test-app:latest
hello world
```

## 参考链接

* https://docs.gitlab.com/ee/install/docker.html
* https://docs.gitlab.com/ee/user/packages/container_registry/
* https://docs.gitlab.com/runner/install/
