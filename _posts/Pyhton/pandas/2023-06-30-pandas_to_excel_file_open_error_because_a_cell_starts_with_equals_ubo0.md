---
layout: post
title: "由于单元格等号（“=”）开头导致Pandas导出的excel文件有问题解决"
date: 2023-06-30 15:17:55 +0800
categories: 技术
tags: Pandas xlsxwriter
---

## 问题介绍

使用Pandas导出的excel文件，使用office打开报如下问题，修复后可正常打开。由于文件数据很多，查看后未能发现导致问题的位置。

![](\assets\images\post\截屏2023-06-30 15.26.04.png)


## 解决过程

### 问题定位

由于sheet也很多，里面的行和列也很多，首先需要缩小范围。通过导出每个sheet也到单独的excel文件中，然后分别打开看看哪个sheet页中的数据有问题，然后定位到sheet页。然后同理定位到有问题的列。
然后我将该列中的数据逐条查看，发现有一条是等号"="开头的比较可疑，应为在excel中等于号后面可以是公式。将这一行数据删除后再次使用pandas导出发现excel文件可以正常打开了。
从而定位到了问题的原因：excel误认为等于号后面是公式，但是后面的内容是字符串，不是正确的公式，所有导致office打开的时候需要修复。

### 问题解决

网上检索后发现使用`xlsxwriter`写excel的时候是可以配置是否开启公式的，如下代码展示了`xlsxwriter`的使用以及相关配置的默认值。

```python
xlsxwriter.Workbook(filename, {
    'strings_to_numbers': False, 
    'strings_to_formulas': True, 
    'strings_to_urls': True
    })
```

在pandas中通过`engine_kwargs`来为`xlsxwriter`传入参数。具体解决方法关键代码如下：

```python
import pandas as pd

...

writer = pd.ExcelWriter(
    "<excel_name>.xlsx", engine='xlsxwriter', 
    engine_kwargs={'options': {'strings_to_formulas': False}})
df.to_excel(writer, "<sheet_name>", index=False)
writer.close()
```

然后再次导出excel文件，office打开就没有问题了。

## 参考链接

* https://stackoverflow.com/questions/51822922/avoid-inserting-formula-when-value-starts-with
* https://github.com/jmcnamara/XlsxWriter/issues/461
* https://xlsxwriter.readthedocs.io/working_with_pandas.html
