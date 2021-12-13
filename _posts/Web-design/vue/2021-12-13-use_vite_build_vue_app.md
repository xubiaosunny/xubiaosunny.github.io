---
layout: post
title: "使用vite构建vue3"
date: 2021-12-13 11:29:30 +0800
categories: 技术
tags: vite vue
---

`vite`官方文档：https://cn.vitejs.dev/

## 创建vue模版工程

```bash
# npm 6.x
npm init vite@latest my-vue-app --template vue

npm init vite@latest my-vue-app --template vue-ts # 创建vue-ts版本

# npm 7+, 需要额外的双横线：
npm init vite@latest my-vue-app -- --template vue
```

## 使用

```bash
npm run dev
npm run build
```

## 问题

* build的时候报如下警告（Some chunks are larger than 500 KiB after minification. Consider）

```
(!) Some chunks are larger than 500 KiB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/guide/en/#outputmanualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
```

在 `vite.config.ts`文件中添加`chunkSizeWarningLimit:1500`

```typescript
export default defineConfig({
  ...
  build: {
    ...
    chunkSizeWarningLimit:1500,
  }
})
```

* dev运行的时候没问题，但构建完页面空白

网上找了好久也没发现问题，后来逐步定位到是vue-router导致的。

```typescript
const routes = [
  { path: '/hello', component: import('@/pages/HelloWorld.vue') },
]
```

改为

```typescript
import HelloWorld from '@/pages/HelloWorld.vue';

const routes = [
  { path: '/hello', component: HelloWorld },
]
```

配置路由的时候import在调试的时候没问题，build就不好使，必须先import再配置路由。

* @方式路径import

在 `vite.config.ts`文件中添加`'@': path.resolve(__dirname, '/src'`

```typescript
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '/src'),
      // 'vue': 'vue/dist/vue.esm-bundler.js',
    },
  },
  ...
})
```

> 'vue': 'vue/dist/vue.esm-bundler.js' 可以解决dev的时候运行时编译

