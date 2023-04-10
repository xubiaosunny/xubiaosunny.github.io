---
layout: post
title: "多种方式实现PDF合并、生成目录及大纲、添加水印"
date: 2023-04-10 13:34:44 +0800
categories: 技术
tags: python PDF reportlab pikepdf PyPDF2 pymupdf
---

最近帮同事做一些PDF相关的功能，大致需求就是将多个PDF合并为一个并且为其生成目录（目录以合并前的各个PDF为单位），而且可以给合并后的PDF添加自定义的水印。
在实现过程中编码测试了多个相关Python包，其中较难的是生成目录，因为这个网络上没有现成的方案，但可以通过计算页数先生成一个目录的PDF，然后载将目录和其他PDF一起合并。

本文用到主要用到`reportlab` `pikepdf` `PyPDF2` `pymupdf` `Pillow`五个第三方包。
`reportlab`用来生成目录以及水印PDF，`Pillow`用来生成水印图片，`pikepdf` `PyPDF2` `pymupdf`这个三个包都可以合并PDF、添加大纲和水印。

其实一开始就使用`pikepdf` `PyPDF2`完成了功能的开发，但据同事反应在大文件合并和添加水印时慢并且可能奔溃，测试的pdf文件总大小大概在1.6G。
我进行调试发现程序运行的过程中确实内存占用很多，最高可达将近5个G，确实可能会在配置低的电脑上OOM。后来又使用`pymupdf`开发了相应的功能。
不得不说`pymupdf`性能确实强很多，同样的测试文件整个过程中内存占用不到1个G，运行速度也有显著提高，并且合并后并添加水印的输出文件只有200多M（之前700M）。

这三个包除了`pymupdf`性能强之外，还有一些其他区别，主要在打水印方面。

* `pikepdf` `PyPDF2`添加的水印为PDF文件，`pymupdf`是图片文件。
* `pikepdf`可以为一页添加多个水印（可以直接设置几行几列，很方便），
* `PyPDF2`看起来只能添加一个水印，而且位置控制不方便，需要定制水印PDF的大小以便契合每一页，
* `pymupdf`一般也只一页添加一个水印，理论上可以添加多个，但需要自己实现计算好每个水印的位置


## 生成目录（TABLE OF CONTENTS）

生成含有目录的PDF需要用到`reportlab`，具体参考下面链接的官方例子实现

* https://www.reportlab.com/snippets/8/
* https://www.reportlab.com/snippets/13/

```python
import os
import time
import logging
import math
import decimal
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import PageBreak
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.frames import Frame
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT_PATH = os.path.join(BASE_DIR, 'static/fonts/MSYH.TTC')
pdfmetrics.registerFont(ttfonts.TTFont('MSYH', DEFAULT_FONT_PATH))
DEFAULT_FONT = 'MSYH'
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


class TOCDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        super().__init__(filename, **kw)
        template = PageTemplate(
            'normal', [Frame(2.5*units.cm, 2.5*units.cm, 15*units.cm, 25*units.cm, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))


h1 = PS(fontName=DEFAULT_FONT, name='Heading1', fontSize=18, leading=20)
h2 = PS(fontName=DEFAULT_FONT, name='Heading2', fontSize=16, leading=18)
body = PS(fontName=DEFAULT_FONT, name='Body', fontSize=12, leading=14)

toc_styles = [
    PS(fontName=DEFAULT_FONT, fontSize=18, name='TOCHeading1',
       leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=18),
    PS(fontName=DEFAULT_FONT, fontSize=16, name='TOCHeading2', leftIndent=0,
       firstLineIndent=0, spaceBefore=10, leading=16),
]

def build_toc(pdf_list: dict, out_path: str):
    """
    pdf_list: 需要合并的PDF列表, eg. [{"path": "T14_1_1.pdf", "bookmark": "受试者筛选情况"}]
    out_path: 输出路径
    """
    tmp_file_name = os.path.join(TMP_DIR, f'tmp_toc_template_{int(time.time() * 1000)}.pdf')
    logging.info('start build Table Of Contents')
    story = []
    toc = TableOfContents()
    toc.levelStyles = toc_styles
    story.append(toc)
    story.append(PageBreak())

    table_page_total = 0
    for pdf_info in pdf_list:
        pdf = Pdf.open(pdf_info['path'])
        page_num = len(pdf.pages)
        table_page_total += page_num
        story.append(Paragraph(pdf_info['bookmark'], h2))
        for i in range(page_num):
            story.append(Paragraph(f"{pdf_info['bookmark']}-{i}", body))
            story.append(PageBreak())

    doc = TOCDocTemplate(tmp_file_name)
    doc.multiBuild(story)
    logging.info('end build Table Of Contents')
    del doc, story, toc

    writer = PdfWriter()
    toc_reader = PdfReader(tmp_file_name)
    toc_num = len(toc_reader.pages) - table_page_total

    for page in toc_reader.pages[:toc_num]:
        writer.add_page(page)
    with open(out_path, "wb") as fp:
        writer.write(fp)
    writer.close()
    os.remove(tmp_file_name)
```

