---
layout: post
title: "angular登陆后转跳之前页面"
date: 2018-09-05 18:13:19 +0800
categories: 技术
tags: Angular
---

之前做了关于登陆认证的功能，但没有实现登陆后转跳之前的url。

使用angular前后端分离后，前后的交互都是异步的，之前MVC那一套的302在这里已经不适用了。但可以借鉴之前的思想，在url中的GET参数（问号后面的值）中传递要转跳的url。

### 使用拦截器转跳登陆页面并携带next转跳url

```typescript
import { Injectable, Injector } from '@angular/core';
import { ActivatedRoute, Router } from "@angular/router";
import { Location } from '@angular/common';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/do';


@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private router: Router) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
      return next.handle(request).do((event: HttpEvent<any>) => {
          if (event instanceof HttpResponse) {
              // do stuff with response if you want
          }
      }, (err: any) => {
          if (err instanceof HttpErrorResponse) {
              if (err.status === 401) {
                  const next = this.location.path();
                    const url = next.split('?')[0];
                    if (url !== '/passport/login') {
                        this.router.navigateByUrl(`/passport/login?next=${next}`);
                    }
              }
          }
      });
  }

}
```

### 登陆成功获取转跳url并转跳

```typescript
...

constructor(
  private router: Router,
  private route: ActivatedRoute,
)

...

  // 如果有next则转跳next，否则转跳‘/’
  this.route.queryParams.subscribe((params: Params) => {
    const next = params['next'] ? params['next'] : '/';
    this.router.navigate([next]);
  });

...
```