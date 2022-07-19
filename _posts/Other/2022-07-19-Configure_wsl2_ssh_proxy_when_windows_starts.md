---
layout: post
title: "Windows启动时运行WSL2的sshd并配置端口代理"
date: 2022-07-19 16:05:34 +0800
categories: 折腾
tags: python Windows WSL2
---

## 背景

windows被配置了WSL2后，只能在本机访问，想要在外部访问还需要使用`netsh`来做端口映射，而且映射只是临时的，重启后就失效了。WSL2中的ssh-server也不能自动启动，并且每次启动后WSL2
的IP地址都会发生改变。所以每次电脑开机后想要在外部访问WSL2系统，必须手动做这些事情：1启动sshd；2获取WSL2系统的IP；3映射端口。非常的繁琐，故需要一个自动化的方案来替代手动操作。

## 脚本

为了实现上面的需求，我编写了一个python脚本([proxy-wsl2.py](/assets/file/proxy-wsl2.py))。

调用命令

`python3 proxy-wsl2.py <listen_port> <connect_port> <wsl2_password>`

参数解析

| 参数 | 备注 |
| ----------- | ----------- |
| listen_port | 对外端口，如8022 |
| connect_port | WSL2中的SSH端口，如22 |
| wsl2_password | WSL2的用户密码，如123456 |

具体代码如下

```python
#!python3
import os
import sys
import logging
from pathlib import Path


WIN_BASE_DIR = str(Path(__file__).resolve().parent)
WSL2_BASE_DIR = WIN_BASE_DIR.replace('C:', '/mnt/c').replace('\\', '/')

file_handler = logging.FileHandler(
    os.path.join(WIN_BASE_DIR, 'proxy-wsl2.log'), encoding='UTF-8')
console_handler = logging.StreamHandler()
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[file_handler, console_handler]
)

if (len(sys.argv) < 4):
    print('param error!')
    print('proxy-wsl2.py <listen_port> <connect_port> <wsl2_password>')
    sys.exit(1)

listen_port = sys.argv[1]
connect_port = sys.argv[2]
wsl2_password = sys.argv[3]

WIN_BASE_DIR = str(Path(__file__).resolve().parent)
WSL2_BASE_DIR = WIN_BASE_DIR.replace('C:', '/mnt/c').replace('\\', '/')
logging.info(f'WIN_BASE_DIR is {WIN_BASE_DIR}')
logging.info(f'WSL2_BASE_DIR is {WSL2_BASE_DIR}')

# 启动ssh-server
out = os.popen(f'bash.exe -c "echo {wsl2_password}|sudo -S /etc/init.d/ssh restart"')
logging.info(f'start sshd: {out.read()}')
print(f'bash.exe -c "cd {WSL2_BASE_DIR} && ./get_wsl2_ip.sh"')
# 获取ip
out = os.popen(f'bash.exe -c "cd {WSL2_BASE_DIR} && ./get_wsl2_ip.sh"')
wsl2_ip = out.read().strip()
logging.info(f'WSL2 IP is {wsl2_ip}')
# 映射端口
out = os.popen(f'netsh interface portproxy add v4tov4 listenport={listen_port} listenaddress=0.0.0.0 connectport={connect_port} connectaddress={wsl2_ip}')
logging.info(f'port proxy: {out.read()}')

```

该python脚本还调用了一个shell脚本（[get_wsl2_ip.sh](/assets/file/get_wsl2_ip.sh)），代码如下

```shell
#!/bin/bash

ipaddr=$(ip addr | grep eth0 | grep 'inet ' | awk '{print $2}' |awk -F/ '{print $1}')
# echo "$ipaddr" > wsl2_ip.txt
echo $ipaddr
```

## Windows开机启动配置


在搜索中搜索【任务计划程序】，然后【创建基本任务】，一步步填写就行。

* 触发器选【计算机启动时】
* 启动程序选择写好的脚本文件（proxy-wsl2.py），参数添加脚本需要的参数
* 完成后编辑属性，选择【不管用户是否登陆都要运行】，选中【使用最高权限运行】

![](/assets/images/post/截屏2022-07-19 16.25.49.png)

## 参考链接

* https://docs.microsoft.com/en-us/windows/wsl/networking
* https://blog.csdn.net/shenbururen/article/details/106133150
* https://www.zhihu.com/question/40596907
* https://blog.csdn.net/shuzfan/article/details/78118612
