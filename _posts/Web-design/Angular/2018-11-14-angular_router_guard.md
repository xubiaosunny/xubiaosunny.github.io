---
layout: post
title: "Angular路由守卫验证用户登陆状态"
date: 2018-11-14 17:46:31 +0800
categories: 技术
tags: Angular
---

最近我们公有云控制台改版已经接近尾声了，最近三个月大部分时间在写前端，我TM一个写python的天天玩这个，
很不爽，不爽归不爽，工作还得做。大功能都开发完了，这两天一直在改细节问题，今天我们架构师说怎么打开页
面的时候会先闪一下然后再转跳到登陆页？之前验证用户登陆认证状态我是通过后端api返回`401`来告诉前端用
户未认证的，前端通过`Angular`拦截器来转跳登陆页面，因为请求是异步的，没有返回`response`的时候
angular就已经吧页面渲染完了，等返回后才转跳，所以会闪一下。

别的不说了，直接说解决方法：使用`CanActivate`来控制页面的显示与否，参考地址

[https://code.i-harness.com/zh-CN/q/20bdb56](https://code.i-harness.com/zh-CN/q/20bdb56)
[https://angular.io/api/router/CanActivate](https://angular.io/api/router/CanActivate)

Angular这么成熟的框架，这些基本的解决方法都有提供的，只是自己没有系统学习过，都是遇到问题再查阅资料解决。`路由守卫`也是切片编程的思想，跟`Python`的`装饰器`思维上差不多。用的时候也比较简单：

实现自己的`CanActivate`注入类

```typescript
import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable()
class CanActivateTeam implements CanActivate {
  constructor(private permissions: Permissions, private currentUser: UserToken) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean>|Promise<boolean>|boolean {
    // 业务逻辑
  }
}
```

在route中给需要的路由配置守卫

```typescript
    { path: 'dashboard', component: DashboardComponent, canActivate: [CanActivateAuth] }
```

`CanActivate`注入类的`canActivate`方法允许的返回值可以为`Observable<boolean> | Promise<boolean> | boolean`，这就为我们提供了异步请求的验证方式，可以直接返回`Observable<boolean>`的`HttpClient`请求，以为我们的接口中还融合了其他信息，我使用`Promise`多封装了一层，基本代码如下：

```typescript
import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { CustomerApiService } from './service/customer-api.service';
import { Observable } from 'rxjs';

const realnameIgnoreUrl = [
  '/customer/authentication',
  '/customer/authentication/edit',
];

@Injectable()
export class CanActivateAuth implements CanActivate {
  constructor(
    private router: Router,
    private customerApi: CustomerApiService,
    public i18n: I18NService
    ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean>|Promise<boolean>|boolean {
    return new Promise((resolve, reject) => {
      this.customerApi.getAuthenticationStatus().subscribe(res => {
        if (res.status === 'Anonymous') {
          // 未登录转跳登陆页面
          this.router.navigateByUrl(`/passport/login?next=${state.url}`);
          resolve(false);
        } else {
          if (res.status !== 'Pass' && realnameIgnoreUrl.indexOf(state.url) < 0) {
            // 显示实名认证提示框
            // ...
          }
          resolve(true);
        }
      });
    });
  }
```

之前显示实名认证提示框的逻辑时写在`Router.events`中的，每次路由变化请求接口拿认证状态，现在正好都放到路由守卫里面，也省了不少事。

路由守卫不光`canActivate`一种，还有`canActivateChild`,`canDeactivate`,`canLoad`，用法都差不多
可以参考官方文档：

[https://angular.io/guide/router#milestone-5-route-guards](https://angular.io/guide/router#milestone-5-route-guards)