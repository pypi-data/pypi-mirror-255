# Label Explorer

#### 介绍

🚀 基于 Electron 的 YOLO 标签分析与整合工具

### 作者简介

#### 👨‍🏫 导师

曾逸夫，从事人工智能研究与开发；主研领域：计算机视觉；[YOLOv8官方开源项目代码贡献人](https://github.com/ultralytics/ultralytics/graphs/contributors)；[YOLOv5官方开源项目代码贡献人](https://github.com/ultralytics/yolov5/graphs/contributors)；[YOLOv5 v6.1代码贡献人](https://github.com/ultralytics/yolov5/releases/tag/v6.1)；[YOLOv5 v6.2代码贡献人](https://github.com/ultralytics/yolov5/releases/tag/v6.2)；[YOLOv5 v7.0代码贡献人](https://github.com/ultralytics/yolov5/releases/tag/v7.0)；[Gradio官方开源项目代码贡献人](https://github.com/gradio-app/gradio/graphs/contributors)

✨  Github：https://github.com/Zengyf-CVer

#### 👩‍🎓 学生

邓乙华，从事计算机视觉的研究和 JavaScript 项目的开发。

### Label Studio

https://github.com/HumanSignal/label-studio

对Label Studio导出的格式进行转换

```shell
yarn add electron --dev
```

### 安装教程

```shell
# Electron版
yarn install
yarn run start

# Python CLI版
pip install label-explorer
```

### 使用教程

#### Python CLI

```shell
# 使用默认参数
label-explorer

# 自定义图片路径和标签路径
label-explorer -sld path/to/imgs -sid path/to/labels

# 自定义训练集和验证集比列
label-explorer -p 0.9
label-explorer -p 0.7
label-explorer -p 0.75
```
