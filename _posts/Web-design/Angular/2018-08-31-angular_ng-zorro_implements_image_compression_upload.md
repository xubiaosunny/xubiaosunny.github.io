---
layout: post
title: "Angular ng-zorro 实现图片压缩上传（附加js实现）"
date: 2018-08-31 17:04:01
categories: 技术
tags: Angular ng-zorro
---

之前做过图片压缩上传的功能，但当时使用的是jquery/js那一套，放到angular项目中不好使，原理相同，即使用`canvas`绘图，然后压缩导出。

## js写法

当时也是在网上找得Demo修改而来的

```javascript
compress_img (file, ql, callback) {
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {
        var result = this.result;
        var img = new Image();
        img.src = result;
        // console.log(img);
        img.onload = function () {
            var that = this;
            // 默认按比例压缩
            var w = that.width,
                h = that.height,
                scale = w / h;
            w = ql.width || w;
            h = ql.height || (w / scale);
            var quality = 0.7;  // 默认图片质量为0.7
            //生成canvas
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            // 创建属性节点
            var anw = document.createAttribute("width");
            anw.nodeValue = w;
            var anh = document.createAttribute("height");
            anh.nodeValue = h;
            canvas.setAttributeNode(anw);
            canvas.setAttributeNode(anh);
            ctx.drawImage(that, 0, 0, w, h);
            // 图像质量
            if (ql.quality && ql.quality <= 1 && ql.quality > 0) {
                quality = ql.quality;
            }
            // quality值越小，所绘制出的图像越模糊
            var base64 = canvas.toDataURL('image/jpeg', quality);
            callback(base64);

        }
    }

},

convertBase64UrlToBlob (urlData){
    var arr = urlData.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type:mime});
},

/* 使用 */
var formdata = new FormData();
$.each($(ele).find('input[type=file]'), function(k, v){
    var file  = v.files[0];
    var p = {quality: 1}; // 压缩率
    //如果图片大小于500kb，则直接上传
    if (file.size > 500 * 1000){
        p.quality = (500 * 1000) / file.size;
    }
    compress_img(v.files[0], p, function (base64) {
    var bl = convertBase64UrlToBlob(base64);
    formdata.append(v.name, bl, file.name);
}
```

## Angular4+ 实现

ui用的是ng-zorro，居然怎么常见的功能也没带。。。网上插件也搜不到，大多数的实现也也是基于angularjs的。最终参考https://github.com/dfa1234/ngx-image-compress的实现完成了功能。

### 压缩服务封装

```typescript
import { Injectable, Renderer2 } from '@angular/core';

@Injectable()
export class ImageCompressService {
  maxSize = 500 * 1000;

  constructor(
    private renderer: Renderer2
  ) { }

  read(file: File) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = function () {
        resolve(reader.result);
      };
    });
  }

  compress(imageDataUrlSource: any, render: Renderer2, ratio?: number, quality?: number): Promise<string> {
    ratio = ratio ? ratio : 1;
    quality = quality ? quality : 0.5;

    return new Promise((resolve, reject) => {
      const sourceImage = new Image();
      // important for safari: we need to wait for onload event
      sourceImage.onload = function () {
        const canvas: HTMLCanvasElement = render.createElement('canvas');
        const ctx: CanvasRenderingContext2D = canvas.getContext('2d');

        canvas.width = sourceImage.naturalWidth * ratio;
        canvas.height = sourceImage.naturalHeight * ratio;

        ctx.drawImage(sourceImage, 0, 0, canvas.width, canvas.height);

        const mime = imageDataUrlSource.substr(5, imageDataUrlSource[0].length);
        // TODO test on mime
        const result = canvas.toDataURL('image/jpeg', quality);

        resolve(result);

      };

      sourceImage.src = imageDataUrlSource;
    });
  }

  convertBase64UrlToBlob (urlData): Blob {
    const arr = urlData.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
  }

  do (file: File) {
    if (file.size > this.maxSize) {
      const quality = this.maxSize / file.size;
      return new Promise((resolve, reject) => {
        this.read(file).then(srcData => {
          this.compress(srcData, this.renderer, 1, quality).then(value => {
            resolve(this.convertBase64UrlToBlob(value));
          });
        });
      });
    } else {
      return new Promise((resolve, reject) => { resolve(file); });
    }
  }
}
```

使用的时候直接使用`imgCompress.do`即可， maxSize可设置需要压缩的文件限制。

### 配合ng-zorro实现压缩后上传文件

使用`nzCustomRequest`覆盖默认行为实现定制需求以实现先压缩在上传，我使用的ng-zorro版本为1.0

```typescript
import { Component } from '@angular/core';
import { HttpClient, HttpRequest, HttpResponse } from '@angular/common/http';
import { NzMessageService, UploadFile } from 'ng-zorro-antd';
import { filter } from 'rxjs/operators';
import { ImageCompressService } from '@core/tool/image-compress.service';

@Component({
  selector: 'app-image-upload',
  template: `
    <nz-upload
        nzAction="api/upload/upload_file/"
        nzListType="picture-card"
        [(nzFileList)]="fileList"
        [nzShowButton]="fileList.length < 1"
        [nzPreview]="handlePreview"
        [nzCustomRequest]="handleUpload"
        [nzBeforeUpload]="beforeUpload"
        (nzChange)="uploadChange($event)">
        <i class="anticon anticon-plus"></i>
        <div class="ant-upload-text">Upload</div>
    </nz-upload>
  `,
  providers: [ ImageCompressService ]
})
export class ImageUploadComponent {
  fileList = [];
  previewImage = '';
  previewVisible = false;
  limitFileType = 'image/png,image/jpeg';

  constructor(
    public http: HttpClient,
    public msg: NzMessageService,
    public imgCompress: ImageCompressService
  ) { }

  handlePreview = (file: UploadFile) => {
    this.previewImage = file.url || file.thumbUrl;
    this.previewVisible = true;
  }

  uploadChange(e) {
    console.log(e);
  }

  beforeUpload = (file: UploadFile): boolean => {
    const isImage = file.type === 'image/jpeg';
    if (!isImage) {
      this.msg.error('You can only upload JPG file!');
    }
    return isImage;
  }

  handleUpload = (item) => {
    this.imgCompress.do(item.file).then((bl: Blob) => {
      const formData = new FormData();
      formData.append(item.name, bl);
      const url = item.action ? item.action : '/api/upload/upload_file/';
      const req = new HttpRequest('POST', url, formData, { reportProgress: true });

      this.http.request(req).pipe(filter(e => e instanceof HttpResponse)).subscribe((event: {}) => {
        item.file.response = event['body'];
        item.onSuccess({}, {
          status: 'done'
        });
      }, err => console.log('upload fail'));
    });
  }
}
```
