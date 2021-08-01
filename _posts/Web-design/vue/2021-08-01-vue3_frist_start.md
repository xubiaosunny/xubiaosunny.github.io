---
layout: post
title: "vue3初探"
date: 2021-08-01 15:42:59 +0800
categories: 技术
tags: vue
---

昨天写了一个页面，新创建的环境，因为之前用vue2，现在出来了正好试试，但用写具踩了不少坑。

## app初始化

vue2 直接用Vue来添加插件， vue3首先用createApp来创建app实例。

vue2 

```js
import Vue from 'vue'
import VueRouter from 'vue-router'
import Antd from 'ant-design-vue'

const HelloWorld = { template: '<div>Holle World</div>' }
const routes = [
  { path: '/hello', name: 'hello', component: HelloWorld },
]
const router = new VueRouter({
    routes
})
Vue.use(Antd)
new Vue({
  router,
}).$mount('#app')
```

vue3

```js
import { createApp } from 'vue';
import Antd from 'ant-design-vue';
import { createRouter, createWebHashHistory } from 'vue-router'

const HelloWorld = { template: '<div>Holle World</div>' }
const routes = [
  { path: '/hello', name: 'hello', component: HelloWorld },
]

const router = createRouter({。
  history: createWebHashHistory(),
  routes,
})
const app = createApp(App)
app.config.productionTip = false;

app.use(Antd);
app.use(router);

app.mount('#app')
```

## setup、ref、reactive

在vue2中我们会使用`data()`来初始化变量，而vue3中又多了一个方法`setup()`，暂时发现以下不同

* setup()中不能访问`this`
* setup()中返回的变量不能数据不能绑定，就是当数据修改了，但页面显示的不会变化

说到setup，与之关联的还有`ref()`和`reactive()`，为了首先数据在模版中绑定，返回的变量要用`ref()`和`reactive()`包装.

```vue
<template>
  <div>
    <a-button type="primary" @click="handleOk">handleOk</a-button>
    <h2> {{ text }} </h2>
  </div>
</template>
<script>
import { defineComponent, ref } from 'vue';
export default defineComponent({
  setup() {
    const text = ref('hello');

    const handleOk = e => {
      text.value = 'world';
    };

    return {
      text,
      handleOk,
    };
  },
});
</script>
```

> 响应式转换是“深层”的——它影响所有嵌套 property。在基于 ES2015 Proxy 的实现中，返回的代理是不等于原始对象。建议只使用响应式代理，避免依赖原始对象。

我理解的就是ref和reactive，ref用来包装基本数据类型的数据，而reactive用来包装类似Object这种嵌套类型饿。


```js
const value1 = ref('hello');
const value1 = ref(1);
const value1 = ref(true);

const value1 = reactive({'text': 'hello'});
```
