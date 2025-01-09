---
layout: post
title: "Vue 实现 AG Grid 自定义单元格编辑（cellEditor）"
date: 2025-01-09 14:57:49 +0800
categories: 技术
tags: ag-grid vue antd
---

`AG Grid` 提供了下面6种cellEditor：

* 文本，input `agTextCellEditor`
* 大文本, textarea `agLargeTextCellEditor`
* 单选，select `agSelectCellEditor`
* 富文本单选 `agRichSelectCellEditor`（社区版不提供，需要企业版）
* 日期选择 `agDateCellEditor`和`agDateStringCellEditor`
* 复选框，checkbox `agCheckboxCellEditor`

但是我们需其他类型的可编辑的单元格的话，就需要我们自定义了。
我这里以自定义一个多选单元格编辑组件来实践一下 `AG Grid` 的自定义单元格编辑，多选的是使用`Ant Design`的多选组件

## 自定义CellEditor

就是单元格在编辑状态使用的组件 `agAntdMultiSelectCellEditor.vue`

```vue
<script setup lang="ts">
import { onMounted, onBeforeUnmount, nextTick, ref } from 'vue';

const props = defineProps<{
  params: any
}>()

const multiSelectRef = ref<any>(null);

const value = ref<string[]>([]);
const options = ref<any[]>([])

const getValue = () => {
  return value.value
}

const initValue = () => {
  value.value = props.params.value;
  const labelMap = props.params.colDef.refData || {};
  options.value = props.params.values.map((item: any) => {
    return {
      label: labelMap[item] || item,
      value: item
    }
  })
};

onMounted(() => {
  initValue()
  nextTick(() => {
    multiSelectRef.value.focus()
  })
})

onBeforeUnmount(() => {
})

defineExpose({
  getValue
});
</script>

<template>
  <a-select
    ref="multiSelectRef"
    v-model:value="value"
    mode="multiple"
    size="small"
    style="width: 100%"
    :options="options"
  ></a-select>
</template>

<style scoped>

</style>
```

## 自定义Renderer

就是单元格在非编辑状态（展示）使用的组件 `agAntdMultiSelectRenderer.vue`

```vue
<template>
  <template v-for="(item, index) of value" :key="item">
    <span>{{ labelMap[item] || item }}<span v-if="index < value.length - 1">,</span></span>
  </template>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const value = ref<any[]>([])
const labelMap = ref<any[]>([])

const props = defineProps<{
  params: any
}>()

onMounted(() => {
  value.value = props.params.value
  labelMap.value = props.params.colDef.refData || {};
})

const refresh = (params: { value: string }) => {
}

defineExpose({
  refresh
});
</script>

<style scoped>
</style>
```

> `refresh` 方法会在数据变动时调用，可以加入一些自定义的逻辑

## `AG Grid`中使用自定义的cellEditor

```vue
<template>
  <ag-grid-vue
    :rowData="rowData"
    :columnDefs="colDefs"
    @cellValueChanged="onCellValueChanged"
  >
  </ag-grid-vue>
</template>
<script lang="ts" setup>
import { onMounted, ref, shallowRef } from 'vue';
import { AgGridVue } from "ag-grid-vue3";
import { 
  AllCommunityModule, 
  ModuleRegistry, 
  type GridApi, 
  type ColDef, 
  type ColGroupDef 
} from 'ag-grid-community';
import agAntdMultiSelectCellEditor from "./agAntdMultiSelectCellEditor.vue";
import agAntdMultiSelectRenderer from "./agAntdMultiSelectRenderer.vue";

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

const colDefs = ref<(ColDef|ColGroupDef)[]>([
  // 省略其他列配置
  {
    headerName: '用户',
    field: "user_id",
    editable: true,
    cellRenderer: agAntdMultiSelectRenderer,
    cellEditor: agAntdMultiSelectCellEditor,
    cellEditorParams: {
      values: [1, 2, 3],
    },
    refData: {
      1: '张三',
      2: '李四',
      3: '王五',
    },
    width: 150,
  },
  // 省略其他列配置
])

const rowData = ref([]);
</script>
```

> `cellEditorParams.value` 可以传入编辑的可选项，`refData` 可以传入单元格value和要显示label的映射对象（Map）。

## 参考链接

* <https://www.ag-grid.com/javascript-data-grid/cell-editors/>
