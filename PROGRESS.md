# 大鱼TT 310 封箱进度 / Progress

**分支**: `enclosure/tt310-full-enclosure`  
**更新时间**: 2026-03-25 12:57

## US-004~010 其他零部件

| Story | 内容 | 状态 |
|-------|------|------|
| US-004 | 顶部风扇安装罩 | ⏳ |
| US-005 | 密封条安装槽与门框加强件 | ⏳ |
| US-006 | 面板DXF切割图 | ⏳ |
| US-007 | BOM物料清单 | ⏳ |
| US-008 | 装配说明书 | ⏳ |
| US-009 | Klipper温控风扇配置 | ⏳ |
| US-010 | STL可打印性验证 | ⏳ |

## US-003 底部支架 & 脚垫 (Bottom Bracket & Feet)

| Story | 状态 | 说明 |
|-------|------|------|
| US-003-01 ✅ | 完成 | 底部支架设计规格文档 |
| US-003-02 ✅ | 完成 | 底部支架几何体 40x30x15mm |
| US-003-03 ✅ | 完成 | M3沉头孔（Ø6.5头+Ø3.2孔，4角） |
| US-003-04 ✅ | 完成 | 侧板连接片（4角L型耳） |
| US-003-05 ✅ | 完成 | 脚垫安装座体 Ø20x15mm |
| US-003-06 ✅ | 完成 | 脚垫法兰环（Ø26接触面+Ø12通孔） |
| US-003-07 ✅ | 完成 | 脚垫 Ø25x5mm |
| US-003-08 ✅ | 完成 | 底部支架装配体 |
| US-003-09 🔶 | 待实物验证 | 配合验证（需TT310实物） |

## 已生成文件

```
enclosure/freecad/
├── BottomBracketBody.FCStd       # 40x30x15mm 主体
├── BottomBracketComplete.FCStd   # 完整版（主体+M3沉头）
├── BottomBracketWithTabs.FCStd   # 侧板连接耳版
├── BottomBracketAssembly.FCStd   # 装配体
├── FootMount.FCStd               # Ø20x15mm 脚垫安装座（基础）
├── FootMountComplete.FCStd      # 完整版（Ø12孔+法兰）
├── FootPad.FCStd                # Ø25x5mm 脚垫
└── scripts/
    ├── create_bottom_bracket_body.py
    ├── create_bottom_bracket_m3_holes.py
    ├── create_foot_mount.py
    └── verify_bottom_bracket_fit.py  # 实物验证清单
```

## 下一步

- [x] US-003-02~08: 底部支架+脚垫FreeCAD模型
- [x] US-003-03: M3沉头孔
- [x] US-003-04: 侧板连接片
- [x] US-003-06: 脚垫法兰环
- [ ] US-003-09: 配合验证（需TT310实物）
- [ ] US-004: 顶部风扇安装罩
- [ ] US-005: 密封条安装槽与门框加强件
- [ ] US-006: 面板DXF切割图
- [ ] US-007: BOM物料清单
- [ ] US-008: 装配说明书
- [ ] US-009: Klipper温控风扇配置
- [ ] US-010: STL可打印性验证
