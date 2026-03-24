# 大鱼TT 310 全封闭机箱（封箱）设计
# Dayu TT310 Full Enclosure Design

## 项目概述 / Project Overview

本项目为 **大鱼TT 310** 3D打印机（打印尺寸 310×310×310mm）设计全封闭机箱。

This project designs a full enclosure for the **Dayu TT310** 3D printer (print volume 310×310×310mm).

### 主要组件 / Major Components

1. **顶部封板** - 配合风机散热孔或风扇位
2. **四周侧板** - 左/右/后三面
3. **前门板** - 铰链+磁吸快拆设计
4. **底部支架** - 固定打印机主体

### 机箱尺寸 / Enclosure Dimensions

- 外形尺寸（估算）: 470 × 450 × 720 mm
- 内腔空间: 约 440 × 420 × 680 mm
- 材质: 3D打印 PLA/PETG

### 目录结构 / Directory Structure

```
enclosure/
├── freecad/
│   └── Assembly.FCStd   # FreeCAD 主装配文件
├── stls/                # STL 输出文件
├── steps/               # STEP 输出文件
├── docs/                # 文档（装配说明、BOM等）
├── README.md            # 本文件
├── dimensions.md        # 尺寸数据
├── layout.txt           # 布局图
└── plan.md              # 设计计划
```

## 软件要求 / Software Requirements

### CAD 软件 / CAD Software

| 软件 / Software | 版本 / Version | 用途 / Purpose |
|----------------|----------------|----------------|
| **FreeCAD** | ≥ 0.19 | 主要设计工具 |
| Onshape | - | 备选（云端） |

### 切片软件 / Slicing Software

| 软件 / Software | 建议设置 / Recommended Settings |
|----------------|--------------------------------|
| Bambu Studio / Orca Slicer | 层高 0.2mm, 壁厚 3-4 walls |
| PrusaSlicer | PLA: 210°C / PETG: 240°C |

### 仿真/验证 / Simulation & Validation

- **Bambu Studio** 或 **Orca Slicer** - 切片验证
- **OpenSCAD** - 参数化修改（可选）

## 设计组 / Design Groups

在 FreeCAD Assembly.FCStd 中，预设以下装配组：

| 组名称 | 功能 | 包含零件 |
|--------|------|---------|
| Assembly_Top | 顶部面板组 | 顶板、风扇安装座 |
| Assembly_Left | 左侧面板组 | 左面板、线缆孔 |
| Assembly_Right | 右侧面板组 | 右面板、散热孔 |
| Assembly_Back | 后面板组 | 后面板、进风口 |
| Assembly_Front | 前门面板组 | 铰链门板、磁吸锁 |
| Assembly_Bottom | 底部支架组 | 底框、脚座 |

## 许可证 / License

本项目采用 **CC BY-NC-SA 4.0** 许可证。

## 参考资料 / References

- B站开源235尺寸封箱: https://www.bilibili.com/video/BV1pe41117h2/
- Gitee TT310增高封箱: https://gitee.com/sk66666/TT310zenggaofengxiang

## 更新日志 / Changelog

- 2026-03-24: US-001 完成，尺寸研究和布局规划
- 2026-03-24: US-002 完成，FreeCAD 项目初始化
