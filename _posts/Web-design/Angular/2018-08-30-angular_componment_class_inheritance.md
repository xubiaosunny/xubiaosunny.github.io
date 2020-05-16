---
layout: post
title: "Angular组件类的继承"
date: 2018-08-30 10:13:30 +0800
categories: 技术
tags: Angular TypeScript
---

在Angular实际应用当中，很多情况下不同组件会用到相同的方法或者变量，通用的功能我们可以写成单独的组件然后在其他组件调用。但通用方法和变量我们可以写一个基类来实现。

弹框我们使用ng-zorro的modal组件，使用该组件需定义`isVisible`和`isConfirmLoading`等变量控制modal的显示和loading，还有一些可以通用的方法。都可以放到基类里面，以减少代码冗余。

### modal基类

```typescript
import { Component, OnInit, ViewChild } from '@angular/core';

export class AbstractModalComponent {
  isVisible: boolean;
  isConfirmLoading: boolean;
  constructor(
  ) {
    this.isVisible = false;
    this.isConfirmLoading = false;
  }

  showModal(): void {
    // 如有特殊需求，可在子类使用super继承
    this.isVisible = true;
  }

  hideModal() {
      this.isConfirmLoading = false;
      this.isVisible = false;
  }

  handleCancel(): void {
    this.isVisible = false;
  }
}
```

### 子类继承

```typescript
import {Component, OnInit, ViewChild, TemplateRef, Type, Input, EventEmitter, Output} from '@angular/core';
import { AbstractModalComponent } from '../modal/abstract-modal.component';

@Component({
  selector: 'app-set-tag',
  template: `
    <nz-modal [(nzVisible)]="isVisible" (nzOnCancel)="handleCancel()" (nzOnOk)="handleOk()"
        [nzOkLoading]="isConfirmLoading">
    </nz-modal>`,
})
export class SetTagComponent extends AbstractModalComponent implements OnInit {

  constructor(
  ) {
    super();
  }

  handleOk(): void {
    this.isConfirmLoading = true;
  }

  ngOnInit(): void {
  }
}
```

### super

构造函数内使用

```typescript
constructor() {
  super();
}
```

* 构造函数内有参数且为angular依赖注入
  
  ```typescript
  // 父类
  constructor(
    public alertMessage: AlertMessageService
  ) { }

  // 子类
  constructor(
    public alertMessage: AlertMessageService
  ) {
    super(alertMessage);
  }
  ```

类方法内使用

```typescript
showModal(): void {
  super.showModal()
}
```
