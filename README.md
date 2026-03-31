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

## ⚡ AI 自我进化系统（Phase 0-5 · 2026 更新）

> 目标：打印机自己学会优化参数、自己发现并修复故障
> 详细设计：`docs/plans/2026-03-27-self-evolving-design.md`

| 阶段 | 内容 | 状态 | 2026 前沿更新 |
|------|------|------|--------------|
| Phase 0 | Obico AI 故障检测上线 | ✅ 已完成 | **Obico 已在全球监测超 800 万小时打印，检测到近 100 万次故障；支持 Klipper/OctoPrint/Bambu Lab，云端或自托管均可** |
| Phase 1 | 数据采集 + NAS 监控面板 | 📋 规划中 | 可参考 Obico 的 print history + statistics 面板设计 |
| Phase 2 | 参数自优化引擎 | 📋 规划中 | Klipper 内置 `SHAPER_CALIBRATE` + ADXL345 加速度计自动调优，可实现 30~50% 提速同时保持同等质量 |
| Phase 3 | 故障自动恢复闭环 | 📋 规划中 | Obico AI 可自动暂停（auto-pause）打印；Bambu Lab 已实现 lidar + camera 实时检测 |
| Phase 4 | AI 助手对话控制 | 📋 规划中 | 语音 AI 智能体正在崛起，未来可通过对话而非文本界面控制打印机 |

---

## 🤖 2026 前沿技术动态

### Obico — AI 故障检测事实标准
- **覆盖规模**：800 万小时打印监测，100 万次故障捕获
- **支持固件**：OctoPrint、Klipper、Bambu Lab
- **部署方式**：云端（免费层 + $4/月 Pro）或自托管（AGPLv3 开源）
- **新进展**：First Layer AI inspection 已进入 alpha 测试，可验证首层粘附
- **对比竞品**：OctoEverywhere（$2.5~5/月）、PrintWatch；Obico 以开源和社区规模领先

### Klipper — Input Shaper 自动调优
- 通过 ADXL345/LIS2DW 等加速度计测量共振频率，自动生成最优 input shaper 参数
- 可在不牺牲精度的情况下实现 **30~50% 提速**
- `calibrate_shaper.py` 脚本自动推荐 shaper 类型（EI/2HUMP_EI/ZV 等）和频率
- 支持 X/Y 双轴同时校准，max smoothing 可控

### CES 2026 新技术
- **MeshyAI Creative Lab**：AI 生成 3D 模型 → 自动修复几何 + 材料推荐 + 打印参数 + 彩色化 → 直连制作服务商
- **Creality SPARKX i7**：AI 错误检测（RGB 灯带实时显示进度），支持 4 色打印，材料浪费减少 50%
- **成本下降**：2026 年 3D 打印单件成本较 3 年前下降约 40%，AI 辅助切片功不可没

### 语音 AI 正在进入 3D 打印
- 2026 年多家语音 AI 初创获融资（Play AI、WaveForms AI 被 Meta 收购）
- 客户服务/销售/IT 支持场景已实现零人工干预对话
- 未来可通过自然对话监控打印状态、调整参数

### 行业数据
- 2026 年 AI Agent 在财报电话会议中被提及次数是 2023 年的 **10 倍**
- 82% 企业表示未来 12 个月将把 AI Agent 应用于客户支持
- 垂直化 AI（医疗、金融）占 Agent AI 公司 19%，其中 32% 已进入部署阶段

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
