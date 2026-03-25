# 大鱼TT 310 封箱进度 / Progress

**分支**: `enclosure/tt310-full-enclosure`  
**更新时间**: 2026-03-25 13:05

---

## 总览

| 阶段 | 状态 |
|------|------|
| US-003 底部支架 & 脚垫 | ✅ 完成 (8/9, 1待实物) |
| US-004~006 结构件 | ✅ 完成 |
| US-007 BOM | ✅ 完成 |
| US-008 装配指南 | ✅ 完成 |
| US-009 Klipper配置 | ✅ 完成 |
| US-010 STL验证 | 🔶 待切片验证 |

---

## US-003 底部支架 & 脚垫

| Story | 状态 | 说明 |
|-------|------|------|
| US-003-01 | ✅ | 设计规格文档 |
| US-003-02 | ✅ | 底部支架几何体 40×30×15mm |
| US-003-03 | ✅ | M3沉头孔（Ø6.5+Ø3.2，4角） |
| US-003-04 | ✅ | 侧板连接片（4角L型耳） |
| US-003-05 | ✅ | 脚垫安装座 Ø20×15mm |
| US-003-06 | ✅ | 脚垫法兰环（Ø26+Ø12通孔） |
| US-003-07 | ✅ | 脚垫 Ø25×5mm |
| US-003-08 | ✅ | 底部支架装配体 |
| US-003-09 | 🔶 | 配合验证（需TT310实物） |

---

## US-004~010 其他零部件

| Story | 状态 | 内容 | 文件 |
|-------|------|------|------|
| US-004 | ✅ | 顶部风扇安装罩 | TopFanMount.FCStd |
| US-004 | ✅ | 角码连接器 ×12 | CornerBracket.FCStd |
| US-004 | ✅ | 顶板固定件 ×8 | TopPlateMount.FCStd |
| US-004 | ✅ | 侧板固定夹 ×16 | SidePanelClip.FCStd |
| US-004 | ✅ | 过滤网框 | FilterFrame.FCStd |
| US-004 | ✅ | 通风盖 | VentCover.FCStd |
| US-004 | ✅ | 线缆入口圈 | CableEntryRing.FCStd |
| US-005 | ✅ | 门框加强条 | DoorFrameReinforcement.FCStd |
| US-005 | ✅ | 铰链安装座 ×3 | HingeMount.FCStd |
| US-005 | ✅ | 磁铁固定座 ×6 | MagnetHolder.FCStd |
| US-005 | ✅ | 门把手 | DoorHandle.FCStd |
| US-006 | ✅ | 面板DXF切割图 | dxf/*.dxf |
| US-007 | ✅ | BOM物料清单 | BOM.md |
| US-008 | ✅ | 装配说明书 | ASSEMBLY.md |
| US-009 | ✅ | Klipper温控风扇配置 | docs/klipper-fan-config.md |
| US-010 | 🔶 | STL可打印性验证 | 待切片 |

---

## 文件清单

### FreeCAD 模型 (enclosure/freecad/)

```
底部支架:
  BottomBracketBody.FCStd         # 40×30×15mm 主体
  BottomBracketComplete.FCStd    # 完整版（含M3沉头）
  BottomBracketWithTabs.FCStd    # 侧板连接耳版
  BottomBracketAssembly.FCStd    # 装配体

脚垫:
  FootMount.FCStd                # Ø20×15mm 安装座
  FootMountComplete.FCStd       # Ø12通孔+Ø26法兰
  FootPad.FCStd                 # Ø25×5mm TPU脚垫

结构件:
  TopFanMount.FCStd             # 125×125×20mm 风扇罩
  CornerBracket.FCStd           # 20×20×10mm 角码
  SidePanelClip.FCStd           # 30×15×10mm 侧板夹
  TopPlateMount.FCStd           # 25×20×8mm 顶板固定件
  FilterFrame.FCStd             # 120×120 过滤网框
  VentCover.FCStd              # 85×85×3mm 通风盖
  CableEntryRing.FCStd         # Ø35×10mm 线缆圈

门板:
  DoorFrameReinforcement.FCStd  # 490mm 加强条
  HingeMount.FCStd             # 铰链安装座
  MagnetHolder.FCStd           # 磁铁固定座
  DoorHandle.FCStd             # 60×20×15mm 把手
```

### DXF 切割图 (enclosure/dxf/)

```
SidePanel_X.dxf    510×760mm  (风扇孔+穿线孔)
SidePanel_Y.dxf    490×760mm  (×2)
TopPanel.dxf       510×490mm  (风扇孔)
BottomPanel.dxf    510×490mm  (脚垫孔)
BackPanel.dxf      490×760mm
FrontDoor.dxf      490×740mm  (铰链+磁铁孔)
```

### 文档 (enclosure/)

```
BOM.md                     完整物料清单+成本估算
ASSEMBLY.md                装配指南 (10步)
docs/klipper-fan-config.md Klipper温控风扇配置
```

---

## 待完成

- [ ] US-003-09: 实物验证（需TT310实机）
- [ ] US-010: STL切片验证（OrcaSlicer）
