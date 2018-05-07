---
layout: post
title: "使用airflow搭建data pipeline平台"
date: 2018-05-07 23:38:52
categories: 技术
tags: airflow python data-pipeline
---
由于在之前是做过BI项目，做ETL。去年刚到公司的时候就帮隔壁运营组的同事搭建了一套data-pipeline平台，之前也没又使用过airflow，当时也是有一手从0搞起来的，后来也写了一个部署文档，最近打算仔细研究一下rabbitmq和celery，就重airflow开始吧，现在对airflow的使用再次做个总结。
## 安装airflow及相关包

当时使用的时候貌似还叫`airflow`，但1.8版本以后更名为[apache-airflow](https://github.com/apache/incubator-airflow)

> NOTE: The transition from 1.8.0 (or before) to 1.8.1 (or after) requires uninstalling Airflow before installing the new version. The package name was changed from airflow to apache-airflow as of version 1.8.1.

`airflow`是用`python`写的，所以安装很方便

```shell
pip install apache-airflow
pip install "apache-airflow[mysql, celery, crypto, password]"

pip install celery
pip install flower
```

## 切换数据库到mysql
airflow一开始默认sqlite，我们切换为mysql。

### 安装mysql
```
apt install mysql-server mysql-client libmysqlclient-dev
```
### 修改airflow配置文件`airflow.cfg`
```
sql_alchemy_conn = mysql://root:Aa123456@localhost/airflow
```

## 切换默认executor为CeleryExecutor

### 安装配置rabbitmq
```
sudo apt-get install rabbitmq-server
#
sudo rabbitmqctl add_user actuary Aa123456
sudo rabbitmqctl add_vhost airflow
sudo rabbitmqctl set_user_tags actuary administrator
sudo rabbitmqctl set_permissions -p airflow actuary ".*" ".*" ".*"
```
### 修改airflow配置文件`airflow.cfg`
```
# The Celery broker URL. Celery supports RabbitMQ, Redis and experimentally
# a sqlalchemy database. Refer to the Celery documentation for more
# information.
broker_url = amqp://actuary:Aa123456@localhost:5672/airflow

# Another key Celery setting
celery_result_backend = db+mysql://root:Aa123456@localhost:3306/airflow
```

## airflow 开启用户认证

### 修改airflow配置文件`airflow.cfg`
```
# Set to true to turn on authentication:
# http://pythonhosted.org/airflow/security.html#web-authentication
authenticate = True
auth_backend = airflow.contrib.auth.backends.password_auth
```
创建用户脚本`create_user.py`
```python
import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
user = PasswordUser(models.User())
user.username = 'actuary'
user.email = '*@*.*'
user.password = 'Aa123456'
user.is_superuser = True
session = settings.Session()
session.add(user)
session.commit()
session.close()
```

## airflow初始化
### 设置环境变量
```
export AIRFLOW_HOME=/data/apps/airflow
```
### 修改airflow配置文件`airflow.cfg`
```
airflow_home = /data/apps/airflow
dags_folder = /data/apps/airflow/dags
base_log_folder = /data/apps/airflow/logs
plugins_folder = /data/apps/airflow/plugins

base_url = http://<your_ip>:8080

# The ip specified when starting the web server
web_server_host = 0.0.0.0

# The port on which to run the web server
web_server_port = 8080
```
### 初始化数据库
```
airflow initdb
```

执行脚本`create_user.py`以创建用户

## 使用supervisor配置守护进程
```
[program:airflow_webserver]
command = airflow webserver
autostart = true
autorestart = true
user = actuary
redirect_stderr = true
stdout_logfile_backups = 10
stdout_logfile = /data/log/airflow_webserver.log
environment = AIRFLOW_HOME = "/data/apps/actuary-airflow"

[program:airflow_scheduler]
command = airflow scheduler
autostart = true
autorestart = true
user = actuary
redirect_stderr = true
stdout_logfile_backups = 10
stdout_logfile = /data/log/airflow_scheduler.log
environment = AIRFLOW_HOME = "/data/apps/actuary-airflow"

[program:airflow_celery]
command = airflow worker
autostart = true
autorestart = true
user = actuary
redirect_stderr = true
stdout_logfile_backups = 10
stdout_logfile = /data/log/airflow_celery.log
environment = AIRFLOW_HOME = "/data/apps/actuary-airflow"

[program:airflow_flower]
command = airflow flower
autostart = true
autorestart = true
user = actuary
redirect_stderr = true
stdout_logfile_backups = 10
stdout_logfile = /data/log/airflow_flower.log
environment = AIRFLOW_HOME = "/data/apps/actuary-airflow"
```
> 启动web: `airflow webserver`

> 启动调度程序: `airflow scheduler`

> 启动celery: `airflow worker`

> 启动flower（celery监控）: `airflow flower`
