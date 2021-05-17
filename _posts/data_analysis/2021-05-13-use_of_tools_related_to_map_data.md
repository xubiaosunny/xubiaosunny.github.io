---
layout: post
title: "地理数据分析相关工具的使用"
date: 2021-05-13 18:59:01 +0800
categories: 技术
tags: GeoDa GIS echart
---


在进行地理数据分析的时候首先需要一个地图文件（shp或其他格式），一般中国的省市县区地图文件都可以在网上下载到，如果下载不到的暂时没有研究如何自己制作。

## 地图裁剪

我们下载到的地图文件包含整个中国，如果我们只想要长三角的几个省，我们可以使用QGIS（或者ArcGIS，ArcGIS是收费软件）。

首先使用QGIS打开对应的shp文件，然后选中想要的省份，点击 `Layer` -> `Create Layer` -> `New GeoPackage Layer...` 导出即可（.gpkg）

## 数据合并

使用GeoDa打开裁剪好的地图文件（.gpkg），点击 `表格` -> `合并`来合并地图数据和指标数据，方便后来进行莫兰指数等空间分析

## echart绘图

使用GeoDa另存，选择格式为`GeoJOSN`，因为echart识别`name`字段，所以如果没有`name`字段，需要在`features.properties`中添加`name`字段来标注该省份。

```json
# 省.geojson
{
    "type": "FeatureCollection",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": [
        {
            "type": "Feature",
            "properties": {
--->            "name": "上海市",
                "省代码": 310000,
                "省": "上海市",
                "类型": "直辖市",
                "D_2009": 0.516310,
                "D_2014": 0.701202,
                "D_2019": 0.580798
            },
...
```

### 示例代码

目录结构

```
.
├── index.html
└── 省.json
```

由于跨域问题，`省.json`是导出的`省.geojson`的jsonp格式

```html
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>ECharts</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css"
        integrity="sha256-T/zFmO5s/0aSwc6ics2KLxlfbewyRz6UNw1s3Ppf5gE=" crossorigin="anonymous">

    <!-- 引入 echarts.js -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.1.1/dist/echarts.min.js"
        integrity="sha256-Yhe8c0oOs2dPYVQKLAi1aBB9uhr7yMmh67ukoWBqDuU=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"
        integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js"
        integrity="sha256-7dA7lq5P94hkBsWdff7qobYkp9ope/L5LQy2t/ljPLo=" crossorigin="anonymous"></script>
</head>

<body>

    <div class="container-fluid"> 
        <div id="chart" class="row"></div>
    </div>
    <script type="text/javascript">
        function drawChart() {
            $("#chart").append(`<div id="chart_1"  style="width: 800px;height:500px;"></div>`);
            // 基于准备好的dom，初始化echarts实例
            var myChart = echarts.init(document.getElementById(`chart_1`));

            myChart.hideLoading();

            // 指定图表的配置项和数据
            var option = {
                title: {
                    text: `test`,
                    textStyle: {
                        fontWeight: 'normal',
                        // lineHeight: 56,
                    },
                    top: 10,
                    left: 50,
                },
                tooltip: {
                    trigger: 'item',
                },
                toolbox: {
                    show: true,
                    orient: 'vertical',
                    left: 'right',
                    top: 'center',
                    feature: {
                        dataView: { readOnly: false },
                        restore: {},
                        saveAsImage: {}
                    }
                },
                visualMap: {
                    x: 'center',
                    y: 'bottom',
                    pieces: [
                        { gt: 0.8, label: '高水平耦合', color: 'orangered' },
                        { gt: 0.5, lte: 0.8, label: '磨合状态', color: 'pink' },
                        { gt: 0.3, lte: 0.5, label: '拮抗状态', color: 'yellow' },
                        { gte: 0, lte: 0.3, label: '低水平耦合', color: 'lightskyblue' },
                    ]
                },
                series: [
                    {
                        name: 'name',
                        type: 'map',
                        mapType: 'my-china', // 自定义扩展图表类型
                        label: {
                            show: true
                        },
                        data: [
                            { name: '上海市', value: 0.569974686 },
                            { name: '江苏省', value: 0.678708509 },
                            { name: '浙江省', value: 0.95899621 },
                            { name: '安徽省', value: 0.998302882 },
                            { name: '江西省', value: 0.941445674 },
                            { name: '湖北省', value: 0.991038399 },
                            { name: '湖南省', value: 0.943186363 },
                            { name: '重庆市', value: 0.949275065 },
                            { name: '四川省', value: 0.835819768 },
                            { name: '贵州省', value: 0.725220756 },
                            { name: '云南省', value: 0.992338543 },
                        ]
                    }
                ]
            };

            // 使用刚指定的配置项和数据显示图表。
            myChart.setOption(option);
        }

        function getJson(geoJson) {
            echarts.registerMap('my-china', geoJson);
            drawChart();

        }

    </script>

    <script type="text/javascript" src="省.json?callback=getJson"></script>
</body>

</html>
```

