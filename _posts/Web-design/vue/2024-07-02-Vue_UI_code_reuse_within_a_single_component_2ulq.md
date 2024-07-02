---
layout: post
title: "Vue单组件内UI代码复用（附Angular实现）"
date: 2024-07-02 11:19:11 +0800
categories: 技术
tags: vue Angular
---

在vue等主流框架中UI复用是常用操作，但大多数都是组件复用。有的时候比较少的代码，而且只会在当前组件内复用。这样的话最好能在本组件内，不必再封装一个组件用来调用。

## Angular实现

在Angular中通过`ng-container`和`ng-template`实现很容易。

```typescript
@Component({
  selector: 'app-test',
  template: `
    <ng-template #loadingTemplate let-name="name">
        <div>Loading {{ name }}...</div>
    </ng-template>

    <ng-container 
        *ngTemplateOutlet="loadingTemplate;context:{name: 'Page1'}">
    </ng-container>
    <ng-container 
        *ngTemplateOutlet="loadingTemplate;context:{name: 'Page2'}">
    </ng-container>
`})
export class AppComponent {
  
}
```

## Vue实现

Vue没有内置的方式，但是可以通过第三方包`@vueuse/core`来实现

```vue
<template>
  <DefineLoadingTemplate v-slot="{ name }">
    <div>Loading {{ name }}...</div>
  </DefineLoadingTemplate>

  <ReuseLoadingTemplate name="Page1" />
  <ReuseLoadingTemplate name="Page2" />
</template>

<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core'

const [DefineLoadingTemplate, ReuseLoadingTemplate] = createReusableTemplate()
</script>
```

看官方文档，`createReusableTemplate`不但可以传递普通参数，还可以传递插槽(solt)，暂时没有该需求，没有验证，以下为官方示例代码

```vue
<script setup>
import { createReusableTemplate } from '@vueuse/core'

const [DefineTemplate, ReuseTemplate] = createReusableTemplate()
</script>

<template>
  <DefineTemplate v-slot="{ $slots, otherProp }">
    <div some-layout>
      <!-- To render the slot -->
      <component :is="$slots.default" />
    </div>
  </DefineTemplate>

  <ReuseTemplate>
    <div>Some content</div>
  </ReuseTemplate>
  <ReuseTemplate>
    <div>Another content</div>
  </ReuseTemplate>
</template>
```

## 最后

`@vueuse/core`还有许多的方法，比如绑定localstorage， 监听滚动等，`createReusableTemplate`只是其中一例。等需要的时候在研究。
对比angular，vue内置的还是欠缺很多。但是感觉angular的份额越来越小了，确实vue用起来简单些，不过vue3用了ts没有vue2好上手了。
