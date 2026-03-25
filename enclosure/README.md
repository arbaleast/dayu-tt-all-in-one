# 大鱼TT 310 全封闭机箱（封箱）设计
# Dayu TT310 Full Enclosure Design

## 项目概述 / Project Overview

本项目为 **大鱼TT 310** 3D打印机（打印尺寸 310×310×310mm）设计全封闭机箱。

This project designs a full enclosure for the **Dayu TT310** 3D printer (print volume 310×310×310mm).

## ⚠️ 重要警告 / Important Warning

> **310mm 尺寸封箱尚未经过实机验证！**
>
> 官方 UP主 大鱼DIY 在 B站视频（[BV1pe41117h2](https://www.bilibili.com/video/BV1pe41117h2/)）中明确说明：
> "我做的是 **235尺寸** 的封箱，310尺寸的**并没有实机验证过**，如有问题，麻烦大佬们反馈给我"
>
> 本项目的封箱设计目标是 **310mm 尺寸**，属于**先行开发、待验证**阶段。
> 在实际打印和测试前，所有尺寸仅供参考。

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

- [BV1pe41117h2](https://www.bilibili.com/video/BV1pe41117h2/) — B站官方235尺寸封箱（**唯一有实物的参考**，310尺寸未经官方验证⚠️）
- [Gitee TT310zenggaofengxiang](https://gitee.com/sk66666/TT310zenggaofengxiang) — 310增高封箱开源文件（第三方参考）
- [BV1bdqzYbEVg](https://www.bilibili.com/video/BV1bdqzYbEVg/) — 大鱼DIY官方回应"大鱼TT还值得一玩吗"

## 验证清单 / Validation Checklist

- [ ] 310 框架实际尺寸测量（框架宽度/深度/高度）
- [ ] 底部支架与调整脚配合间隙确认
- [ ] 侧板与框架固定夹位置匹配
- [ ] 门板铰链安装位偏差
- [ ] 顶部风扇位与 Z 轴碰撞检查
- [ ] 实际装配后腔体温升测试

## 更新日志 / Changelog

- 2026-03-25: 添加310mm验证警告、235 vs 310差异对比表、验证清单
- 2026-03-24: US-001 完成，尺寸研究和布局规划
- 2026-03-24: US-002 完成，FreeCAD 项目初始化
