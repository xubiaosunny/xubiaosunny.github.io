---
layout: post
title: "Angular动态加载组件"
date: 2018-12-14 10:48:31
categories: 技术
tags: Angular
---

最近在看一些无关技术的书：《三体》还有《浪潮之巅》，一直没学啥新东西，工作的内容也轻车熟路，所以最近页没写啥博客。好久没写变得懒散了，还是得坚持这个习惯。

前两天做一个应用市场的功能，每个应用页面都不同，但使用同一个url（要不然得写n个url）。我的思路是，url映射的组件根据url中传入的`aapName`来动态加载对应的各应用的组件。

参考：

> [https://segmentfault.com/a/1190000010086185](https://segmentfault.com/a/1190000010086185)
> [https://angular.cn/guide/dynamic-component-loader](https://angular.cn/guide/dynamic-component-loader)

定义应用的`interface`

```typescript
export interface EnterAppComponent {
  data: any;
}
```

某应用组件具体实现：

```typescript
@Component({
  selector: 'app-market-app-demo',
  template: `
    ...
  `,
})
export class MarketAppDemoComponent implements OnInit, EnterAppComponent {
  @Input() data;
  constructor(
    private sanitizer: DomSanitizer
  ) { }

  ngOnInit(): void {
  }
}
```

应用名与组件映射表：

```typescript
export const appComponentMap = {
  'demoApp': MarketAppDemoComponent,
  ...
};
```

动态加载组件核心代码：

```typescript
import { Component, Input, OnInit, ViewChild, ComponentFactoryResolver, ViewContainerRef } from '@angular/core';

@Component({
  selector: 'app-market-enter-app',
  template: `
    <nz-card>
      <ng-template #enterAppContainer></ng-template>
    </nz-card>
  `
})
export class MarketEnterAppComponent implements OnInit {
    appName = this.route.snapshot.params.appName;

    @ViewChild('enterAppContainer', { read: ViewContainerRef }) container: ViewContainerRef;
    constructor(
        private componentFactoryResolver: ComponentFactoryResolver
    ) { }
    loadComponent(appComponent) {
        const componentFactory = this.componentFactoryResolver.resolveComponentFactory(appComponent);
        const componentRef = this.container.createComponent(componentFactory);

        const instance = (<EnterAppComponent>componentRef.instance);
        instance.data = {};
    }

    ngOnInit(): void {
        // 根据appName 动态加载对应组件
        const appComponent = appComponentMap[this.appName];
        if (appComponent) {
          this.loadComponent(appComponent);
        }
    }
}
```

在获取到实例的时候对实例调用的时候回报‘没有xxx属性’的错误，可以为实例指定类型：

```typescript
const instance = <EnterAppComponent>componentRef.instance;
```

类似的还有

```typescript
// 如果不指定类型回报 没有submit方法
const form = <HTMLFormElement>document.getElementById('form')
form.submit();
```
