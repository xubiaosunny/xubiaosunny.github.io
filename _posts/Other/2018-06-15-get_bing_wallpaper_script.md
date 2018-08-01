---
layout: post
title: "mac自动设置bing壁纸"
date: 2018-06-15 21:50:02
categories: 折腾
tags: bing 爬虫
---

一直觉得bing的壁纸不错，手机使用microsoft launcher可以每天获取bing壁纸，win10锁屏默认也是bing。想在mac上也能换上bing壁纸。在app store上有一款app可以做到，但是要12块钱。网上一搜好多脚本实现。。。emmm。。。看来和我有一样想法的也是大有人在。推荐一个网站[https://bing.ioliu.cn/](https://bing.ioliu.cn/)，这个哥们儿每天爬bing的壁纸，还做了网站展示，不光有壁纸，还有bing壁纸的介绍也展示了，很不错，也提供了壁纸下载的api。

请求[https://bing.ioliu.cn/](https://bing.ioliu.cn/)的api很自己爬bing也没什么两样，于是自己动手也写了个脚本。

```python3
# -*- coding: utf-8 -*-
import requests
import json
import time
import datetime
import os
import platform


BING_HOST = "https://cn.bing.com"
WALLPAPER_JSON_URL = '/HPImageArchive.aspx?format=js&idx={idx}&n={n}'
SET_WALLPAPER_CMD = {
    "Darwin": "osascript -e \'tell application \"Finder\" to set desktop picture to POSIX file \"{image_name}\"\'",
}

image_dir = os.path.abspath(os.path.dirname(__file__))


def set_wallpaper(image_name):
    if not os.path.exists(image_name):
        print("%s don't exist!!!" % image_name)
        return False

    c_os = platform.system()
    set_wallpaper_cmd = SET_WALLPAPER_CMD.get(c_os)
    os.system(set_wallpaper_cmd.format(image_name=image_name))
    print("set wallpaper successful: %s" % image_name)
    return True


def get_wallpaper():
    res = requests.get(BING_HOST + WALLPAPER_JSON_URL.format(idx=0, n=8))
    res_dict = json.loads(res.content.decode(encoding='utf-8'))

    for image in res_dict['images']:
        im_res = requests.get(BING_HOST + image['url'])
        date = image['enddate']
        image_name = os.path.join(image_dir, date + '.jpg')

        if os.path.exists(image_name):
            print('[~] %s already exists' % date)
            continue

        with open(image_name, 'wb') as f:
            f.write(im_res.content)
            print('[+] %s download successful' % date)

        today_str = datetime.datetime.today().strftime('%Y%m%d')
        if today_str == date:
            set_wallpaper(image_name)

        time.sleep(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Bing Wallpaper Program')
    parser.add_argument('--set', dest='image_name', help='set existed image to wallpaper')
    args = parser.parse_args()

    image_name = args.image_name
    if image_name:
        image_name = os.path.join(image_dir, image_name + '.jpg')
        set_wallpaper(image_name)
    else:
        get_wallpaper()
```

然后挂个crontab，实现每日自动更新。

```
0 10-18 * * * /usr/local/bin/python3 /Users/xubiao/Pictures/bing/bing.py >/dev/null 2>&1
```

也没什么难的东西，就是先爬图片存起来，然后再调用mac系统命令将爬到的图片设置为桌面壁纸。以后可以在添加些内容，对多平台支持。
