---
layout: post
title: "vue组件动态插槽实现"
date: 2019-11-15 19:36:52
categories: 技术 
tags: vue
---

最近在公司又开始写一些前端了，现在公司的主流是vue，所以用了vue。在搭框架的时候对基础组件进行了封装，在做公共组件会经常用到插槽（slot），官方文档地址如下

[https://cn.vuejs.org/v2/guide/components-slots.html](https://cn.vuejs.org/v2/guide/components-slots.html)

vue的`v-solt`与angular的`ngTemplateOutlet`类似，简单来说插槽就是用来填空的地方。简单的用法就不介绍了，主要在我的实践中遇到的动态插槽及通过插槽使用子组件的变量

## 场景

我在做通用表格组件（common-table）封装的时候需要实现根据列名的列表（columns）生成表的各列，每行默认填充各列对应的值，同时也提供定义特定列的显示，比如在名称列显示要加上转跳（a标签）。
在提供自定义实现上就需要用到插槽，并且列名不确定所以要实现动态插槽。

## 实现

以下只展示了关于插槽的代码

### 通用表格组件（common-table）组件

```html
<template>
    ...
        <md-table-row slot="md-table-row" slot-scope="{ item }">
          <md-table-cell
            v-for="column in columns"
            :key="column.index"
            :md-label="$t(column.title || column.index)"
            :md-sort-by="column.index"
          >
            <slot :name="'column-' + column.index" v-bind:item="item">{{
              item[column.index]
            }}</slot>
          </md-table-cell>
        </md-table-row>
    ...
</template>

<script>
export default {
  name: "common-table",
  props: {
    tableData: Array,
    columns: Array,
  }
};
</script>
```

columns 的数据格式为

```json
[
    {
        index: String,
        title: String
    },
    ...
]
```

### 页面组件使用

```html
<template>
    ...
        <common-table
          title=""
          :tableData="data"
          :columns="columns"
        >
          <template v-slot:column-name="{ item }">
            <router-link :to="`/xxx/${item.id}`">{{
              item.name
            }}</router-link>
          </template>
        </common-table>
    ...
</template>

<script>
import { CommonTable } from "@/components";

export default {
  components: {
    CommonTable
  },
  computed: {},
  data() {
    return {
      data: [],
      columns: [
        { index: "name", title: "Name" },
      ]
    };
  }
};
</script>
```

## 总结

通过for循环动态生成具名插槽，并绑定变量`item`，设置槽的默认显示

```html
<slot :name="'column-' + column.index" v-bind:item="item">{{ item[column.index] }}</slot>
```

在父组件可以从子组件获取数据

```html
<!-- 插槽名为column-name，获取变量item -->
<template v-slot:column-name="{ item }">
    ...
</template>
```

关于动态插槽名，根据文档貌似可以怎么写（未实践）：

```html
<base-layout>
  <template v-slot:[dynamicSlotName]>
    ...
  </template>
</base-layout>
```
