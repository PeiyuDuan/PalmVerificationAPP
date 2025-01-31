# PalmVerificationAPP

## 项目概述

PalmVerificationAPP 是一个基于掌纹识别技术的应用项目。本项目结合计算机视觉技术，对掌纹区域进行检测与特征提取，从而实现对掌纹的有效验证与识别。

## 技术细节

### 1. **ROI区域检测**

- **模型**: 使用 YOLO（You Only Look Once）模型对掌纹的 ROI（Region of Interest）区域进行检测。
- **功能**: 快速、准确地定位掌纹区域，为后续特征提取提供高质量的输入。

### 2. **特征提取**

- **模型**: 使用 MobileFaceNet 对检测出的 ROI 区域进行特征提取。
- **输入**: 提取 224×224 尺寸的掌纹图像。
- **输出**: 生成该图像的特征向量，供后续的匹配与验证。

## 系统架构

- **后端**:
  - 功能较为完善，完成了掌纹识别的核心功能，包括 ROI 检测、特征提取和特征匹配。
- **前端**:
  - 当前为一个基础 Demo，主要用于展示应用的基本功能。

## 注意事项

- 前端使用了uniapp框架，需要使用hbuilderx编译运行
- 不同时间段的特征提取会有较大的差异，可能此处有不足之处
