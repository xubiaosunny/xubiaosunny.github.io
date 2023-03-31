---
layout: post
title: "vxe-table高级表格(grid)自定义toolbar指令编码(code)"
date: 2023-03-29 20:40:06 +0800
categories: 技术
tags: vxe-table
---

下面是vxe-table高级表格使用toolbar的配置示例

```javascript
toolbarConfig: {
  buttons: [
    { code: 'insert_actived', name: '新增', icon: 'vxe-icon-square-plus' },
    { code: 'delete', name: '直接删除', icon: 'vxe-icon-delete' },
    { code: 'mark_cancel', name: '删除/取消', icon: 'vxe-icon-delete' },
    { code: 'save', name: 'app.body.button.save', icon: 'vxe-icon-save', status: 'success' }
  ],
  refresh: true,
  import: true,
  export: true,
  print: true,
  zoom: true,
  custom: true
},
```

完整例子见 https://vxetable.cn/v3/#/table/grid/fullEdit


查看[toolbar的接口文档](https://vxetable.cn/v3/#/toolbar/api)也没有介绍code有哪些，以及如何添加自定义的code。

在网上查询无果后，看了下vxe-table的源码找到了对应实现代码，代码片段和地址如下

https://github.com/x-extends/vxe-table/blob/master/packages/grid/src/grid.ts

```typescript
...
    switch (code) {
      case 'insert':
        return $xetable.insert({})
      case 'insert_actived':
        return $xetable.insert({}).then(({ row }) => $xetable.setEditRow(row))
      case 'mark_cancel':
        triggerPendingEvent(code)
        break
      case 'remove':
        return handleDeleteRow(code, 'vxe.grid.removeSelectRecord', () => $xetable.removeCheckboxRow())
      case 'import':
        $xetable.importData(btnParams)
        break
      case 'open_import':
        $xetable.openImport(btnParams)
        break
      case 'export':
        $xetable.exportData(btnParams)
        break
      case 'open_export':
        $xetable.openExport(btnParams)
        break
      case 'reset_custom':

      ...

      default: {
          const btnMethod = VXETable.commands.get(code)
          if (btnMethod) {
            btnMethod({ code, button, $grid: $xegrid, $table: $xetable }, ...args)
          }
        }
      }
...
```

由源码可以看出是通过匹配code来执行对应的代码，vxe-table内置了许多code，如果匹配不到内置的code，就会到`VXETable.commands`中找code。这样的话就好办了，我们可以向`VXETable.commands`添加自己的code和对应的方法。
如添加一个在最后面新增一条记录的功能，code为`insert_bottom_actived`。

```javascript
import VXETable from 'vxe-table'

VXETable.commands.add('insert_bottom_actived', function ({ code, button, $grid, $table }, ...args) {
  return $table.insertAt({}, -1).then(({ row }) => $table.setEditRow(row))
})
```

这样就可以使用我们自定义的`insert_bottom_actived`来配置toolbar了

```javascript
toolbarConfig: { 
  buttons: [
    { code: 'insert_bottom_actived', name: '新增', icon: 'vxe-icon-square-plus' },
    { code: 'delete', name: '删除', icon: 'vxe-icon-delete' },
    { code: 'save', name: '保存', icon: 'vxe-icon-save', status: 'success' }
  ],
},
```

以上方式适用于全局，如果为单个页面添加指令code处理，可以在`vxe-grid`上添加`toolbar-button-click`事件

```vue
...

<template>
  <vxe-grid ref='xGrid' v-bind="gridOptions" 
    @toolbar-button-click="toolbarButtonClickEvent">
  </vxe-grid>
</template>

...

<script>

...

  methods: {
    toolbarButtonClickEvent ({ code }) {
      const $table = this.$refs.xGrid
      switch (code) {
        case 'insert_bottom_actived':
          $table.insertAt({}, -1).then(({ row }) => $table.setEditRow(row))
          break
      }
    },
  }

...
</script>
```
