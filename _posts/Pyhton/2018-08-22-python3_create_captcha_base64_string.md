---
layout: post
title: "python3生成图片验证码并在angluar中显示"
date: 2018-08-22 17:59:48 +0800
categories: 技术
tags: captcha python Angular
---

python生成验证码基本套路，使用Pillow（python2可以用PIL）生成文字和干扰线。

参考文章：https://blog.fudenglong.site/2017/09/21/python3%E7%94%9F%E6%88%90%E9%AA%8C%E8%AF%81%E7%A0%81/

该文章代码生成了中文验证码，在此基础上我增加了英文数字验证码的选项，并区分了Unicode和gbk2312字符集（Unicode字符集包含中文太多，会出现过多生僻字）。由于在实际应用当中生成图片的情况较少，一般都是放到前端页面显示，故增加了生成图片base64字符串，便于接口传输。

### 代码

```python
import random
import string
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class ImageChar(object):
    def __init__(self, font_color=(0, 0, 0),
                 size=(160, 60),
                 font_path='/ui/src/assets/fonts/simsun.ttc',
                 bg_color=(255, 255, 255),
                 font_size=30):

        self.size = size
        self.font_path = font_path
        self.bg_color = bg_color
        self.font_size = font_size
        self.font_color = font_color
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.image = Image.new('RGB', size, bg_color)

    def rotate(self):
        self.image.rotate(random.randint(0, 30), expand=0)

    def draw_text(self, pos, txt, fill):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, font=self.font, fill=fill)

    @staticmethod
    def rand_rgb():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def rand_point(self):
        width, height = self.size
        return random.randint(0, width), random.randint(0, height)

    def rand_line(self, num=10):
        draw = ImageDraw.Draw(self.image)
        for i in range(num):
            draw.line([self.rand_point(), self.rand_point()], self.rand_rgb())

    @staticmethod
    def random_chinese(code='gbk2312'):
        if code == 'unicode':
            return chr(random.choice(range(0X4E00, 0X9FA5)))
        elif code == 'gbk2312':
            head = random.randint(0xb0, 0xf7)
            body = random.randint(0xa1, 0xf9)
            val = "%x%x" % (head, body)
            return bytes.fromhex(val).decode('gb2312')
        else:
            raise ValueError('code error')

    @staticmethod
    def random_char():
        return random.choice(string.ascii_letters + string.digits)

    def write_char(self, num=4, is_chinese=False):
        char_str = ""
        width, height = self.size
        gap, start = int(width / num - self.font_size), 0
        get_char_func = self.random_chinese if is_chinese else self.random_char
        for i in range(num):
            char = get_char_func()
            char_str += char
            x = start + self.font_size * i + random.randint(0, gap) + gap * i
            self.draw_text((x, random.randint(0, int((height - self.font_size) / 2))), char, self.rand_rgb())
            self.rotate()

        self.rand_line(random.randint(10, 15))

        return char_str

    def output(self, path):
        self.image.save(path)

    def to_base64(self):
        buffered = BytesIO()
        self.image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        return "data:image/jpeg;base64," + img_str.decode()

    @classmethod
    def example(cls):
        instance = cls(size=(160, 60), font_size=28)
        instance.write_char(4)
        instance.output("test.png")

    @classmethod
    def create_chinese_captcha(cls):
        instance = cls(font_path='%s/ui/src/assets/fonts/simsun.ttc' % (
            settings.BASE_DIR, ))
        char_str = instance.write_char(4, True)
        img_str = instance.to_base64()
        return char_str, img_str

    @classmethod
    def create_char_captcha(cls):
        instance = cls(font_path='%s/ui/src/assets/fonts/Arial.ttf' % (
            settings.BASE_DIR, ))
        char_str = instance.write_char(4)
        img_str = instance.to_base64()
        return char_str, img_str
```

* 注意如果使用中文需使用中文字体，否则不能显示

### 前端使用

前端使用angular框架，基本代码如下：

html

```html
<a nz-col [nzSpan]="8" (click)="getCaptchaImage()">
    <img [src]="captchaImage" height="40px">
</a>
```

TS

```typescript
...

captchaImage: string;

...

getCaptchaImage() {
    this.captchaApi.getBase64Img().subscribe( response => { 
        this.captchaImage = response['image']
    });
}

...
```

### 后端逻辑

每次请求生成验证码图片的时候，可以将验证码字符串存储在session中，以便做验证码校验。
