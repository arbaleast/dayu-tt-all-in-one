# 大鱼TT 310 封箱进度 / Progress

**分支**: `enclosure/tt310-full-enclosure`  
**更新时间**: 2026-03-25 13:10

---

## 总览

| 阶段 | 状态 |
|------|------|
| US-003 底部支架 & 脚垫 | ✅ 8/9（1待实物） |
| US-004~010 全部完成 | ✅ |

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

## US-004~010

| Story | 状态 | 内容 |
|-------|------|------|
| US-004 | ✅ | 顶部风扇安装罩 + 8种结构件 |
| US-005 | ✅ | 门框加强件 + 门板配件 |
| US-006 | ✅ | 6张DXF面板切割图 |
| US-007 | ✅ | 完整BOM物料清单 |
| US-008 | ✅ | 10步装配说明书 |
| US-009 | ✅ | Klipper温控风扇配置 |
| US-010 | ✅ | 14个STL可打印文件 |

---

## 文件清单

### FreeCAD (.FCStd) + STL (.stl)

**底部支架**: BottomBracket, FootMount, FootPad (各含基础版+完整版)  
**结构件**: TopFanMount, CornerBracket, SidePanelClip, TopPlateMount, FilterFrame, VentCover, CableEntryRing  
**门板**: DoorFrameReinforcement, HingeMount, MagnetHolder, DoorHandle

### 文档

| 文件 | 内容 |
|------|------|
| BOM.md | 物料清单+成本估算 |
| ASSEMBLY.md | 10步装配指南 |
| docs/klipper-fan-config.md | Klipper温控配置 |
| dxf/*.dxf | 6张切割图 |
| stl/*.stl | 14个STL打印文件 |

---

## 待完成

- [ ] US-003-09: 实物验证（需TT310实机）
