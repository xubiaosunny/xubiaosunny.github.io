---
layout: post
title: "Vue3 setup语法糖"
date: 2025-01-09 14:29:59 +0800
categories: 技术
tags: vue
---

`setup` 是 Vue 3 引入的新特性，它使得组件的逻辑和状态更加清晰、简洁。初次VUE3使用还是用的VUE2风格的代码，通过各种选项来定义组件的逻辑，后来 `setup` 语法糖用的多了，也慢慢熟练了，这里简单总结一下两种风格代码的常见差异。

## **模版使用定义**

使用 `setup` 语法糖，定义的变量、方法等自动暴露给 `template`

```vue
<script setup>
import {ref} from 'vue'
const msg = ref('11111')
const doSomething = () => {
  msg.value = '22222'
}
</script>

<template>
  <h1>{{ msg }}</h1>
  <button @click="doSomething" >do</button>
</template>
```

不使用 `setup` 语法糖，则需要 `return` 来暴露给 `template` ，否则在 `template` 中无法调用

```vue
<script>
import {ref} from 'vue'
export default {
  setup() {
    const msg = ref('11111')
    const doSomething = () => {
      msg.value = '22222'
    }
    return {msg, doSomething}
  }
}
</script>

<template>
  <h1>{{ msg }}</h1>
  <button @click="doSomething" >do</button>
</template>
```

## **生命周期钩子函数**

在 `setup` 中，生命周期钩子通过 Vue 3 的 Composition API 来调用

```vue
<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  console.log('Component mounted');
});
</script>
```

传统的 Vue 3 组件中，生命周期钩子函数是通过组件选项中的 `mounted` 等选项来定义的

```vue
<script>
export default {
  setup() {  },
  created() {
    console.log('Component created');
  },
  mounted() {
    console.log('Component mounted');
  }
};
</script>
```

## **props**

使用 `setup` 语法糖，使用 `defineProps` 

```vue
<template>
  <div>{{ foo }}</div>
</template>

<script setup>
const props = defineProps({
  foo: String
})
</script>
```

不使用 `setup` 语法糖，通过 `props` 来声明

```vue
<template>
  <div>{{ foo }}</div>
</template>

<script>
export default {
  props: {
    foo: String,
  },
  setup() {
    
  },
}
</script>
```

> 类似的 `emits` 使用 `defineEmits` 来声明

## **组件**

使用 `setup` 语法糖，导入子组件可以直接使用

```vue
<script setup>
import MyComponent from './MyComponent.vue'
</script>

<template>
  <MyComponent />
</template>
```

不使用 `setup` 语法糖，则需要使用 `components` 选项来显式注册

```vue
<script>
import MyComponent from './MyComponent.vue'
export default {
  components: {
    MyComponent
  },
  setup() {
    // ...
  }
}
</script>
```

## **自定义指令**

使用 `setup` 语法糖，以 `v` 开头的驼峰式命名的变量会自动注册为**自定义指令**

```vue
<script setup>
// 在模板中启用 v-highlight
const vHighlight = {
  mounted: (el) => {
    el.classList.add('is-highlight')
  }
}
</script>

<template>
  <p v-highlight>This sentence is important!</p>
</template>
```

不使用 `setup` 语法糖需要需要通过 `directives` 注册

```vue
<script>
export default {
  setup() {
    /*...*/
  },
  directives: {
    // 在模板中启用 v-highlight
    highlight: {
      mounted: (el) => {
        el.classList.add('is-highlight')
      }
    }
  }
}
</script>
```

## 参考链接

* <https://vuejs.org/api/sfc-script-setup>
* <https://cn.vuejs.org/guide/reusability/custom-directives>
