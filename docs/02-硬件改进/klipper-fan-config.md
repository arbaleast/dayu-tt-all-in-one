# Klipper 温控风扇配置 / Klipper Temperature-Controlled Fan Config

> 大鱼TT 310 全封闭机箱 - 温控风扇智能切换
> 适用: Klipper 固件 + Moonraker + Fluidd/Mainsail

---

## 一、配置思路

### 封闭机箱散热挑战

| 场景 | 风扇策略 | 阈值 |
|------|----------|------|
| 常规打印 | 低速过滤 | 30% 占空比，持续通风 |
| 高温打印 (PLA) | 关闭或低速 | 喷嘴 < 200°C |
| 高温打印 (PETG/ABS) | 中速 | 喷嘴 210-250°C |
| 热床高温 | 低速辅助 | 热床 > 55°C |
| 腔体温控 | 按温度开关 | 腔体 > 45°C 开启 |

### 推荐风扇

** Noctua NF-A12×25 120mm 4针 PWM 温控风扇 ×1-2

---

## 二、fan 对象配置

在 `printer.cfg` 中添加：

```ini
# ─────────────────────────────────────────────────────────────
# 机箱排风扇 (Chamber Exhaust Fan)
# 连接到: fan0 (或自定义)
# ─────────────────────────────────────────────────────────────
[fan]
fan0:
    pin: EXP1_2           # 根据实际接线调整
    max_power: 1.0
    kick_start_time: 0.5
    off_below: 0.15
    # 调速范围: 15%~100%
    # PWM 频率
    hardware_pwm: False
    shutdown_speed: 0

# ─────────────────────────────────────────────────────────────
# 温度传感器 - 腔体温度 (使用热敏电阻贴在机箱内侧)
# ─────────────────────────────────────────────────────────────
[temperature_sensor chamber]
sensor_type: NTC 100K MGB18-100F39550
# 或使用热电偶 (TC):
# sensor_type: MAX6675
pin: EXP1_1              # 根据实际接线调整
min_temp: 0
max_temp: 100
gcode_id: T_chamber

# ─────────────────────────────────────────────────────────────
# 腔体温控风扇 (根据腔体温度自动调速)
# ─────────────────────────────────────────────────────────────
[controller_fan ChamberCooling]
# 风扇
fan: fan0
# 温度传感器
sensor: temperature_sensor chamber
# 温度阈值
idle_temperature: 35
fan_speed: 0.30          # 待机低速 30%
min_speed: 0.15
max_speed: 1.0
# 温控曲线: 温度越高风扇越快
temperature_offset: 3.0
control_width: 0.5

# ─────────────────────────────────────────────────────────────
# 喷嘴温度联动风扇 (打印时根据 nozzle temp 调速)
# ─────────────────────────────────────────────────────────────
[heater_fan hotend_fan]
# 热端风扇 - 跟喷嘴温度联动
fan: fan0
heater: extruder
idle_speed: 0.25         # 待机 25%
min_speed: 0.15
max_speed: 0.75          # 热端全速时上限 75%

---

## 三、Moonraker / API 自定义温控 (可选)

如果需要更精细的控制，可通过 Moonraker 添加自定义温控逻辑。

```json
// POST /api/fan/set_smart_fan
{
  "fan": "chamber",
  "mode": "auto",          // auto / manual / disabled
  "thresholds": {
    "low": 35,             // °C 以下
    "medium": 45,          // °C
    "high": 55,            // °C
    "critical": 65         // °C 紧急
  },
  "speeds": {
    "low": 0.20,
    "medium": 0.45,
    "high": 0.75,
    "critical": 1.0
  }
}
```

---

## 四、G-code 宏

```ini
# ─────────────────────────────────────────────────────────────
# 快捷宏 - 在 console 或 slicer 中调用
# ─────────────────────────────────────────────────────────────

[gcode_macro FAN_ON]
gcode:
    SET_FAN_SPEED FAN=fan0 SPEED=1.0
    {action_respond_info("风扇全速开启")}

[gcode_macro FAN_OFF]
gcode:
    SET_FAN_SPEED FAN=fan0 SPEED=0
    {action_respond_info("风扇关闭")}

[gcode_macro FAN_CHAMBER]
gcode:
    {% set temp = params.TEMP|default(45)|float %}
    {% set speed = (temp - 30) / 40 * 0.8 + 0.15 %}
    {% set speed = [[speed, 0.15]|max, 1.0]|min %}
    SET_FAN_SPEED FAN=fan0 SPEED={speed}
    {action_respond_info("腔体风扇: %.0f%%" % (speed * 100))}

[gcode_macro ENCLOSURE_PETG]
gcode:
    # PETG 封闭机箱打印设定
    SET_FAN_SPEED FAN=fan0 SPEED=0.40
    {action_respond_info("PETG模式: 腔体风扇 40%")}

[gcode_macro ENCLOSURE_ABS]
gcode:
    # ABS 高温打印 - 腔体加热 + 风扇
    SET_FAN_SPEED FAN=fan0 SPEED=0.60
    {action_respond_info("ABS模式: 腔体风扇 60%")}

[gcode_macro ENCLOSURE_PLA]
gcode:
    # PLA 低温打印 - 过滤通风
    SET_FAN_SPEED FAN=fan0 SPEED=0.25
    {action_respond_info("PLA模式: 腔体风扇 25% (过滤通风)")}
```

---

## 五、 slicer 后处理 (可选)

在 OrcaSlicer / PrusaSlicer 的后处理脚本中添加：

```
; 温控风扇后处理
M810 ; 记录宏调用
{if nozzle_temp_layer0 >= 210} M810 ; PETG
{elsif nozzle_temp_layer0 >= 245} M811 ; ABS
{endif}
```

---

## 六、调参建议

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | 空载运行风扇 | 无共振噪音 |
| 2 | 手动调速 15%~100% | 确认无抖动 |
| 3 | 热端升温 200°C | 风扇应自动提速 |
| 4 | 模拟腔体升温 | 确认温控响应 |
| 5 | 完整打印测试 | 监听噪音，优化阈值 |

---

## 七、常见问题

**Q: 风扇低速抖动**
A: 设置 `off_below: 0.15` 避免低速区不稳定

**Q: 风扇不转**
A: 检查 `kick_start_time: 0.5`，检查 PWM 信号

**Q: 腔体温度不准**
A: 热敏电阻位置影响大，贴在机箱内壁中央位置

**Q: Noctua 噪音**
A: NF-A12 有三级调速线，可接 PWM 或 DC 调速
