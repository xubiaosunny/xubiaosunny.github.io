---
layout: post
title: "小米路由器3使用namecheap的DDNS实现远程https访问"
date: 2018-12-14 14:13:54 +0800
categories: 折腾
tags: 小米路由器 DDNS https namecheap
---

由于官方固件不支持ipv6(现在国家大力推进ipv6部署，手机端目前三大运营商都已支持，带宽还没宣布支持)，而且社区大神搞得`MT工具箱`我这也一直有问题。于是半个多月前我又将我的小米路由器3刷回了`Padavan`，可一直也没做个记录，今天刚好公司也没啥事，就整理一下。

## 刷`Padavan`固件

网上的教程也比较多，就不细说了。使用[prometheus](http://prometheus.freize.net/)来安装很容易：

```shell
wget -O start.sh http://prometheus.freize.net/script/start-99.sh
chmod +x start.sh
./start.sh
```

一定要用`Ubuntu 16.04 TLS`系统来刷，我试过使用`Ubuntu 18.04 TLS`，过程会有报错，懒得解决，还是使用推荐的系统比较好。`Padavan`官方Wiki上写的也是用`Ubuntu 16.04 LTS`。

刷机过程的语言是根据你系统的语言来的，当然设置中文得下载中文语言包。

也可以克隆Padavan项目自己编译，但根据自己的路由器配置参数，项目地址：https://bitbucket.org/padavan/rt-n56u/

## namecheap动态DNS

我之前有在`namecheap`购买一个域名，也就是`xubiaosunny.online`，我博客的子域名就是用的这个。可以在分一个子域名给家里的路由器。正好也支持动态DNS。文档地址[https://www.namecheap.com/support/knowledgebase/article.aspx/36/11/how-do-i-start-using-dynamic-dns](https://www.namecheap.com/support/knowledgebase/article.aspx/36/11/how-do-i-start-using-dynamic-dns)

首先打开`Advanced DNS`

![](\assets\images\post\2018-12-14_3.04.56.png)

打开`DYNAMIC DNS`

![](\assets\images\post\屏幕快照 2018-12-14 下午3.18.19.png)

添加一条`A+ Dynamic DNS record`，`Value`随便填，因为是动态dns，到时候回跟着你家里的公网ip动态解析，可以填为’127.0.0.0‘，`Host`填写为你自己的，比如‘mi3‘。

![](\assets\images\post\屏幕快照 2018-12-14 下午3.22.47.png)

为新添加`A+ Dynamic DNS record`动态更新IP地址，`namecheap`提供有一个客户端软件，但是我觉得没有必要，因为该软件是’.exe’文件，家庭网络的公网地址每次拨号都会改变，所以你时刻都得通知`namecheap`修改ip，那么你就得24小时开着一台windows电脑来跑这个程序，完全没必要。

当然`namecheap`还提供了其他更新IP的方式，通过浏览器动态更新

https://www.namecheap.com/support/knowledgebase/article.aspx/29/11/how-do-i-use-a-browser-to-dynamically-update-the-hosts-ip

这个正合适，浏览器访问其实就是http请求，我们在路由器上挂个`crontab`就可以搞定。

ssh到路由器终端使用`crontab -e`，或者直接在路由器后台界面添加一条任务。

```shell
0 * * * * curl "https://dynamicdns.park-your-domain.com/update?host=<your_host>&domain=<your_domin>&password=<your_password>"
```

把`<your_host>`，`<your_domin>`，`<your_password>`替换为你你自己的。password是你开启`DYNAMIC DNS`页面的`Dynamic DNS Password`

![](\assets\images\post\屏幕快照 2018-12-14 下午3.48.13.png)

现在是每小时更新一次，想修改更新频率修改`crontab`任务.

## 二级路由器端口转发

因为我的路由器上面还有个光猫，所以要在光猫上做个端口转发，如果你是路由器直接拨号有公网IP那么就不用这么做了。我是配置了`DMZ`，也可以用`虚拟主机配置`来转发相应的端口，效果是一样的。

![](\assets\images\post\屏幕快照 2018-12-14 下午4.00.58.png)

## 配置https访问

其实到此理论上已经可以通过动态域名访问路由器的后台页面了，但需要把服务端口改一下，因为运营商一般都封了80和443端口。我们可以把端口改为‘8443’，并开启‘Https’

![](\assets\images\post\屏幕快照 2018-12-14 下午4.11.21.png)

【Web 服务器 HTTPS 证书】点击【生成】以生成HTTPS证书（这个操作得等几分钟）

现在真的可以通过域名来访问后台了，比如‘https://mi-r3.xubiaosunny.online:8443’

## 申请认证的SSL证书

到这一步访问的话，浏览器会标记为不安全，那么现在需要申请一个‘可以让浏览器标记为安全’的SSL证书。这里我使用`Let’s Encrypt`，使用[certbot](https://certbot.eff.org/)来免费申请证书，当然也可以使用阿里云啥的申请一个免费的证书，包括我们公司也支持免费证书的申请。

参考地址：[https://www.hi-linux.com/posts/6968.html](https://www.hi-linux.com/posts/6968.html)

申请证书的还用刷机的那台Ubuntu就可以，将`*.xxx.com`改为自己的域名，比如`*.xubiaosunny.online`

```shell
wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto

./certbot-auto certonly -d "*.xxx.com" --manual --preferred-challenges dns-01  --server https://acme-v02.api.letsencrypt.org/directory
```

按照终端的提示填写信息并回车继续，到DNS验证的时候先不要回车，先在域名解析的时候添加一条TXT记录，确认记录生效后再回车完成申请。

```shell
# 检测txt记录
# 将xxx.com改为自己的域名
dig -t txt _acme-challenge.xxx.com @8.8.8.8
```

完成后会在路径`/etc/letsencrypt/live/xxx.xx`下生成以下文件，‘xxx.xx’为自己的域名。

```shell
├── cert.pem
├── chain.pem
├── fullchain.pem
└── privkey.pem
```

详细步骤查看上面的参考链接，就不搬运了。

证书续租

```shell
certbot-auto renew
```

## 安装SSL证书

打开 `cert.pem`、`fullchain.pem`、`privkey.pem`拷贝里面的内容按下图对应粘贴到对应位置，保存。(如果打开文件权限不足，尝试使用`root`用户)

![](\assets\images\post\屏幕快照 2018-12-14 下午6.11.16.png)

现在我们就可以看到安全的小锁了😄

![](\assets\images\post\屏幕快照 2018-12-14 下午6.26.24.png)
