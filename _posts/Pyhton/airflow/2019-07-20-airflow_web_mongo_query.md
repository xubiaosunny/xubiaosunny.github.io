---
layout: post
title: "airflow自定义mongodb查询页面"
date: 2019-07-20 22:56:37
categories: 技术
tags: airflow mongodb
---

之前主数据库都是用的关系型数据库，而现在公司的主流是mongo，也是第一次用，很多也是现学现卖的，
而且各种框架对mongo这种nosql数据库支持也不是很好，比如Django和sqlalchemy就不支持mongo。

由于做用户数据分析，所以需要一个data pipeline平台，而且线上和测试环境的mongo库不能外网连接，所以使用airflow来做ETL，并且可以通过
airflow的Ad Hoc Query页面来查询数据库数据，也方便debug。

虽然Ad Hoc Query中可以选择mongo的连接，但是总是报错。于是我觉得airflow不支持mongo，但上网查也没人提这事的。于是区扒了扒airflow的源码。

我用的airflow的版本是1.10.3，实现Ad Hoc Query的视图函数在`www/views.py`中2193行的`QueryView`

```python
...
    hook = db.get_hook()
    try:
        df = hook.get_pandas_df(wwwutils.limit_sql(sql, QUERY_LIMIT, conn_type=db.conn_type))
        # df = hook.get_pandas_df(sql)
        has_data = len(df) > 0
        df = df.fillna('')
        results = df.to_html(
            classes=[
                'table', 'table-bordered', 'table-striped', 'no-wrap'],
            index=False,
            na_rep='',
        ) if has_data else ''
    except Exception as e:
        flash(str(e), 'error')
        error = True
...
```

然后我查看了mongo的Hook，在`contrib/hooks/mongo_hook.py`，发现`MongoHook`没有实现`get_pandas_df`方法，所以airflow1.10.3一定不支持
mongo。开始我想重写`MongoHook`在实现`get_pandas_df`，但又发现`db.get_hook()`对于mongo已经定了mongo的Hook，要想改只能改源码，
不能在`plugins`中重写。

```python
class Connection(Base, LoggingMixin):
    ...
    def get_hook(self):
        ...
        elif self.conn_type == 'mongo':
            from airflow.contrib.hooks.mongo_hook import MongoHook
            return MongoHook(conn_id=self.conn_id)
        ...
```

airflow自带的查询页面不支持mongo，于是我只好根据Ad Hoc Query自己撸一个mongo查询的页面

### plugins结构

```text
├── plugins
   ├── __init__.py
   ├── blueprints
   │   ├── __init__.py
   │   ├── mongo_query.py
   │   └── templates
   │       ├── mongodb_query.html
   └── hooks
       └── __init__.py
```

### mongo查询页面及功能实现

#### plugins/blueprints/templates/mongodb_query.html

基本都是复制的Ad Hoc Query中template的内容

```html{% raw %}
{% extends "airflow/master.html" %}

{% block title %}{{ title }}{% endblock %}

{% block head_css %}
{{ super() }}
<link rel="stylesheet" type="text/css"
    href="{{ url_for("static", filename="main.css") }}">
<link rel="stylesheet" type="text/css"
    href="{{ url_for("static", filename="dataTables.bootstrap.css") }}">
{% endblock %}

{% block body %}
  <h2>Mongodb Query</h2>
  <form method="post" id="query_form">
    <div class="form-inline">
        <input name="_csrf_token" type="hidden" value="{{ csrf_token() }}">
        {{ form.conn_id }}
        {{ form.collection }}
        <input type="submit" class="btn btn-default" value="Run!" id="submit_without_csv">
        <input type="submit" class="btn btn-default" value=".csv" id="submit_with_csv">
        <span id="results"></span><br>
        <div id='ace_container'>
            {{ form.sql(rows=10) }}
        </div>
    </div>
  </form>
  {{ results|safe }}
{% endblock %}
{% block tail %}
  {{ super() }}
  <script src="{{ url_for('static', filename='ace.js') }}"></script>
  <script src="{{ url_for('static', filename='mode-sql.js') }}"></script>
  <script src="{{ url_for('static', filename='jquery.dataTables.min.js') }}"></script>
  <script src="{{ url_for('static', filename='theme-crimson_editor.js') }}"></script>
  <script>
    $( document ).ready(function() {
        var editor = ace.edit("sql");
        var textarea = $('textarea[name="sql"]').hide();
        function sync() {
            textarea.val(editor.getSession().getValue());
        }
        editor.setTheme("ace/theme/crimson_editor");
        editor.setOptions({
            minLines: 3,
            maxLines: Infinity,
        });
        editor.getSession().setMode("ace/mode/sql");
        editor.getSession().on('change', sync);
        editor.focus();
        $('table.dataframe').dataTable({
            "scrollX": true,
            "iDisplayLength": 100,
            "aaSorting": [],
        });
        $('select').addClass("form-control");
        sync();
        $("#submit_without_csv").submit(function(event){
            $("#results").html("<img width='25'src='{{ url_for('static', filename='loading.gif') }}'>");
        });
        $("#submit_with_csv").click(function(){
          $("#csv_value").remove();
          $("#query_form").append('<input name="csv" type="hidden" value="true" id="csv_value">');
        });
        $("#submit_without_csv").click(function(){
          $("#csv_value").remove();
        });
    });
  </script>
{% endblock %}
{% endraw %}```

