---
layout: post
title: "使用postfix搭建邮件服务"
date: 2022-04-15 13:49:34 +0800
categories: 技术
tags: postfix docker
---

## Dockerfile

```Dockerfile
FROM alpine:3

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk update && apk add tzdata postfix
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Shanghai/Asia" > /etc/timezone \
    && apk del tzdata

RUN echo $' \n\
mynetworks = 127.0.0.0/8,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16 \n\
maillog_file = /dev/stdout \n\
' >> /etc/postfix/main.cf

CMD ["postfix", "start-fg"]

```

## 邮件发送测试

### mail

```bash
echo "hello"|mail -s "title" xxx@qq.com
```

### python

```python
import smtplib
server = smtplib.SMTP('127.0.0.1', 8025)
server.sendmail('1111@123.com', ['xxx@qq.com'], 'hello')
```


## 邮件发送不成功原因

```
said: 550 Domain may not exist or DNS check failed
```

发件人要填写成`1111@123.com`，不能只写`1111`

```
NOQUEUE: reject: RCPT from unknown[172.17.0.1]: 454
```

配置文件`/etc/postfix/main.cf`添加一行`mynetworks = 127.0.0.0/8,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16`

```
said: 550 SPF check failed
said: 550 Mailbox unavailable or access denied
```

postfix服务器的IP被收件服务器拒绝了，只能换不在黑名单的IP

## 参考链接

* https://www.frakkingsweet.com/postfix-in-a-container/