使用`build_toc`函数即可根据传入的PDF列表生成包含目录的PDF文件。

## 合并PDF并添加导航大纲（Outline）

在这一步需要用到上面的生成含有目录的PDF，然后将目录PDF和所有PDF合并，并在过程中添加大纲

### `PyPDF2`

```python
from PyPDF2 import PdfReader, PdfWriter


def merge_pdfs_and_build_toc_use_pypdf2(pdf_list: dict, out_path: str):
    """
    合并多个PDF并生成目录（PyPDF2实现）

    pdf_list: 需要合并的PDF列表, eg. [{"path": "T14_1_1.pdf", "bookmark": "受试者筛选情况"}]
    out_path: 合并后输出路径
    """
    tmp_toc_path = os.path.join(TMP_DIR, f'tmp_toc_{int(time.time() * 1000)}.pdf')
    build_toc(pdf_list, tmp_toc_path)

    writer = PdfWriter()
    toc_reader = PdfReader(tmp_toc_path)
    for page in toc_reader.pages:
        writer.add_page(page)

    current_page = len(toc_reader.pages)
    for pdf_info in pdf_list:
        logging.info(f'merging {pdf_info["path"]}')
        writer.add_outline_item(
            pdf_info['bookmark'], current_page, parent=None)
        _reader = PdfReader(pdf_info['path'])
        for page in _reader.pages:
            writer.add_page(page)
            current_page += 1

    logging.info(f'output... {out_path}')
    with open(out_path, "wb") as fp:
        writer.write(fp)

    writer.close()
    os.remove(tmp_toc_path)
```

### `pikepdf`

```python
def merge_pdfs_and_build_toc_use_pikepdf(pdf_list: dict, out_path: str):
    """
    合并多个PDF并生成目录(pikepdf实现)

    pdf_list: 需要合并的PDF列表, eg. [{"path": "T14_1_1.pdf", "bookmark": "受试者筛选情况"}]
    out_path: 合并后输出路径
    """
    tmp_toc_path = os.path.join(TMP_DIR, f'tmp_toc_{int(time.time() * 1000)}.pdf')
    build_toc(pdf_list, tmp_toc_path)

    toc_pdf = Pdf.open(tmp_toc_path)
    output = Pdf.new()
    for page in toc_pdf.pages:
        output.pages.append(page)

    current_page = len(toc_pdf.pages)
    outline_list = []
    for pdf_info in pdf_list:
        logging.info(f'merging {pdf_info["path"]}')
        _pdf = Pdf.open(pdf_info['path'])
        for page in _pdf.pages:
            output.pages.append(page)
        outline_list.append(OutlineItem(pdf_info['bookmark'], current_page))
        current_page += len(_pdf.pages)

    with output.open_outline() as outline:
       outline.root.extend(outline_list)
    output.save(out_path)
    os.remove(tmp_toc_path)
```

### `pymupdf`

