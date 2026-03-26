# 🐟 大鱼TT 全能资料库

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/arbaleast/dayu-tt-all-in-one)
[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> 大鱼TT 310mm 封箱改装完整解决方案 — 含设计文件、装配指南、BOM物料清单、AI校准配置

---

## 📋 目录

- [项目结构](#项目结构)
- [快速导航](#快速导航)
- [最新进度](#最新进度)
- [文件说明](#文件说明)
- [参与贡献](#参与贡献)

---

## 项目结构

```
dayu-tt-all-in-one/
├── docs/                          # 文档中心
│   ├── 00-入门指南/               # 新手必读
│   ├── 01-封箱方案/               # 封箱改装方案
│   ├── 02-硬件改进/               # AI校准、改装指南 🆕
│   ├── 03-改装实战/               # 改装步骤与实录
│   ├── 04-参考资料/               # 社区资源汇总
│   └── 99-项目维护/               # GitHub同步、SSH配置
├── enclosure/                      # 封箱310专项（核心产出）
│   ├── stl/                       # 14个可打印STL文件
│   ├── dxf/                       # 6张切割图（激光/CNC）
│   ├── freecad/                   # FreeCAD源文件
│   ├── steps/                     # 装配步骤文件
│   ├── ASSEMBLY.md                # 10步装配指南
│   ├── BOM.md                     # 完整物料清单
│   ├── dimensions.md              # 尺寸规格
│   ├── layout.txt                 # 布局说明
│   ├── plan.md                    # 改装计划
│   └── README.md                  # 封箱子项目说明
├── archive/                        # 历史迁移记录
├── images/                        # 参考图片
├── models/                        # 3D模型预览
├── scripts/                        # 自动化脚本
├── CHANGELOG.enclosure.md          # 更新日志
├── PROGRESS.md                    # 封箱进度追踪
└── README.md                      # 本文件
```

---

## 快速导航

### 🔰 新手入门
1. **改装全貌** → [`docs/00-入门指南/大鱼TT从零DIY完全指南.md`](docs/00-入门指南/大鱼TT从零DIY完全指南.md)
2. **预算清单** → [`docs/00-入门指南/3-配件清单与预算.md`](docs/00-入门指南/3-配件清单与预算.md)

### 📦 封箱改装
3. **封箱方案对比** → [`docs/01-封箱方案/方案对比可视化.md`](docs/01-封箱方案/方案对比可视化.md)
4. **物料清单** → [`enclosure/BOM.md`](enclosure/BOM.md)
5. **装配指南** → [`enclosure/ASSEMBLY.md`](enclosure/ASSEMBLY.md)
6. **STL可打印文件** → [`enclosure/stl/`](enclosure/stl/)
7. **DXF切割图** → [`enclosure/dxf/`](enclosure/dxf/)

### ⚡ AI校准（2026新增）
8. **AI校准实战** → [`docs/02-硬件改进/AI校准进化实战指南.md`](docs/02-硬件改进/AI校准进化实战指南.md)
9. **OrcaSlicer配置** → [`docs/02-硬件改进/OrcaSlicer高级功能指南.md`](docs/02-硬件改进/OrcaSlicer高级功能指南.md)

---

## 最新进度

**封箱改装：** US-003~010 全部完成 ✅  
**待验证：** US-003-09 底部支架配合验证（需TT310实机）

详细进度 → [`PROGRESS.md`](PROGRESS.md)

---

## 文件说明

### enclosure/ — 封箱专项文件

| 文件/目录 | 内容 |
|---------|------|
| `stl/` | 14个3D打印零件（底部支架、风扇罩、门板配件等）|
| `dxf/` | 6张激光/CNC切割图（底板、侧板、门板等）|
| `freecad/` | FreeCAD源文件（含装配体）|
| `BOM.md` | 完整物料清单（Markdown，含成本估算）|
| `ASSEMBLY.md` | 10步装配指南 |
| `dimensions.md` | 封箱尺寸规格 |

### docs/02-硬件改进/ — AI校准与改装

| 文件 | 内容 |
|------|------|
| `AI校准进化实战指南.md` | OrcaSlicer + PrintGuard + Obico 组合配置 |
| `OrcaSlicer高级功能指南.md` | PA校准、Input Shaping、VFA分析 |
| `故障排查与维护手册.md` | 常见问题处理 |
| `腔体温控与封箱散热指南.md` | 封箱后温控配置 |

---

## 大鱼TT 简介

| 项目 | 内容 |
|------|------|
| **结构** | CoreXY |
| **打印尺寸** | 235×235×250mm / 310×310×310mm |
| **框架** | 2020/2040 铝型材 |
| **固件** | Klipper / Marlin |
| **定位** | 开源 DIY · 高性价比 · 改装潜力大 |

---

## 参与贡献

- 提交 Issue / PR → [GitHub](https://github.com/arbaleast/dayu-tt-all-in-one)
- 资料补充 → 提交到对应 `docs/` 目录
- STL/模型 → 放入 `enclosure/stl/` 或 `models/`
- 图片 → 放入 `images/`

> 项目持续更新，欢迎 Star ⭐
