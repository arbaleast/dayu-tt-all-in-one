# 大鱼TT 310 封箱进度 / Progress

**分支**: `enclosure/tt310-full-enclosure`  
**更新时间**: 2026-03-25

## US-003 底部支架 & 脚垫 (Bottom Bracket & Feet)

| Story | 状态 | 说明 |
|-------|------|------|
| US-003-01 ✅ | 完成 | 底部支架设计规格文档 |
| US-003-02 ✅ | 完成 | 底部支架几何体 40x30x15mm |
| US-003-03 🔄 | 部分 | M3沉头孔（需FreeCAD GUI精调） |
| US-003-04 ⏳ | 待做 | 侧板连接片 |
| US-003-05 ✅ | 完成 | 脚垫安装座体 Ø20x15mm |
| US-003-06 ⏳ | 待做 | 脚垫法兰环 |
| US-003-07 ✅ | 完成 | 脚垫 Ø25x5mm |
| US-003-08 ✅ | 完成 | 底部支架装配体 |
| US-003-09 ⏳ | 待做 | 配合验证（需实物） |

## 已生成文件

```
enclosure/freecad/
├── BottomBracketBody.FCStd      # 40x30x15mm 主体
├── BottomBracketAssembly.FCStd  # 装配体
├── FootMount.FCStd              # Ø20x15mm 脚垫安装座
├── FootPad.FCStd               # Ø25x5mm 脚垫
└── scripts/
    ├── create_bottom_bracket_body.py
    ├── create_bottom_bracket_m3_holes.py
    └── create_foot_mount.py
```

## 下一步

- [ ] US-003-03: M3沉头孔（FreeCAD GUI精调）
- [ ] US-003-04: 侧板连接片
- [ ] US-003-06: 脚垫法兰环
- [ ] US-003-09: 配合验证
- [ ] US-004~010: 其他零部件
