---
layout: post
title: "Pandas设置excel样式的两种方式"
date: 2023-07-03 21:51:04 +0800
categories: 技术
tags: Pandas xlsxwriter
---

## 通过`Pandas`本身的`Styler`设置样式

https://pandas.pydata.org/docs/reference/style.html

`Pandas的`的`Styler`使用css样式，但是也不是所有样式都支持，下面是一个简单的例子，实现了设置列头及数据的样式。

```python
# 列头为黄色背景、字体加粗，数据内容为黄色背景
writer = pd.ExcelWriter('path/to/excel.xlsx', engine='xlsxwriter', engine_kwargs={'options': {'strings_to_formulas': False}})
df_style = df.style.apply(
    lambda x: [f'background-color:"yellow";'] * len(df.columns), axis=1, subset=df.columns
).applymap_index(
    lambda x: f'background-color:"blue";font-weight:bold;', axis=1
)
df_style.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False)
writer.close()
```

经过测试不是所有的html的css都会在`Styler`上生效, 下面是一些常用的设置excel的css

* `"font-family:"Arial";font-size:9pt;"` 字体、字号
* `"border-style:solid;border-width:1px;"` 边框
* `"text-align:left;"` 水平靠左，居中为`center`
* `"vertical-align:middle;"` 垂直居中
* `"white-space:pre-wrap;"` 自动换行

添加样式主要用到以下的四个方法，`apply`和`applymap`用于为数据内容添加样式，`apply_index`和`applymap_index`为列或者行的标题单元格设置样式。

### Styler.apply

```python
# 通过 axis 来指定传入的行还是列，为1时传入的是行，0时传入的是列，即变量x，类型是pandas.Series
# 通过 subset 来限制数据的index（列或者行），即变量x的数据
df.style.apply(lambda x: np.where(x == np.nanmax(x.to_numpy()), f"color: yellow;", None), axis=1)
```

### Styler.applymap

```python
# applymap相对于apply方式缺少了axis参数，默认传入的是列（column）
# apply返回的是一个列表，而applymap返回的是一个样式的字符串
df.style.applymap(lambda x: f'background-color:"yellow";', subset=df.columns)
```

### Styler.apply_index

```python
# 逻辑同apply，只不过apply_index操作的是列头或者行的index
df = pd.DataFrame([[1,2], [3,4]], index=["A", "B"])
def color_b(s):
    return np.where(s == "B", "background-color: yellow;", "")
df.style.apply_index(color_b)
```

### Styler.applymap_index

```python
# 逻辑同applymap，只不过applymap_index操作的是列头
df = pd.DataFrame([[1,2], [3,4]], index=["A", "B"])
def color_b(s):
    return "background-color: yellow;" if v == "B" else None
df.style.applymap_index(color_b)
```


## 通过`xlsxwriter`设置样式

https://xlsxwriter.readthedocs.io/working_with_pandas.html

```python
df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False)

# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

# Add a header format.
header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'fg_color': '#D7E4BC',
    'border': 1})

# Write the column headers with the defined format.
for col_num, value in enumerate(df.columns.values):
    worksheet.write(0, col_num + 1, value, header_format)
```

上面的例子设置的是一个单元格的一个单元格的添加样式，下面的例子可以直接设置一行的样式

```python
cell_format = workbook.add_format({'bold': True})

worksheet.set_row(0, 20, cell_format)
```

`xlsxwriter`是通过本身的`Format`类来设置样式的，具体参见以下文档

https://xlsxwriter.readthedocs.io/format.html#format

通过`workbook.add_format`添加`Format`实例，通过属性(Property)或者类方法(Method Name)来配置excel表格的样式

| Category   | Description	     |  Property	      | Method Name          |
| ---------- | ----------------- | ------------------ | -------------------- |
| Font	     | Font type	     |  'font_name'	      | set_font_name()      |
|  	         | Font size	     |  'font_size'	      | set_font_size()      |
|  	         | Font color	     |  'font_color'      | set_font_color()     |
|  	         | Bold	             |  'bold'	          | set_bold()           |
|  	         | Italic	         |  'italic'	      | set_italic()         |
|  	         | Underline	     |  'underline'	      | set_underline()      |
|  	         | Strikeout	     |  'font_strikeout'  | set_font_strikeout() |
|  	         | Super/Subscript   |  'font_script'	  | set_font_script()    |
| Number	 | Numeric format	 |  'num_format'	  | set_num_format()     |
| Protection | Lock cells        |  'locked'          | set_locked()         |
|  	         | Hide formulas     |  'hidden'          | set_hidden()         |
| Alignment	 | Horizontal align  |  'align'           | set_align()          |
|  	         | Vertical align    |  'valign'          | set_align()          |
|  	         | Rotation	         |  'rotation'        | set_rotation()       |
|  	         | Text wrap         |  'text_wrap'       | set_text_wrap()      |
|  	         | Reading order     |  'reading_order'   | set_reading_order()  |
|  	         | Justify last      |  'text_justlast'   | set_text_justlast()  |
|  	         | Center across     |  'center_across'   | set_center_across()  |
|  	         | Indentation       |  'indent'          | set_indent()         |
|  	         | Shrink to fit     |  'shrink'          | set_shrink()         |
| Pattern    | Cell pattern      |  'pattern'         | set_pattern()        |
|            | Background color  |  'bg_color'        | set_bg_color()       |
|            | Foreground color  |  'fg_color'        | set_fg_color()       |
| Border     | Cell border       |  'border'          | set_border()         |
|  	         | Bottom border     |  'bottom'          | set_bottom()         |
|  	         | Top border        |  'top'             | set_top()            |
|  	         | Left border       |  'left'            | set_left()           |
|  	         | Right border      |  'right'           | set_right()          |
|  	         | Border color      |  'border_color'    | set_border_color()   |
|  	         | Bottom color      |  'bottom_color'    | set_bottom_color()   |
|  	         | Top color         |  'top_color'       | set_top_color()      |
|  	         | Left color        |  'left_color'      | set_left_color()     |
|  	         | Right color       |  'right_color'     | set_right_color()    |

