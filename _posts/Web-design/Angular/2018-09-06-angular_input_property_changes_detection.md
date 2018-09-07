---
layout: post
title: "Angular 使用@Input()检测数据变更"
date: 2018-09-06 17:46:56
categories: 技术
tags: Angular
---

之前使用@Input()用于父子组件间通信，参考[之前的博客](/技术/2018/08/28/angular_component_communication.html)。

可以做到单向绑定的效果，但不能检测传入值的变化，我这里需要根据传入值的变化改变其他值。[这里](https://ngdev.space/angular-2-input-property-changes-detection-3ccbf7e366d2)介绍了@Input()的另外一种用法。@Input() 不但可以装饰变量，也能装饰`get`和`set`方法。

我这里的是要根据产品的状态来显示不同颜色提示，我们公司产品比较多，大多数都有状态显示，所以封装个通用组件。以下为基本实现。

```typescript
import { Component, OnInit, Input } from '@angular/core';


const statusTypeMap = {
  'Running': 'success',
  'Provisioning': 'warning',
  'Stopped': 'error',
};


@Component({
  selector: 'app-status-show',
  template: `
    <nz-badge [nzStatus]="statusType" [nzText]="status"></nz-badge>
    `,
})
export class StatusShowComponent implements OnInit {
  private _statusType: string;
  private _status: string;

  @Input()
  set status(name: string) {
    this._status = name;
    this.setStatusType();
  }

  get status (): string {
    return this._status;
  }

  get statusType (): string {
    return this._statusType;
  }

  constructor () {
  }

  private setStatusType () {
    this._statusType = statusTypeMap[this._status] ? statusTypeMap[this._status] : 'default';
  }

  ngOnInit(): void {
  }
}

```

typescript的`get`和`set`在python中也有，在python中是通过`property`装饰器实现的。