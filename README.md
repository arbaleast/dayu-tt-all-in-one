# 🐟 大鱼TT 310mm 封箱改装方案

[![分支](https://img.shields.io/badge/分支-enclosure%2Ftt310--full--enclosure-orange?logo=git)](https://github.com/arbaleast/dayu-tt-enclosure)
[![状态](https://img.shields.io/badge/状态-V2%20%E5%B7%A5%E7%A8%8B%E5%AE%8C%E6%88%90-brightgreen)](https://github.com/arbaleast/dayu-tt-enclosure)
[![工程分析](https://img.shields.io/badge/Engineering-V2%E7%BB%93%E6%9E%84%2B%E7%83%AD%E5%8A%9B%E5%88%86%E6%9E%90%E5%AE%8C%E6%88%90-blue)](https://github.com/arbaleast/dayu-tt-enclosure)

> 大鱼TT（TT310）封箱改装完整解决方案 — 含 V2 参数化设计、工程分析、可打印 STL、DXF 切割图、装配指南

---

## 核心产出物

| 类型 | 数量 | 路径 |
|------|------|------|
| **3D 打印件 STL** | 8 个（V2） | `enclosure/stl_v2/` |
| **DXF 切割图** | 7 张（V2） | `enclosure/dxf_v2/` |
| **FreeCAD 源文件** | 14 个 | `enclosure/freecad/` |
| **物料清单 BOM** | 含成本估算 | `enclosure/BOM.md` |
| **装配指南** | 10 步 | `enclosure/ASSEMBLY.md` |
| **AI 校准配置** | 含 OrcaSlicer | `docs/02-硬件改进/` |

---

## 🚀 快速导航

**新人入门**
1. [`大鱼TT从零DIY完全指南.md`](docs/00-入门指南/大鱼TT从零DIY完全指南.md) — 全流程概览
2. [`配件清单与预算.md`](docs/00-入门指南/3-配件清单与预算.md) — 要买什么

**封箱改装（核心）**
3. [`BOM.md`](enclosure/BOM.md) — V2 物料清单 + 成本
4. [`ASSEMBLY.md`](enclosure/ASSEMBLY.md) — 10 步装配
5. `enclosure/stl_v2/` — 8 个可直接打印的 STL
6. `enclosure/dxf_v2/` — 7 张激光/CNC 切割图

**AI 校准（特色）**
7. [`AI校准进化实战指南.md`](docs/02-硬件改进/AI校准进化实战指南.md) — OrcaSlicer + PrintGuard + Obico
8. [`OrcaSlicer高级功能指南.md`](docs/02-硬件改进/OrcaSlicer高级功能指南.md) — Input Shaping / PA 校准

**改装进阶**
9. [`腔体温控与封箱散热指南.md`](docs/02-硬件改进/腔体温控与封箱散热指南.md) — 热管理
10. [`故障排查与维护手册.md`](docs/02-硬件改进/故障排查与维护手册.md)

---

## V2 重新设计亮点（2026-03-26）

### 🔧 结构工程分析结论
- **底部支架**：104x 安全系数，强度远超需求
- **侧板加厚**：3mm → **4mm**（3mm 在风扇抽风 ΔP=50Pa 下挠度 6mm，不合格）
- **门板**：5mm 加固，挠度仅 1.3mm，够用

### 🌡️ 热力分析结论
| 散热方式 | 腔温 | 适用材料 |
|---------|------|---------|
| 自然对流（无风扇）| ~46°C | ⚠️ PLA 禁用 |
| **强制排风 120mm** | **~27°C** | ✅ 所有材料适合 |

> 🔥 **结论：强制排风是必须的**，无风扇腔温接近 PLA 软化点（55°C）

### 参数化生成
所有 STL / DXF 均由 Python 脚本生成，可按实际机型微调：
```
scripts/redesign_v2/
├── stl_writer.py      ← STL 参数化生成
├── dxf_writer.py      ← DXF 切割图生成
└── analysis_v2.py     ← 工程分析脚本
```

---

## 大鱼TT 基本规格

| 项目 | TT150 | TT310 |
|------|-------|-------|
| 打印尺寸 | 150×150×150mm | **310×310×310mm** |
| 框架 | 2020 铝型材 | 2020/2040 铝型材 |
| 固件 | Klipper / Marlin | Klipper / Marlin |
| 定位 | 开源 DIY | 开源 DIY · 高改装潜力 |

---

## 目录结构

```
docs/
├── 00-入门指南/        ← 新手必读
├── 01-封箱方案/        ← 方案对比与选型
├── 02-硬件改进/        ← AI校准、改装指南
├── 03-功能扩展/        ← 温控、摄像头等
└── 04-参考资料/        ← 社区资源

enclosure/             ← 封箱核心产出
├── stl_v2/            ← V2 可打印件（8个）
├── dxf_v2/            ← V2 切割图（7张）
├── freecad/           ← FreeCAD 源文件
├── BOM.md             ← 物料清单
├── ASSEMBLY.md        ← 装配指南
└── REDESIGN_V2.md     ← V2 设计文档
```

---

## 状态

**V2 设计** → ✅ 结构/热力分析完成
**待做** → 实物验证（打印 STL → 发工厂切亚克力 → 装配）

---

*有问题或建议 → [GitHub Issues](https://github.com/arbaleast/dayu-tt-enclosure/issues)*
