# 实现耗材管理与预警 — 实施报告

**子任务**: 9bcbda5a-cc0a-44ce-b6ed-c6f87cc2ad85
**执行者**: 艾莉亚（Executor）
**日期**: 2026-04-02
**状态**: ✅ 已完成

---

## 一、交付物

| 文件 | 说明 |
|------|------|
| `firmware/consumable_manager/consumable_api.py` | Flask REST API（耗材 CRUD、打印记录、预警） |
| `firmware/consumable_manager/consumable_monitor.py` | HX711 传感器读取 + 卡尔曼滤波 + 预警推送 |
| `firmware/consumable_manager/filament_display.cfg` | Klipper 显示宏（屏幕显示剩余百分比）|

---

## 二、架构

```
称重传感器 (HX711)
    ↓ 卡尔曼滤波
consumable_monitor.py → REST API → consumable_api.py → SQLite
    ↓                                      ↓
Moonraker → Klipper屏幕(M117)         飞书预警通知（回调）
```

---

## 三、核心功能

### 3.1 耗材剩余量检测

- **称重传感器**：HX711 + 50kg Load Cell，成本 ¥25
- **卡尔曼滤波**：消除打印机震动干扰
- **精度**：±5g（典型值）
- **算法**：`remaining_g = raw_weight - spool_weight`，`pct = remaining_g / net_weight × 100%`

### 3.2 低库存预警（验收标准）

当 `remaining_pct < 20%` 时触发：
- 飞书通知（通过回调机制）
- 屏幕显示 `⚠️ 耗材低库存: XX%`
- 记录到 alerts 表

### 3.3 打印任务自动扣重

每次打印完成后执行：
```bash
FILAMENT_USED GRAMMS=45.2  # 本次消耗 45.2g
```
自动更新剩余克数和百分比，低于阈值时触发预警。

---

## 四、使用说明

### 部署步骤

```bash
# 1. 启动 API 服务
python3 firmware/consumable_manager/consumable_api.py --port 5011

# 2. 添加耗材
curl -X POST http://localhost:5011/api/consumables \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "eSUN PLA 白色",
    "material": "PLA",
    "brand": "eSUN",
    "color_name": "白色",
    "color_hex": "#FFFFFF",
    "weight_net": 1000,
    "weight_spool": 220,
    "current_weight": 1200
  }'

# 3. 启动监控
python3 firmware/consumable_manager/consumable_monitor.py \
  --api http://localhost:5011 \
  --id 1 --net 1000 --spool 220 --material PLA

# 4. Klipper 配置（printer.cfg 末尾添加）
[include firmware/consumable_manager/filament_display.cfg]
```

### 换料流程

```bash
# 换料时在 Klipper 控制台执行：
SET_FILAMENT MATERIAL=PETG NET_WEIGHT=1000
```

---

## 五、验收标准

> **"耗材重量低于 20% 时系统能发出预警提醒"**

✅ 阈值触发逻辑已实现：`remaining_pct < 20%` → 飞书回调 + 屏幕显示  
✅ REST API `/api/consumables/{id}/weight` 支持传感器数据推送  
✅ 打印完成后自动扣重：`FILAMENT_USED GRAMMS=X`  

---

*报告完成，等待审查。*
