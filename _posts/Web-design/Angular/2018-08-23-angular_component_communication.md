---
layout: post
title: "Angular组件间通信（传值、回调）"
date: 2018-08-28 09:25:27
categories: 技术
tags: Angular
---

最近公司公有云控制台改版，采用前后分离，之前一直是MVC一套撸。前端框架使用angualr6，后台使用Python3.5+Django2.0。由于前端人手不够，我也一直充当前端的角色，之前做过一个物理机的项目，对angualr也用所了解了。

在项目中有很多公用的部分我们可以拆出来写成单独的组件，或者一个大的功能也可以拆成多个独立的组件。那么这个时候就会涉及到组件间的通信。

## 父组件向子组件传值

### Input()

子组件

```typescript
import {Component, OnInit, ViewChild, TemplateRef, Input} from '@angular/core';
@Component({
  selector: 'app-set-tag',
  template: `
    <div>
      <ng-container *ngTemplateOutlet="myContent"></ng-container>
    </div>
    <input nz-input (click)="$event.stopPropagation();" name="tag" id="tag" [(ngModel)]="tagName" #tag="ngModel">
    `,
})
export class SetTagComponent implements OnInit {
  @Input() tagName: string;
  @Input() myContent: string | TemplateRef<{}>;

  constructor(
  ) {
  }

  ngOnInit(): void {
  }
}
```

父组件

```html
<!-- 传入变量 -->
<app-set-tag #setTagModel [tagName]="'tttt'"></app-set-tag>

<!-- 传入template -->
<app-set-tag [myContent]="contentTemplate">
  <ng-template #contentTemplate>
    <h1>ttt</h1>
    <p>ttt</p>
  </ng-template>
</app-set-tag>
```

### ViewChild

父组件

```typescript
@Component({
  selector: 'app-autoscaling-list',
  templateUrl: './list.component.html'
})
export class AutoscalingListComponent implements OnInit {
  @ViewChild('setTagModel') setTag: SetTagComponent;
  constructor(
  ) {
  }

  ngOnInit(): void {
    this.setTag.tagName = 'ttt';
  }
}
```

* 非Input()字段也可以使用ViewChild传值

## 子组件向父组件传值

### Output()

子组件

```typescript
import {Component, EventEmitter, OnInit, Output} from '@angular/core';

@Component({
  selector: 'app-datacenter-operation',
  templateUrl: './datacenter-operation.component.html',
  styleUrls: ['./datacenter-operation.component.css']
})
export class DatacenterOperationComponent implements OnInit {
  @Output() private operationOuter = new EventEmitter();
  constructor() {}

  ngOnInit(): void {
    this.operationOuter.emit('success');
  }
}
```

父组件

```html
<app-datacenter-operation #operationDatacenterModal (operationOuter)="handelOperation($event)"></app-datacenter-operation>
```

```typescript
@Component({
  selector: 'app-datacenter-list',
  templateUrl: './datacenter-list.component.html',
  styleUrls: ['./datacenter-list.component.css'],
  providers: [DatacenterApiService]
})
export class DatacenterListComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {
  }

  handelOperation(e) {
    comsole.log(e);  // success
  }
}
```

### 利用@Output()实现Callback

子组件

```typescript
import {Component, OnInit, ViewChild, TemplateRef, Input} from '@angular/core';
@Component({
  selector: 'app-set-tag',
  template: `
    <button nz-button nzType="primary" (click)="handleOk()">Ok</button>
    `,
})
export class SetTagComponent implements OnInit {
  @Output() okCallback = new EventEmitter<any>();
  constructor() { }

  handleOk(): void {
    // do someting before
    this.okCallback.emit();
    // do someting after
  }

  ngOnInit(): void {
  }
}
```

父组件

```typescript
@Component({
  selector: 'app-autoscaling-list',
  template:`<app-set-tag #setTagModel (okCallback)="doSetTag($event)"></app-set-tag>`
})
export class AutoscalingListComponent implements OnInit {
  constructor() { }

  doSetTag(e) {
    // do someting
  }

  ngOnInit(): void {
  }
}
```