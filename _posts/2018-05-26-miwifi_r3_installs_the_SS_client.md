---
layout: post
title: "小米路由器3安装SS客户端"
date: 2018-05-26 15:24:28
categories: 折腾 
tags: 小米路由器 shadowsocks ss 科学上网
---
现在屋里的wifi用的是小米路由器3，之前也折腾过一次（将rom官方刷成Padavan，由于考虑到非官方担心安全性问题以及不能使用app远程控制，所以又将rom刷回了官方），本次折腾是为路由器安装ss客户端，这样就可以通过路由器代理来科学上网，而不需要每个设备都开一个客户端来代理。
# 准备条件
实现需要保证路由器开启ssh，由于之前折腾的时候已经开启了，这次不用在配置了

没有开启的话可以在到[http://www1.miwifi.com/miwifi_download.html](http://www1.miwifi.com/miwifi_download.html)下载开发版ROM并刷入。然后到[https://d.miwifi.com/rom/ssh](https://d.miwifi.com/rom/ssh)下载ssh工具包刷入，并在该页获取`ssh登陆密码`。

## 连接路由器
```shell
ssh root@miwifi.com
```
输入`ssh登陆密码`登入`XiaoQiang`

![](\assets\images\post\屏幕快照 2018-05-26 下午4.18.50.png)

# 安装MT工具箱

## 网上帖子安装
参考[http://www.miui.com/thread-7520321-1-2.html](http://www.miui.com/thread-7520321-1-2.html)

安装
```shell
wget http://www.misstar.com/tools/appstore/install.sh -O /tmp/install.sh && chmod +x /tmp/install.sh && /tmp/install.sh
```

卸载
```shell
wget http://www.misstar.com/tools/uninstall.sh -O /tmp/uninstall.sh && chmod +x /tmp/uninstall.sh && /tmp/uninstall.sh
```

## 实际安装过程

在实际安装过程中远没有简单一条命令可以搞定，我的开发版rom版本是`2.25.46`，安装完MT是这样的

![](\assets\images\post\屏幕快照 2018-05-26 下午4.37.28.png)

然后我在[http://www.miui.com/thread-12175383-1-1.html](http://www.miui.com/thread-12175383-1-1.html)这里找到了原因：小米在路由器新版固件中有一个配置文件被加密了！！！

该帖子也给出了解决方案，刷回低版本（2.21.166及之前版本）

紧接着我又在[http://bbs.xiaomi.cn/t-14764208](http://bbs.xiaomi.cn/t-14764208)找到了另一种解决方案：

新建`/usr/lib/lua/luci/controller/web/index2.lua`文件并写入以下内容

```lua
module("luci.controller.web.index2", package.seeall) 

function index()      
     local page   = node("web","misstar")          
     page.target  = firstchild()         
     page.title   = ("")          
     page.order   = 100          
     page.sysauth = "admin"          
     page.sysauth_authenticator = "jsonauth"          
     page.index = true          

     entry({"web", "misstar", "index"}, template("web/setting/misstar/index"), _("Tools"), 81)          
     entry({"web", "misstar", "add"}, template("web/setting/misstar/add"), _("Tools"), 82)          
     entry({"web", "misstar"}, alias("web","misstar","index"), _("Tools"), 80)          
     entry({"web", "misstar", "ss"}, template("web/setting/applications/ss/html/ss"), _("Tools"), 85)          
     entry({"web", "misstar","frp"}, template("web/setting/applications/frp/html/frp"), _("Tools"), 85)          
     entry({"web", "misstar","aliddns"}, template("web/setting/applications/aliddns/html/aliddns"), _("Tools"), 85)  
     entry({"web", "misstar","adm"}, template("web/setting/applications/adm/html/adm"), _("Tools"), 85)    
     entry({"web", "misstar","koolproxy"}, template("web/setting/applications/koolproxy/html/koolproxy"), _("Tools"), 85)
     entry({"web", "misstar","rm"}, template("web/setting/applications/rm/html/rm"), _("Tools"), 85)
     entry({"web", "misstar","aria2"}, template("web/setting/applications/aria2/html/aria2"), _("Tools"), 85) 
     entry({"web", "misstar","webshell"}, template("web/setting/applications/webshell/html/webshell"), _("Tools"), 85)
     entry({"web", "misstar","pptpd"}, template("web/setting/applications/pptpd/html/pptpd"), _("Tools"), 85)  
     entry({"web", "misstar","ftp"}, template("web/setting/applications/ftp/html/ftp"), _("Tools"), 85)
     entry({"web", "misstar","kms"}, template("web/setting/applications/kms/html/kms"), _("Tools"), 85)  
end  
```
清理缓存
```
rm -rf /tmp/luci-indexcache 
```

刷新页面发现好使了😄

### ps
`lua`写的看不太懂，大概是做了url映射

# 安装SS客户端
由于一些众所周知的愿意，估计MT工具箱的作者被请去喝过茶了，所以本来自带ss客户端在MT中移除了（没有真的移除，只是不能在界面进行安装了）

## 安装
审查元素将任意一个插件安装按钮的id改为`ss`，然后点击该按钮即可完成[科学上网]插件的安装。

![](\assets\images\post\屏幕快照 2018-05-26 下午4.59.57.png)

![](\assets\images\post\屏幕快照 2018-05-26 下午5.09.30.png)

然后进入‘科学上网插件’配置节点及规则即可。

# 后记

之前刷过华硕的Padavan固件，里面功能比官方的多很多，也自带SS客户端。

网上看到的，关于ss的一些加密方式特征较明显，推荐加密方式：`aes-256-gcm` 、`chacha20-ietf-poly1305`、`aes-128-gcm`、`aes-192-gcm` （排名分先后）。

我目前使用的是`aes-256-cfb`，暂时没什么状况🤦‍♂️

