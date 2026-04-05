# 大鱼TT 310 封箱进度

**分支**: `enclosure/tt310-full-enclosure`  
**当前版本**: V2 重新设计（基于 STEP 精确尺寸 + 工程分析）  
**更新**: 2026-03-26

---

## 总览

| 阶段 | V1 状态 | V2 状态 | 备注 |
|------|---------|---------|------|
| STEP 尺寸分析 | ✅ | ✅ | 478×490×760mm 实测 |
| 参数化代码 | ❌ | ✅ | Python 脚本可控 |
| 3D 打印件 STL | ✅ V1 完成 | ✅ 8个生成 | 待打印验证 |
| DXF 切割图 | ✅ V1 完成 | ✅ 7张生成 | 待发工厂确认 |
| **工程分析** | ❌ | **✅ 结构+热力完成** | 2026-03-26 |
| 实物验证 | 🔶 | 🔶 待完成 | 需 TT310 实机 |

---

## V2 重新设计成果

### 3D 打印件（8个 STL）
```
enclosure/stl_v2/
├── BottomBracketV2.stl    ✅ 底部四角支架（104x安全系数）
├── FootMountV2.stl      ✅ 脚垫安装座（含减震腔）
├── FootPadV2.stl        ✅ TPU 脚垫
├── SidePanelClipV2.stl  ✅ 快拆卡扣（~21kgf插入力）
├── TopFanMountV2.stl    ✅ 120mm 风扇罩（迷宫密封）
├── CableEntryRingV2.stl ✅ 线缆密封入口（3通道）
├── MagnetHolderV2.stl  ✅ 磁铁快拆座
└── DoorHingeMountV2.stl ✅ 门铰链座
```

### DXF 切割图（7张）
```
enclosure/dxf_v2/
├── SIDE_PANEL_X2_520x770x4.DXF   ← ✅ 已改为 4mm
├── SIDE_PANEL_Y2_530x770x4.DXF   ← ✅ 已改为 4mm
├── TOP_PANEL_520x530x3.DXF
├── BOTTOM_PANEL_520x530x5.DXF     ✅ 底板加厚
├── BACK_PANEL_530x770x3.DXF
├── FRONT_DOOR_520x745x5.DXF       ✅ 门板加厚
└── DOOR_HANDLE_OUTLINE.DXF
```

### 生成脚本
```
scripts/redesign_v2/
├── stl_writer.py       ← STL 参数化生成（纯 Python）
├── dxf_writer.py      ← DXF 切割图生成
└── analysis_v2.py     ← 工程分析脚本
```

### 文档清单
```
enclosure/
├── REDESIGN_V2.md               ← V2 完整设计方案
├── ASSEMBLY.md                 ← 装配指南（V1，待更新）
├── BOM.md                      ← 物料清单（V1，待更新）
├── dimensions.md               ← 尺寸规格
└── layout.txt                 ← 布局说明

docs/02-硬件改进/
├── V2-结构热力分析报告.md        ← 🆕 工程分析（结构+热力）
├── TT310-SOURCE-ANALYSIS.md    ← 🆕 STEP 模型分析
└── ...（其他改装指南）
```

---

## 工程分析核心结论（2026-03-26）

### 🔧 结构
| 零件 | 结论 |
|------|------|
| 底部支架 | ✅ 104x 安全系数，强度远超需求 |
| M3 螺丝连接 | ✅ 38x 安全系数 |
| 卡扣插入力 | ✅ ~21kgf，手工可拆装 |
| **3mm 侧板（风扇抽风）** | ⚠️ ΔP=50Pa 时挠度 6mm，**建议加厚到 4mm** |
| 5mm 门板 | ✅ 1.3mm 挠度，够用 |

### 🌡️ 热力
| 散热方式 | 腔温 | 结论 |
|---------|------|------|
| 自然对流（无风扇）| ~46°C | ⚠️ PLA 禁用，PETG 勉强 |
| **强制风冷 120mm** | **~27°C** | ✅ 所有材料适合！ |

> 🔥 **强制排风是必须的**，无风扇腔温接近 PLA 软化点（55°C）

### 🏗️ 材料推荐
- **PETG** → 主打印件（耐温 70°C）
- **TPU95A** → 脚垫/密封圈
- **PLA** → ⚠️ **封箱内禁止使用**（55°C 软化）

---

## ⚠️ V2 待确认事项

| 序号 | 事项 | 优先级 | 影响 |
|------|------|--------|------|
| 1 | ~~侧板加厚到 4mm？~~ | ✅ **已确认 4mm** | ✅ DXF 已更新 |
| 2 | 打印 BottomBracketV2 验证 | 🔴 最高 | 尺寸配合确认 |
| 3 | DXF 发工厂报价 | 🔴 最高 | 亚克力采购 |
| 4 | 风扇型号确认 | 🟡 高 | Klipper 配置 |
| 5 | GitHub commit | 🟢 低 | 存档 |

---

## 下一步行动

```
🔴 最高优先级（立即执行）
  1. 确认侧板厚度（3mm → 4mm？）
  2. 打印 BottomBracketV2.stl 验证尺寸
  3. DXF 发工厂切割亚克力板

🟡 高优先级（本周）
  4. 购买 PETG + TPU 耗材
  5. 打印其余 7 个 3D 打印件
  6. 配置 Klipper 风扇控制

🟠 中期（封箱完成后）
  7. 腔温实测验证（目标 ~27°C）
  8. 罗技 C270 摄像头安装
  9. AI 校准配置（OrcaSlicer）
```

---

## 关键尺寸（STEP 实测）

| 项目 | 数值 |
|------|------|
| 机器 X 外形 | 478mm |
| 机器 Y 外形 | 490mm |
| 机器 Z 总高 | 760mm（官方）|
| 型材规格 | 2020（20×20mm，槽宽 6mm）|
| 喷嘴最高点 | 460mm |
| 顶部净空 | 300mm |

---

*由 OpenClaw AI 生成/更新 | 2026-03-26*
