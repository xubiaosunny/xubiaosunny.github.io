---
layout: post
title: "Angular @Input()根据传入值自适应显示"
date: 2018-09-18 18:02:07
categories: 技术
tags: Angular html
---

在使用那`NZ-ZORRO`的时候发现很多组件的传入值既可以是`sting`类型，也可以是`TemplateRef`，比较灵活。我也试着实现这样的组件，开始使用`ngTemplateOutlet`来做的，发现只支持tempalte，传入string就报错了。后来看了`ng-zorro`的源码发现其实他们是根据类型判断走不同的`ng-container`来实现的。我以为这里用高级用法呢，有些失望。我也安ng-zorro的思路实现一下，逻辑比较简单，判断没那么多。

```typescript
mport { Component, OnInit, ViewChild, TemplateRef,  Input } from '@angular/core';


@Component({
  selector: 'app-log-modal',
  template: `
    <ng-container [ngSwitch]="true">
      <ng-container *ngSwitchCase="isTemplateRef(logContent)">
        <pre><ng-container [ngTemplateOutlet]="logContent"></ng-container></pre>
      </ng-container>
      <ng-container *ngSwitchCase="isString(logContent)">
        <pre [innerHTML]="logContent"></pre>
      </ng-container>
      <ng-container *ngSwitchDefault><pre></pre></ng-container>
    </ng-container>`,
})
export class LogModalComponent implements OnInit {
  @Input() logContent: string | TemplateRef<{}>;

  constructor() {}

  isTemplateRef (logContent) {
    return logContent instanceof TemplateRef;
  }

  isString (logContent) {
    return typeof(logContent) === 'string';
  }

  ngOnInit(): void {
  }
}

```

### JS类型判断

在JS类型判断的时候需要注意`instanceof`和`typeof`, 我的理解`typeof`可以返回基本数据类型（number、string等），而`instanceof`用来判断Class。在这一点上跟python就有比较大的区别，在python中都是Class，不论是内置数据类型`int`、`str`等，还是自定义的Class，都可以使用`isinstance`来判断实例的类型。

所以在TS(或JS)中判断是否为字符串等基本数据类型不能使用`instanceof`，要这样写

```typescript
typeof(logContent) === 'string'
```

### `NgTemplateOutlet`还可以为tmeplate传入变量

[https://angular.io/api/common/NgTemplateOutlet](https://angular.io/api/common/NgTemplateOutlet)

Usage notes

```typescript
<ng-container *ngTemplateOutlet="templateRefExp; context: contextExp"></ng-container>
```

Using the key $implicit in the context object will set its value as default.

> Example

```typescript
@Component({
  selector: 'ng-template-outlet-example',
  template: `
    <ng-container *ngTemplateOutlet="greet"></ng-container>
    <hr>
    <ng-container *ngTemplateOutlet="eng; context: myContext"></ng-container>
    <hr>
    <ng-container *ngTemplateOutlet="svk; context: myContext"></ng-container>
    <hr>

    <ng-template #greet><span>Hello</span></ng-template>
    <ng-template #eng let-name><span>Hello {{name}}!</span></ng-template>
    <ng-template #svk let-person="localSk"><span>Ahoj {{person}}!</span></ng-template>
`
})
class NgTemplateOutletExample {
  myContext = {$implicit: 'World', localSk: 'Svet'};
}
```
