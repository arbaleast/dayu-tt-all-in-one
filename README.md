# 🐟 大鱼TT / Dayu TT 资料库

[![GitHub](https://img.shields.io/badge/GitHub-arbaleast%2Fdayu--tt--all--in--one-blue?logo=github)](https://github.com/arbaleast/dayu-tt-all-in-one)
[![工程分析](https://img.shields.io/badge/Engineering-V2%E7%BB%93%E6%9E%84%2B%E7%83%AD%E5%8A%9B%E5%88%86%E6%9E%90%E5%AE%8C%E6%88%90-blue)](https://github.com/arbaleast/dayu-tt-all-in-one)

> 大鱼TT（TT150/TT310/TT235）DIY 改装完整资料库 — 封箱方案、配件清单、AI 校准、改装实战

---

## 📂 项目结构

| 目录 | 内容 |
|------|------|
| `docs/00-入门指南/` | 从零起步：装机指南、配件预算、固件配置 |
| `docs/01-封箱方案/` | 各种封箱方案对比：李炫键降噪、汪汪队射手、开源源文件 |
| `docs/02-硬件改进/` | AI校准、Klipper固件、故障排查、改装实战 |
| `docs/03-功能扩展/` | 腔体温控、摄像头、热管理系统 |
| `source/` | B站全套原始资料（STEP/SolidWorks 文件、CNC 图纸） |
| `enclosure/` | **TT310 封箱专项**：V2 STL/DXF/BOM/装配指南 |

---

## 🚀 快速导航

**装机入门**
- [大鱼TT从零DIY完全指南](docs/00-入门指南/大鱼TT从零DIY完全指南.md)
- [配件清单与预算](docs/00-入门指南/3-配件清单与预算.md)
- [软件固件配置](docs/00-入门指南/2-软件固件配置.md)

**TT310 封箱改装**（核心）
- [V2 物料清单 BOM](enclosure/BOM.md)
- [10步装配指南](enclosure/ASSEMBLY.md)
- `enclosure/stl_v2/` — 8个可打印 STL（底部支架、风扇罩、门铰链座等）
- `enclosure/dxf_v2/` — 7张激光/CNC切割图

**改装进阶**
- [AI校准实战指南](docs/02-硬件改进/AI校准进化实战指南.md) — OrcaSlicer + PrintGuard + Obico
- [Klipper固件配置完全指南](docs/02-硬件改进/Klipper固件配置完全指南.md)
- [腔体温控与封箱散热指南](docs/02-硬件改进/腔体温控与封箱散热指南.md)

---

## ⚡ AI 校准配置（特色功能）

| 文件 | 用途 |
|------|------|
| `AI校准进化实战指南.md` | PrintGuard 失败检测 + Obico 远程监控 |
| `OrcaSlicer高级功能指南.md` | Input Shaping、PA 校准、VFA 分析 |
| `klipper-fan-config.md` | Klipper 风扇控制配置 |

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

- **底部支架**：104x 安全系数
- **侧板**：3mm → **4mm**（ΔP=50Pa 风扇抽风下挠度 6mm → 合格）
- **参数化脚本**：STL / DXF 由 Python 生成，可自由调整尺寸

---

*有问题 → [GitHub Issues](https://github.com/arbaleast/dayu-tt-all-in-one/issues) · 欢迎 Star ⭐*
