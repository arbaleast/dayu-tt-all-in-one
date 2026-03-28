# 🐟 大鱼TT / Dayu TT 资料库

[![GitHub](https://img.shields.io/badge/GitHub-arbaleast%2Fdayu--tt--all--in--one-blue?logo=github)](https://github.com/arbaleast/dayu-tt-all-in-one)
[![工程分析](https://img.shields.io/badge/Engineering-V2%E7%BB%93%E6%9E%84%2B%E7%83%AD%E5%8A9B%E5%88%86%E6%9E%90%E5%AE%8C%E6%88%90-blue)](https://github.com/arbaleast/dayu-tt-all-in-one)

> 大鱼TT（TT150/TT310/TT235）DIY 改装完整资料库 — 封箱方案、配件清单、AI 校准、改装实战

---

## 📂 项目结构

| 目录 | 内容 | 状态 |
|------|------|------|
| `docs/00-入门指南/` | 从零起步：装机指南、配件预算、固件配置 | ✅ |
| `docs/01-封箱方案/` | 各种封箱方案对比：李炫键降噪、汪汪队射手、开源源文件 | ✅ |
| `docs/02-硬件改进/` | AI校准、Klipper固件、故障排查、改装实战 | ✅ |
| `source/` | B站全套原始资料（STEP/SolidWorks 文件、CNC 图纸） | ✅ |
| `bom/` | **完整物料清单 CSV**（封箱配件分项） | ✅ |
| `enclosure/freecad/` | FreeCAD 参数化模型（底部支架等零件） | ✅ |
| `models/` | 打印件 STL（待整理） | ⚠️ 待补充 |
| `stls/` | 社区打印件 STL（待整理） | ⚠️ 待补充 |
| `docs/plans/` | 自我进化系统完整设计文档 | ✅ |

---

## 🚀 快速导航

**装机入门**
- [大鱼TT从零DIY完全指南](docs/00-入门指南/大鱼TT从零DIY完全指南.md)
- [配件清单与预算](docs/00-入门指南/3-配件清单与预算.md)
- [软件固件配置](docs/00-入门指南/2-软件固件配置.md)

**封箱改装**
- [封箱方案对比](docs/01-封箱方案/) — 李炫键降噪 / 汪汪队射手 / 官方方案
- [BOM 物料清单](bom/完整物料清单.csv) — 封箱配件分项 CSV
- [装配指南](docs/01-封箱方案/装配指南.md)
- [皮带张紧器设计](docs/01-封箱方案/皮带张紧器设计.md)
- `enclosure/freecad/` — FreeCAD 参数化模型

**改装进阶**
- [AI校准进化实战指南](docs/02-硬件改进/AI校准进化实战指南.md) — 完整自我进化系统（Obico + 进化引擎）
- [Klipper固件配置完全指南](docs/02-硬件改进/Klipper固件配置完全指南.md)
- [封箱散热与BOSSAC热床改装指南](docs/02-硬件改进/封箱散热BOSSAC热床改装指南.md)
- [CoreXY改进大鱼TT实战指南](docs/02-硬件改进/CoreXY改进大鱼TT实战指南.md) — Voron Design 参考改装

**原始资料**
- [B站 TT235/TT310 资料](source/) — STEP / SolidWorks / 装配图

---

## ⚡ AI 自我进化系统（Phase 0-5 混合方案）

> 目标：打印机自己学会优化参数、自己发现并修复故障
> 详细设计：`docs/plans/2026-03-27-self-evolving-design.md`

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 0 | Obico AI 检测上线（当晚完成） | ✅ 已完成（见 AI校准进化实战指南.md）|
| Phase 1 | 数据采集 + NAS 监控面板 | 📋 规划中 |
| Phase 2 | 参数自优化引擎 | 📋 规划中 |
| Phase 3 | 故障自动恢复闭环 | 📋 规划中 |
| Phase 4 | AI 助手对话控制 | 📋 规划中 |

---

## 🌡️ TT310 封箱热力结论

| 散热方式 | 腔温 | 可用材料 |
|---------|------|---------|
| 自然对流 | ~46°C | ⚠️ PLA 禁用，PETG 勉强 |
| **强制排风 120mm** | **~27°C** | ✅ 所有材料适合 |

> 🔥 强制排风是必须的，封箱后必须加风扇排风

---

## 大鱼TT 基本规格

| 型号 | 打印尺寸 | 框架 | 固件 |
|------|---------|------|------|
| TT150 | 150×150×150mm | 2020 铝型材 | Klipper / Marlin |
| TT235 | 235×235×250mm | 2020 铝型材 | Klipper / Marlin |
| **TT310** | **310×310×310mm** | **2020/2040 铝型材** | **Klipper / Marlin** |

---

## 工程分析亮点

- **底部支架**：104× 安全系数
- **侧板**：3mm → **4mm**（ΔP=50Pa 风扇抽风下挠度 6mm → 合格）
- **参数化脚本**：STL / DXF 由 Python 生成，可自由调整尺寸

---

## ⚠️ 目录状态说明

| 目录/文件 | 状态 | 说明 |
|-----------|------|------|
| `models/` | ⚠️ 待整理 | 暂无 STL 文件，需从 B站/MakerWorld 补充 |
| `stls/` | ⚠️ 待整理 | 社区打印件，待补充 |
| `enclosure/stl_v2/` | ❌ 不存在 | STL 需从 MakerWorld 下载 |
| `enclosure/dxf_v2/` | ❌ 不存在 | DXF 需从 FreeCAD 生成 |

> 📌 STL/DXF 文件需从 [MakerWorld 大鱼TT页面](https://makerworld.com.cn/zh/search?query=%E5%A4%A7%E9%B1%BCTT) 或 B站视频描述链接下载。

---

*有问题 → [GitHub Issues](https://github.com/arbaleast/dayu-tt-all-in-one/issues) · 欢迎 Star ⭐*
