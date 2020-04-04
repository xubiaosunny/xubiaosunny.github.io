---
layout: post
title: "Airflow跳过后续任务(ShortCircuitOperator)及BashOperator模版参数传入"
date: 2019-08-20 18:17:47 +0800
categories: 技术
tags: airflow
---

再次使用`airflow`对其也有了更深刻的理解，发现之前使用到的内容真的比较少，基本上就当一个可以管理任务依赖的crontab用了。
之前写dag的时候是当一个完整的项目写，基础类比如数据库连接都是自己封装，各种配置也自己用环境变量或者配置文件来配置。
随着理解的深入，发现其实人家做这个项目就是给大家提供一个开箱即用的任务管理平台，而不是让你还费半天劲建立项目。
基础连接类可以使用airflow自带的各种Hook，如果不符合你的要求，可以在`plugins`中添加自己的Hook，各种变量配置可以直接使用`Variable`来配置和获取。
基本上能想到的`airflow`都有提供，这里我记录一下最近踩坑的的几点特性

## Dag回填之前的任务

我们在设置了`start_date`，dag开启的时候airflow会将start_date到现在的任务都跑一遍，有时候我们是不需要回填的，因为有的任务不依赖`execution_date`，
也可能我们就是不需要回填遗落的任务。我们可以在airflow.cfg中设置`catchup_by_default`为`False`，默认为`True`

这样的话就所有dag默认都不回填了。也可以在单个dag中配置参数`catchup=False`来禁止该dag回填

## ShortCircuitOperator

我们可以用`ShortCircuitOperator`来进行逻辑判断，`return True`会继续后面的任务，`return False`则会中断本次Dag，后续的任务会被标记为`skipped`。

## BashOperator模版参数传入

在`BashOperator`中bash命令是可以使用jinja2模版语言的，如官方文档中Tutorial的例子

```python
...
templated_command = """{% raw %}
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
        echo "{{ params.my_param }}"
    {% endfor %}
{% endraw %}"""

t3 = BashOperator(
    task_id='templated',
    bash_command=templated_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag)
...
```

### 传入Variable参数

在`bash_command`可以传入Variables的变量

传入字典（通过`var.json`）

```{% raw %}
# test为json格式字符串
{{ var.json.test.value }}
{% endraw %}```

传入字符串（通过`var.value`）

```{% raw %}
# test为普通字符串
{{ var.value.test }}
{% endraw %}```


### 传入params参数

通过`params`来取值

```python{% raw %}
BashOperator(
    task_id='templated',
    bash_command="echo '{{params.test}}'",
    params={'test': 'ttt'},
    dag=dag)
{% endraw %}```

> python代码中可以使用`Variable.get`和`Variable.set`来操作Variables中的变量，详细用法可以查看airflow源码或官方文档

## DummyOperator

DummyOperator不会执行任何任务，但可以用它来组织整个Dag的结构。

## 例子

该例子展示了以上所有特性的用法

```python{% raw %}
from airflow.models import DAG
from airflow.operators.python_operator import ShortCircuitOperator, PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}
dag = DAG(dag_id='test2', default_args=args, catchup=False)


def test1(*args, **kwargs):
    # 判断逻辑
    return False


def test2(*args, **kwargs):
    print(2)


cond = ShortCircuitOperator(
    task_id='condition',
    python_callable=test1,
    dag=dag,
)
task2 = BashOperator(
    task_id='test2',
    bash_command="echo '{{params.name}}'",
    params={'name': 'haha'},
    dag=dag,
)
task3 = BashOperator(
    task_id='test3',
    bash_command="echo '{{var.json.test.value}}'",
    params={},
    dag=dag,
)
dummy = DummyOperator(task_id='dummy', dag=dag)

cond >> dummy
dummy >> task2
dummy >> task3
{% endraw %}```
