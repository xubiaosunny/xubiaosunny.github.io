---
layout: post
title: "Ionic入门实践"
date: 2024-02-21 22:24:17 +0800
categories: 技术
tags: Ionic Angular
---

之前写了一个记账的应用一直自己使用，使用Flutter开发的。年前家人换手机了，这个应用的安装包也找不到了，然后用之前的代码编译还通不过，原因是现在Flutter版本高了，之前开发时的代码不适用了，好久没写Dart了，想想也难受。
所以上网又调研了一下其他移动端App的开发框架，选用了Ionic，原因是其可以使用Vue、Angular、React来开发，这个领域我熟啊。现记录一下实践过程。

## 安装

```bash
npm install -g @ionic/cli
```

## 创建项目

```bash
ionic start
```

输出

```
? Use the app creation wizard? No

Pick a framework! 😁

Please select the JavaScript framework to use for your new app. To bypass this prompt next time, supply a value for the
--type option.

? Framework: Angular

Every great app needs a name! 😍

Please enter the full name of your app. You can change this at any time. To bypass this prompt next time, supply name,
the first argument to ionic start.

? Project name: ionic-test

Let's pick the perfect starter template! 💪

Starter templates are ready-to-go Ionic apps that come packed with everything you need to build your app. To bypass this
prompt next time, supply template, the second argument to ionic start.

? Starter template: tabs
? Would you like to build your app with NgModules or Standalone Components?
 Standalone components are a new way to build with Angular that simplifies the way you build your app.
 To learn more, visit the Angular docs:
 https://angular.io/guide/standalone-components
```

> 这里我选用了Angular，当然Vue和React也是可以的。只是Ionic最早只支持Angular，估计Angular的兼容性会更好些吧（猜测），而且Angulr我也熟悉。

## 运行项目

```bash
ionic serve
```

## 编译项目

```bash
ionic build
```

### 编译为Android App

```bash
npm install @capacitor/android

npx cap add android

npx cap copy && npx cap sync

npx cap open android
```

然后通过Android Studio编译为apk文件（**Generate Signed Bundle / APK**）

详见官方文档：

* <https://capacitorjs.com/docs/android#adding-the-android-platform>
* <https://ionicframework.com/docs/deployment/play-store>

## 代码开发

Ionic应用的开发没啥好说的，基本上就是写angualr，我重写用的UI组件都是Ionic自带的，暂时没有遇到什么问题。

## 参考链接

* <https://ionicframework.com/docs/>

