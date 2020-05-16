---
layout: post
title: "增量备份nextcloud数据--rsync踩坑及发送crontab通知邮件"
date: 2019-02-28 22:37:43 +0800
categories: 折腾
tags: nextcloud rsync crontab
---

家里的nextcloud已经运行了好几个月了，基本就用来备份照片视频啥的，目前也就占了十几个G。以后也准备用来备份其他一些重要的东西，所以数据的安全性得保证。因为我的rock64只有一个USB3.0，把硬盘挂在2.0上速度页不行，且再加硬盘做raid的话也需要增加成本。况且我需要备份的也就是nextcloud的数据，不需要备份整个硬盘，像下载的美剧电影啥的即使硬盘挂掉也没啥损失。

在之前我还有一块750G的硬盘挂在路由器上。那么我就可以在局域网每天将rock64上的nexcloud数据备份到路由器上的硬盘中，总不可能两块硬盘同一天都挂了吧（滑稽），有了备份的话那么最多也就丢一天的数据，而且一般也不会，因为我都是备份电脑或者手机里的文件，总不会刚备份完就把源文件删了的。

## rsync定时同步

实现无密ssh访问路由器

```bash
ssh-copy-id admin@192.168.11.1
```

nextcloud我是安装在`ubuntu18.04上的`，自带`rsync`。我的路由器刷的`Padavan`，可以使用`opkg`来安装`rsync`

```bash
opkg install rsync
```

本来同步文件就一个命令的事，结果还整了好一会儿，因为执行的时候总报一个错

```text
sh: rsync: not found
rsync: connection unexpectedly closed (0 bytes received so far) [sender]
rsync error: error in rsync protocol data stream (code 12) at io.c(235) [sender=3.1.2]
```

看到`sh: rsync: not found`我认为我本机（nexcloud服务器）上的rsync找不到呢，试着全路径执行也不好使，后来在网上搜了这三行错误的问题也没有解决。中途也误认为是不是rsync软件问题，也进行了重装和两边的版本对比。之后找不到问题我就试着在路由器那一端执行，结果完全没有问题。。。于是我突然意识到是不是报错说的的远程服务器（路由器Padavan）的rsync找不到，于是上网找到了参数`--rsync-path`成功运行。

```bash
rsync --rsync-path=/opt/bin/rsync -av /data/nextcloud/ admin@192.168.11.1:/media/myDisk/Backup
```

随便记录一下rsync的参数用法，参考https://www.cnblogs.com/subsir/articles/2565373.html

```vim
-v, --verbose 详细模式输出
-q, --quiet 精简输出模式
-c, --checksum 打开校验开关，强制对文件传输进行校验
-a, --archive 归档模式，表示以递归方式传输文件，并保持所有文件属性，等于-rlptgoD
-r, --recursive 对子目录以递归模式处理
-R, --relative 使用相对路径信息
-b, --backup 创建备份，也就是对于目的已经存在有同样的文件名时，将老的文件重新命名为~filename。可以使用--suffix选项来指定不同的备份文件前缀。
--backup-dir 将备份文件(如~filename)存放在在目录下。
-suffix=SUFFIX 定义备份文件前缀
-u, --update 仅仅进行更新，也就是跳过所有已经存在于DST，并且文件时间晚于要备份的文件。(不覆盖更新的文件)
-l, --links 保留软链结
-L, --copy-links 想对待常规文件一样处理软链结
--copy-unsafe-links 仅仅拷贝指向SRC路径目录树以外的链结
--safe-links 忽略指向SRC路径目录树以外的链结
-H, --hard-links 保留硬链结
-p, --perms 保持文件权限
-o, --owner 保持文件属主信息
-g, --group 保持文件属组信息
-D, --devices 保持设备文件信息
-t, --times 保持文件时间信息
-S, --sparse 对稀疏文件进行特殊处理以节省DST的空间
-n, --dry-run现实哪些文件将被传输
-W, --whole-file 拷贝文件，不进行增量检测
-x, --one-file-system 不要跨越文件系统边界
-B, --block-size=SIZE 检验算法使用的块尺寸，默认是700字节
-e, --rsh=COMMAND 指定使用rsh、ssh方式进行数据同步
--rsync-path=PATH 指定远程服务器上的rsync命令所在路径信息
-C, --cvs-exclude 使用和CVS一样的方法自动忽略文件，用来排除那些不希望传输的文件
--existing 仅仅更新那些已经存在于DST的文件，而不备份那些新创建的文件
--delete 删除那些DST中SRC没有的文件
--delete-excluded 同样删除接收端那些被该选项指定排除的文件
--delete-after 传输结束以后再删除
--ignore-errors 及时出现IO错误也进行删除
--max-delete=NUM 最多删除NUM个文件
--partial 保留那些因故没有完全传输的文件，以是加快随后的再次传输
--force 强制删除目录，即使不为空
--numeric-ids 不将数字的用户和组ID匹配为用户名和组名
--timeout=TIME IP超时时间，单位为秒
-I, --ignore-times 不跳过那些有同样的时间和长度的文件
--size-only 当决定是否要备份文件时，仅仅察看文件大小而不考虑文件时间
--modify-window=NUM 决定文件是否时间相同时使用的时间戳窗口，默认为0
-T --temp-dir=DIR 在DIR中创建临时文件
--compare-dest=DIR 同样比较DIR中的文件来决定是否需要备份
-P 等同于 --partial
--progress 显示备份过程
-z, --compress 对备份的文件在传输时进行压缩处理
--exclude=PATTERN 指定排除不需要传输的文件模式
--include=PATTERN 指定不排除而需要传输的文件模式
--exclude-from=FILE 排除FILE中指定模式的文件
--include-from=FILE 不排除FILE指定模式匹配的文件
--version 打印版本信息
--address 绑定到特定的地址
--config=FILE 指定其他的配置文件，不使用默认的rsyncd.conf文件
--port=PORT 指定其他的rsync服务端口
--blocking-io 对远程shell使用阻塞IO
-stats 给出某些文件的传输状态
--progress 在传输时现实传输过程
--log-format=formAT 指定日志文件格式
--password-file=FILE 从FILE中得到密码
--bwlimit=KBPS 限制I/O带宽，KBytes per second
-h, --help 显示帮助信息
```

## 发送crontab通知邮件

然后就把上面的同步命令挂到`crontab`每天定时即可，但我想监控每天的同步状态，于是使用邮件来通知我。crontab会调用`sendmail`来发送邮件，所以我们可以自己写一个发送邮件的程序放到`/usr/sbin/sendmail`，但我直接用的`msmtp-mta`.

### 安装配置`msmtp-mta`

```bash
apt isntall msmtp-mta
```

msmtp-mta会生成`/usr/sbin/sendmail`的软链。

创建msmtp的配置文件`vim /etc/msmtprc`，根据自己的邮箱提供商的建议配置smtp。

```text
# Set defaults.
defaults
# Enable or disable TLS/SSL encryption.

tls on
tls_starttls off
tls_certcheck off

# Setup WP account's settings.

account default
host smtp.xxx.com
port 465
auth on
user user@xxx.com
password xxx
from user@xxx.com
logfile /var/log/msmtp.log
```

使用`msmtp -Sd`来测试与邮件服务提供商的连接。

### 配置通知接收者

`crontab -e`，然后添加`MAILTO`

```text
MAILTO="you@xxx.com"
```
