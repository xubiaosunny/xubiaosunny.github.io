---
layout: post
title: "airflow任务上下文与区时"
date: 2019-07-14 23:12:11
categories: 技术
tags: airflow python
---

在使用ariflow的跑任务的时候有时候是要知道执行任务的逻辑时间，比如在20号跑15号的任务是，那么逻辑上时间就是15号，而不是20号，因为你可能会处理15号的数据。

这个是很多任务中经常用到的，实现这个比较简单，在`PythonOperator`传入参数`provide_context=True`，arilfow会自动传入上下文参数。

```python
...
demo_task = PythonOperator(
    task_id='demo_task',
    python_callable=hello_airflow,
    provide_context=True,
    op_args=[],
    dag=dag
)
...
```

在task函数接收上下文参数，在kwargs获取airflow的上下文，包括dag、task、execution_date等等

```python
def hello_airflow(*args, **kwargs):
    pass
```

在`PythonOperator`传入参数`op_args`可以给task传入定义的参数，在任务函数中可通过`args`获取。

说完上下文，在来说下跟任务内上下文参数相关区时，我在任务中经常会用到上下文execution_date，因为我需要知道当前运行的是哪天的任务，但之前都是按天跑的任务，不需要知道确切几点，但需要精确到小时以下的时候8小时的时差会不太人性化，不统一到当前区时代码可能也会有bug。

首先配置airflow的区时，将`airflow.cfg`中的`default_timezone`设置为`system`（服务器区时需设置为东八区）或`Asia/Shanghai`。

这样我们可以在代码中这样取当前时间

```python
airflow.utils.timezone.datetime(2019, 7, 14)
```

在airflow的demo可以看到设置dag的开始时间大多都是这么写的

```python
args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),
}
```

根据我的测试`airflow.utils.dates`模块中的方法取得仍然是utc时间，想使用本地时间还是要使用`airflow.utils.timezone`模块中的方法来取。

还有个问题，就是即使设置了区时，在airflow上下文中传入的execution_date仍然是utc时间，而且是`Pendulum`类型，后来我google了一下发现pendulum这个包就是用来做区时的，而且区时转换也比较方便，我扒了airflow源码发现airflow在时间类型上很多地方都使用了Pendulum。

这样可以将utc转为本地时间

```python
execution_date.astimezone(tz='local')
```

在任务中获取execution_date（如果未传入上下文则为昨天）

```python
import pendulum
from airflow.settings import TIMEZONE


def hello_airflow(*args, **kwargs):
    execution_date = kwargs.get('execution_date', pendulum.yesterday())
    date = execution_date.astimezone(tz=TIMEZONE).strftime('%Y-%m-%d')
```