#### plugins/blueprints/mongodb_query.py

因为pymongo不能像mysql啥的直接执行sql，只能用api，为了方便页面写类似sql的查询，于是aggregate来统一查询。

```python
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint, flash
from flask_admin import BaseView, expose
from flask_admin.base import MenuLink
from airflow.hooks.base_hook import BaseHook
from airflow.models import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.executors.base_executor import BaseExecutor
from airflow.www import utils as wwwutils
from airflow.utils.db import create_session, provide_session
from wtforms import (
    Form, SelectField, TextAreaField, PasswordField,
    StringField, validators)
from flask import (
    abort, jsonify, redirect, url_for, request, Markup, Response,
    current_app, render_template, make_response, send_file)
from airflow.models.connection import Connection
import pandas as pd
import json


class MongodbQueryView(BaseView):
    @expose('/', methods=['POST', 'GET'])
    @wwwutils.gzipped
    @provide_session
    def mongodb_query(self, session=None):
        dbs = session.query(Connection).filter(Connection.conn_type == 'mongo').order_by(Connection.conn_id)
        db_choices = list(((db.conn_id, db.conn_id) for db in dbs if db.get_hook()))
        conn_id_str = request.form.get('conn_id')
        csv = request.form.get('csv') == "true"
        sql = request.form.get('sql') or """[{"$match": {}}, {"$sort": {"createAt": -1}}, {"$limit": 100}]"""
        collection = request.form.get('collection') or 'user_event'

        results = ''
        if conn_id_str and request.method == 'POST':
            try:
                db = [db for db in dbs if db.conn_id == conn_id_str][0]
                hook = db.get_hook()
                _data = hook.aggregate(collection, json.loads(sql))
                df = pd.DataFrame(_data)
                try:
                    df['create_time'] = pd.to_datetime(df['createAt'], unit='ms')
                except Exception:
                    pass
                df = df.fillna('')
                results = df.to_html(
                    classes=['table', 'table-bordered', 'table-striped', 'no-wrap'], index=False, na_rep='')
            except Exception as e:
                flash(str(e), 'error')
            else:
                if csv:
                    headers = {"Content-Disposition": "attachment; filename=%s_%s.csv" % (conn_id_str, collection)}
                    return Response(response=df.to_csv(index=False), status=200, headers=headers, mimetype="application/text")

        class QueryForm(Form):
            conn_id = SelectField("Layout", choices=db_choices)
            collection = StringField("Collection")
            sql = TextAreaField("SQL", widget=wwwutils.AceEditorWidget())

        form = QueryForm(request.form, data={'conn_id': conn_id_str, 'sql': sql, 'collection': collection})
        session.commit()
        return self.render("mongodb_query.html", form=form, results=results, title="Mongodb Query")


v = MongodbQueryView(category="My", name="Mongodb Query")
```

#### plugins/blueprints/__init__.py

```python
from .mongo_query import v as mongo_query_v

admin_views = [mongo_query_v,]
menu_links = []

```

#### plugins/__init__.py

```python
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from .blueprints import admin_views, menu_links

bp = Blueprint("my_plugin", __name__, template_folder='blueprints/templates', static_url_path='/static')


class AirflowMyBlueprintPlugin(AirflowPlugin):
    name = "my_plugin"
    flask_blueprints = [bp]
    admin_views = admin_views
    menu_links = menu_links

```

### 用户认证

当然数据不能被所有人查看，所以改视图要判断是否登陆

```python
class OnlineUserView(BaseView):
    @expose('/', methods=['GET'])
    @login_required
    @provide_session
    def view(self, session=None):
```

`airflow.login.login_required`直接引用是NoneType，需要`load_login`，但是这个不应该，我看airflow源码启动的时候load了，不知道具体原因。。。

```python
if airflow.login is None:
    airflow.load_login()
login_required = airflow.login.login_required
```

1.10.3还不能区分区分权限，只能验证登陆跟超级用户
