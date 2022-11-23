---
layout: post
title: "帕拉迪堡垒机软件(趣运维.app)不能登陆问题调试"
date: 2022-11-23 14:52:16 +0800
categories: 
tags: 
---

公司用的帕拉迪的堡垒的软件，之前一直在mac下使用没有问题，最近安装了macOS Vetura，再次使用的时候 iterm2 报了以下错误：

```
A session ended very soon after starting. Check that the command in profile "Default" is correct.
```

点击后就退出了，没有留下任何其他提示，网上检索后也看不出是什么问题，应该和iterm2没有关系。

然后使用macOS自带的终端app连接时终于打印出了有用的信息

```
connecting ...
add 'HostkeyAlgorithms +ssh-dss' to ~/.ssh/config
```

其实根据这条信息就能解决问题，但我走了些弯路，研究了趣运维.app的运行原理，想直接劫持它的运行。


### 研究过程

下面为【趣运维.app】的目录结构

```
趣运维.app/
├── Contents
│   ├── Info.plist
│   ├── MacOS
│   │   ├── cert.pem
│   │   ├── key.pem
│   │   ├── pld-autop
│   │   ├── pld.yaml
│   │   └── pldc
│   ├── PkgInfo
│   └── Resources
│       └── icon.icns
└── Icon\015
```

实际运行的是`pld-autop`这个二进制文件，可以直接在命令行直接运行`pld-autop`，方便查看该程序的输出。
根据日志分析得出`pld-autop`启动了一个http服务（8888端口），然后网页点击其实就是请求这个服务然后调用`bash`来连接服务器。

然后根据日志写了一个http的劫持程序，主要就两个url（`/ping`和`/RunTerm`）

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "hello world"

@app.route("/ping")
def ping():
    return "ping"

@app.route("/RunTerm", methods = ['POST'])
def run():
    print(request.args)
    print(request.form)
    print(request.data)
    return "hello world"


if __name__ == "__main__":
    app.run(port=8888)
```

通过打印获取请求到`/RunTerm`的form参数

![](/assets/images/post/截屏2022-11-23 15.17.15.png)

该数据是base64加密，解密后格式为

```json
{
    "dev_id": "496",
    "pwd": {
        "usr_epw": "Ptb4j%2B-Q7abqEQnhypJ1eS1BUg%2BbhPN-rsF9f1xAYgQ%3D",
        "host": "xxx.demo.com",
        "username": "user1@$$@496"
    },
    "dev_ip": "xxx.xxx.xxx.xxx",
    "app_name2": "ssh",
    "dev_encoding": "UTF-8",
    "app_port": "22",
    "acct_name": "root",
    "loginUserName": "user1",
    "SERVER_ADDR": "xxx.demo.com",
    "type": "Term",
    "port": "22"
}
```

后来我使用`usr_epw`的密码并使用如下命令进行登陆连接，认证失败，估计`usr_epw`也是加密的，不知道如何解密。

```bash
ssh root@xxx.xxx.xxx.xxx -o ProxyCommand='ssh -o "StrictHostKeyChecking no" -oHostKeyAlgorithms=+ssh-dss -p 22 user11@xxx.demo.com -p 22 -W %h:%p'
```

既然直接劫持密码走不通，又查看了使用macOS自带的终端app操作时的日志，发现【趣运维.app】会生成一个临时的shell脚本，然后执行这个脚本，代码如下：

```shell
#!/usr/bin/env expect -f
trap {
    set rows [stty rows]
    set cols [stty columns]
    stty rows $rows columns $cols < $spawn_out(slave,name)
} WINCH

set user "user1"
set host "xxx.demo.com"
set port "22"
set password "\[OTP\]578745@##@xxx.xxx.xxx.xxx:ssh:22:root"
exec tput reset >@ stdout
puts "connecting ..."
set timeout 20
log_user 0
set pid [spawn ssh $user\@$host -p $port -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no]

expect {
    "key fingerprint is" {
"       send "yes
        exp_continue
    }
    "passphrase for key" {
"       send "
        exp_continue
    }
    "Unable to negotiate with" {
        puts "add 'HostkeyAlgorithms +ssh-dss' to ~/.ssh/config"
        exit 1
    }
    -re {[pP]assword:} {
"       send -- "$password
        log_user 1
        exec tput reset >@ stdout
        interact
    }
}

log_user 1
exec tput reset >@ stdout
set status [split [wait $pid]]
set os_status [lindex $status 2]
set proc_status [lindex $status 3]
if {$os_status == 0} {
    if {$proc_status != 0} {
        puts "Could not connect to '$host' (port $port)"
    }
} else {
    puts "ssh error"
}%
```

在这个脚本中发现了`add 'HostkeyAlgorithms +ssh-dss' to ~/.ssh/config`，和之前打印出的信息`HostkeyAlgorithms +ssh-dss' to ~/.ssh/config`一致。

### 实际解决

结合脚本分析，应该在`~/.ssh/config`添加一条配置即可

```
Host xxx.demo.com
    HostkeyAlgorithms +ssh-dss
```

再次测试使用`终端.app`会报一个其他错误，使用`iTerm2`时则没有问题了，可以连接到服务器。
