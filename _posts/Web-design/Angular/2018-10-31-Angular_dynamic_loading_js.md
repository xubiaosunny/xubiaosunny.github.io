---
layout: post
title: "Angular动态加载js文件"
date: 2018-10-31 17:34:47
categories: 技术
tags: Angular
---

在做`付钱拉`支付的时候，要使用它的js包。

### 在html中通过`script`标签引入

```html
<script src="xxxx.js"></scritp>
```

这种方法必须将代码写在`index.html`中，写到component中不好使。这样的话所有页面的都会加载这个js文件，没有必要而且会增加加载时间。

网上还有一种方法是在`angular.json`中引入，然后在`typings.d.ts`用`any`大法定义，例如：

```typescript
declare var $: any;
declare var jQuery: any;
```

因为我们用的angular6，已经没有`typings.d.ts`文件。其实这些方法都不是按需引入，都是全局的。

### 动态加载js

网上找了找，开始没找到好的方案，我自己写了一个简单的，就是在需要js的组件中动态创建一个`script`标签，然后append到body中，但是很快就报错了，找不到js包。原因很简单就是因为js文件还没加载完，后来我就写了个延时，但这太low了，万一延时还没加载完还是回报错的。后来我在网上找到了解决方法（想法类似，只不过人家js onload时才执行代码，我不知道这么用。。。）

链接地址：[https://code.i-harness.com/zh-CN/q/20e463c](https://code.i-harness.com/zh-CN/q/20e463c)

我的实现如下

```typescript
declare var FUQIANLAPC: any; // any大法

// ...

loadScript () {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = 'https://lib.fuqian.la/pcinit.4.0.js';
      if (script['readyState']) {  // IE
          script['onreadystatechange'] = () => {
              if (script['readyState'] === 'loaded' || script['readyState'] === 'complete') {
                  script['onreadystatechange'] = null;
                  resolve(true);
              }
          };
      } else {
          script.onload = () => {
              resolve(true);
          };
      }
      script.onerror = (error: any) => resolve(false);
      document.getElementsByTagName('head')[0].appendChild(script);
    });
  }

  goFuqianla (amount) {
    this.loadScript().then( (status) => {
      if (!status) return;
      // 我的业务逻辑
      // 。。。
    });
  }
```

之后我将该功能封装为通用组件也不难：

```typescript
loadScript (scriptSrc) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = scriptSrc;
    if (script['readyState']) {  // IE
        script['onreadystatechange'] = () => {
            if (script['readyState'] === 'loaded' || script['readyState'] === 'complete') {
                script['onreadystatechange'] = null;
                resolve(true);
            }
        };
    } else {
        script.onload = () => {
            resolve(true);
        };
    }
    script.onerror = (error: any) => resolve(false);
    document.getElementsByTagName('head')[0].appendChild(script);
  });
}

// use
// loadScript方法传入js文件的网络路径即可
```
