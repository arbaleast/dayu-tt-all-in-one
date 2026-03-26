# AI校准进化实战指南

> 大鱼TT 3D打印AI校准配置手册
> 更新: 2026-03-26

---

## 适合大鱼TT的AI校准组合

```
OrcaSlicer (事前校准) + PrintGuard (本地检测) + Obico (远程通知)
```

---

## 一、OrcaSlicer — 精细校准配置

**推荐校准顺序：**

1. **温度塔** → 确定最佳打印温度
2. **Pressure Advance** → 消除高速过冲（PA 对大鱼TT高速打印尤为重要）
3. **Flow 校准** → 确保挤料量精准
4. **Retraction 测试** → 消除拉丝
5. **Input Shaping** → 配合 Klipper 减少振纹（OrcaSlicer Alpha 2.3.1 已内置）
6. **VFA 测试** → 精细调整锐度

**大鱼TT特定建议：**
- PA 值对 CoreXY 结构敏感，实测值可能与默认值差异大
- 封箱后腔温升高，需要重新校准温度（比裸机打印高 5~10°C）
- PA-CF / PA-GF 等碳纤维材料需要单独校准 Flow

**配合 Klipper：**
```bash
# 测量 Input Shaping 频率
SHAPER_CALIBRATE

# 测量 Pressure Advance
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 END=0.2 STEP=0.01
```

---

## 二、PrintGuard — 本地AI检测（推荐）

**优势：**
- 完全本地运行，无需网络
- 比 Obico 前身 Spaghetti Detective 快 40×
- 资源占用 <1GB RAM（适合树莓派）

**部署步骤：**
1. 树莓派安装 OctoPrint 或 Moonraker
2. 接入 USB 摄像头
3. 安装 PrintGuard 插件
4. 开启实时监控

**检测能力：**
- Spaghetti（面团缠绕）✅
- 打印脱落 ✅
- 层移 ✅

---

## 三、Obico — 远程通知

**推荐原因：**
- 首层 AI 检测（First Layer AI）
- 外出时推送失败通知
- 用户反馈帮助模型进化
- 支持 Klipper / OctoPrint

**与 PrintGuard 的区别：**
- PrintGuard = 本地实时，误报低
- Obico = 云端分析，功能更全，但需联网

---

## 四、封箱体打印的特殊注意事项

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 首层粘不住 | 腔温升高，热床温度基准变 | 降低热床温度 5°C 或增加首层流量 |
| 打印中途脱落 | 热端温度波动 | 检查热敏电阻，建议加装腔温传感器 |
| 碳纤维材料堵头 | 研磨性强 + 高温 | 用硬化钢喷嘴，定期清理喉管 |
| 长时间打印精度下降 | 皮带张力变化 | 打印前检查皮带张力，张紧器调整 |

---

## 五、AI校准进化路线图

### 阶段1（现在）
- [x] OrcaSlicer 精细校准
- [x] PrintGuard / Obico 接入
- [x] 罗技C270 摄像头配置

### 阶段2（下一步）
- [ ] 封箱后腔温传感器接入 Klipper
- [ ] 实测 PA 值，建立大鱼TT PA 曲线
- [ ] 碳纤维材料 Flow 校准

### 阶段3（高级）
- [ ] Multitask Bayesian 优化实验
- [ ] CMU VLM 路线追踪（等开源复现）
- [ ] 封箱后材料参数数据库建立

---

## 六、相关文档

| 文档 | 说明 |
|------|------|
| `OrcaSlicer高级功能指南.md` | OrcaSlicer 完整配置 |
| `罗技C270-大鱼TT摄像头完整配置.md` | 摄像头接入指南 |
| `Klipper固件配置完全指南.md` | Klipper 配置 |
| `故障排查与维护手册.md` | 常见问题处理 |
| `腔体温控与封箱散热指南.md` | 封箱散热配置 |