```python
import fitz


def merge_pdfs_and_build_toc_use_fitz(pdf_list: dict, out_path: str):
    """
    合并多个PDF并生成目录(pymupdf实现)

    pdf_list: 需要合并的PDF列表, eg. [{"path": "T14_1_1.pdf", "bookmark": "受试者筛选情况"}]
    out_path: 合并后输出路径
    """
    logging.info(f'building TOC')
    tmp_toc_path = os.path.join(TMP_DIR, f'tmp_toc_{int(time.time() * 1000)}.pdf')
    build_toc(pdf_list, tmp_toc_path)

    doc = fitz.Document()
    toc = []

    _doc = fitz.open(tmp_toc_path)
    doc.insert_pdf(_doc)
    current_page = len(_doc) + 1
    logging.info(f'merging TOC')
    for index, item in enumerate(pdf_list):
        logging.info(f'merging {index} {item["path"]}')
        _doc = fitz.open(item['path'])
        doc.insert_pdf(_doc)
        toc.append([1, item['bookmark'], current_page])
        current_page += len(_doc)

    doc.set_toc(toc)
    doc.save(out_path)
```

## 为PDF添加文字水印

同样分别使用上面三个包分别实现，具体代码如下

```python
from PIL import Image, ImageDraw, ImageFont


def generate_string_watermark_pdf(
        out_path, watermark_str: str, watermark_width: int = None, watermark_height: int = None, fontsize: int = 18, center=False):
    """
    生成水印PDF文件
    """
    angle = 45
    text_fill_alpha = 0.1
    str_len_r = 0
    for s in watermark_str:
        str_len_r += 0.75 if (ord(s) <= 255) else 1
    if watermark_width is None or watermark_height is None:
        watermark_width = watermark_height = str_len_r * fontsize / 3

    c = canvas.Canvas(out_path, pagesize=(
        watermark_width * units.mm, watermark_height * units.mm))
    if center:
        t_length = int(math.sqrt(watermark_width ** 2 + watermark_height ** 2))
        t_prop = (t_length - str_len_r * fontsize / 2.54) / 2 / t_length
        c.translate(
            t_prop * watermark_width * units.mm, t_prop * watermark_height * units.mm)
    else:
        c.translate(
            0.1 * watermark_width * units.mm, 0.05 * watermark_height * units.mm)  # 进行轻微的画布平移保证文字的完整
    c.rotate(angle)  # 设置旋转角度
    c.setFont(DEFAULT_FONT, fontsize)  # 设置字体及字号大小
    c.setStrokeColorRGB(0, 0, 0)  # 设置文字轮廓色彩
    c.setFillColorRGB(0, 0, 0)  # 设置文字填充色
    c.setFillAlpha(text_fill_alpha)  # 设置文字填充色透明度
    c.drawString(0, 0, watermark_str)  # 绘制文字内容
    c.save()  # 保存水印pdf文件


def add_string_watermark_use_pypdf2(pdf_path: str, out_path: str, watermark_str: str, fontsize: int = 24):
    """
    PDF添加文字水印（PyPDF2实现）

    pdf_path: 原始PDF路径
    out_path: 输出PDF路径
    watermark_str: 水印字符
    """
    writer = PdfWriter()
    reader = PdfReader(pdf_path)

    def _add_watermark(target_page):
        watermark_pdf_name = os.path.join(TMP_DIR, f"tmp_watermark_{int(time.time() * 1000)}.pdf")
        watermark_width = int(target_page.mediabox.width / decimal.Decimal(2.54))
        watermark_height = int(target_page.mediabox.height / decimal.Decimal(2.54))
        generate_string_watermark_pdf(
            watermark_pdf_name, watermark_str, watermark_width=watermark_width, watermark_height=watermark_height, fontsize=fontsize, center=True)
        watermark_pdf = PdfReader(watermark_pdf_name)
        watermark_page = watermark_pdf.pages[0]
        target_page.merge_page(watermark_page)
        target_page.compress_content_streams()
        os.remove(watermark_pdf_name)

    for index, page in enumerate(reader.pages):
        logging.info(f'add watermark on page {index}')
        _add_watermark(page)
        writer.add_page(page)
        del page

    logging.info(f'output... {out_path}')
    with open(out_path, "wb") as fp:
        writer.write(fp)

    writer.close()


def add_string_watermark_use_pikepdf(pdf_path: str, out_path: str, watermark_str: str, watermark_width: int = None, watermark_height: int = None, fontsize: int = 18):
    """
    PDF添加文字水印（pikepdf实现）

    pdf_path: 原始PDF路径
    out_path: 输出PDF路径
    watermark_str: 水印字符
    """
    def add_watermark(pdf_path: str, out_path: str, watermark_path: str):
        target_pdf = Pdf.open(pdf_path)
        watermark_pdf = Pdf.open(watermark_path)
        watermark_page = watermark_pdf.pages[0]

        for target_page in target_pdf.pages:
            ncol = int(target_page.trimbox[2] / watermark_page.trimbox[2])
            nrow = int(target_page.trimbox[3] / watermark_page.trimbox[3])
            for x in range(ncol):
                for y in range(nrow):
                    rectangle = Rectangle(
                        target_page.trimbox[2] * x / ncol,
                        target_page.trimbox[3] * y / nrow,
                        target_page.trimbox[2] * (x + 1) / ncol,
                        target_page.trimbox[3] * (y + 1) / nrow
                    )
                    target_page.add_overlay(
                        watermark_page, rectangle)

        target_pdf.save(out_path)

        watermark_pdf.close()
        target_pdf.close()

    watermark_pdf_name = os.path.join(TMP_DIR, f"tmp_watermark_{int(time.time() * 1000)}.pdf")
    generate_string_watermark_pdf(watermark_pdf_name, watermark_str, watermark_width=watermark_width, watermark_height=watermark_height, fontsize=fontsize)
    logging.info(f'adding watermark by {watermark_pdf_name}')
    add_watermark(pdf_path, out_path, watermark_pdf_name)
    os.remove(watermark_pdf_name)


def add_image_watermark_use_fitz(pdf_path: str, out_path: str, image_path: str):
    """
    PDF添加图片水印（pymupdf实现）

    pdf_path: 原始PDF路径
    out_path: 输出PDF路径
    image_path: 水印图片路径
    """
    logging.info(f'add image watermark ...')
    doc = fitz.open(pdf_path)
    pix = fitz.Pixmap(image_path)
    img_xref = 0 
    for page in doc:
        page_pix = page.get_pixmap()
        p_length = int(math.sqrt(page_pix.width ** 2 + page_pix.height ** 2))
        t_length = int(math.sqrt(pix.width ** 2 + pix.height ** 2))
        t_prop = (p_length - t_length) / 2 / p_length
        start_h = int(t_prop * page_pix.height)
        start_w = int(t_prop * page_pix.width)
        rect = fitz.Rect(start_w, start_h, pix.width + start_w, pix.height + start_h)
        img_xref = page.insert_image(rect, pixmap=pix, xref=img_xref)
    doc.save(out_path)


def add_string_watermark_use_fitz(pdf_path: str, out_path: str, watermark_str: str, fontsize: int = 32):
    """
    PDF添加文字水印（pymupdf实现）

    pdf_path: 原始PDF路径
    out_path: 输出PDF路径
    image_path: 水印图片路径
    """
    logging.info(f'generate watermark image ...')
    tmp_watermark_path = os.path.join(TMP_DIR, f"tmp_watermark_{int(time.time() * 1000)}.png")
    image = Image.new(mode='RGBA', size=(int(fontsize * len(watermark_str)), int(fontsize * 1.3)))
    draw_table = ImageDraw.Draw(image)
    draw_table.text((0, 0), watermark_str, fill=(0, 0, 0, 70), font=ImageFont.truetype(DEFAULT_FONT_PATH, fontsize))
    # image.show()
    image = image.rotate(45, expand=True, fillcolor=(0,0,0,0))
    image.save(tmp_watermark_path, 'PNG') 
    image.close()

    add_image_watermark_use_fitz(pdf_path, out_path, tmp_watermark_path)

```
