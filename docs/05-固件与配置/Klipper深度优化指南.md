# Klipper 深度优化指南

> 更新时间：2026-03-29
> 适用：大鱼TT / CoreXY 结构 / Klipper 固件
> 前提：已安装 Klipper 固件并完成基础配置

---

## 一、加速度与 Jerk 设置（CoreXY 优化）

### 1.1 CoreXY vs 笛卡尔机器的差异

CoreXY 结构的特点是**两个电机协同控制 X/Y 运动**，对角线移动时两个电机同时运转。因此加速度和 jerk 设置需要考虑结构应力：

- **XY 总加速度**（`max_accel`）：过高会造成立框抖动，过低则打印速度受限
- **XY 最大加速度**（`max_accel_to_decel`）：建议设为 `max_accel` 的约 50%，平滑减速防止撞击
- **Jerk**（瞬时速度变化）：CoreXY 对 jerk 敏感，高 jerk 会在拐角处产生共振纹

### 1.2 推荐参数范围

```ini
# printer.cfg — 运动学参数

[printer]
kinematics: corexy
max_velocity: 500          # 最大移动速度 mm/s（打印头总速度）
max_z_velocity: 20         # Z 轴最大速度（丝杠结构建议 15-25）
max_z_accel: 150            # Z 轴加速度（限制启停冲击）

[mover]
# ============ 打印参数（影响打印质量）===========
max_accel: 3000             # 打印加速度 mm/s²
max_accel_to_decel: 1500    # 加速转减速的过渡加速度（推荐 max_accel 的 50%）
square_corner_velocity: 5.0 # 拐角速度（mm/s），控制拐角精度

# ============ 空程参数（影响换行效率）===========
max_accel: 5000             # 空程/归位时可以更高
```

> **提示：** `square_corner_velocity` 不要设为 0，会导致所有拐角都变成圆弧，影响细节。5-8 是比较平衡的值。

### 1.3 实际调参思路

建议分三步走：

1. **保守起步**：`max_accel = 1500`，`square_corner_velocity = 5.0`
2. **压力成型测试**：打印官方测试块，观察表面质量和立柱稳定性
3. **逐步提升**：每次 +300，观测共振纹和飞边情况，找到临界值后回退 10-15%

---

## 二、输入整形（Input Shaper）参数调优

### 2.1 什么是输入整形？

输入整形是 Klipper 抑制机械共振的核心功能。打印机在高速运动时，框架和皮带会产生共振，导致表面出现**波纹（ringing/ghosting）**。输入整形通过对运动命令进行"预变形"来抵消这种共振。

### 2.2 校准流程

**步骤一：连接 ADXL345 加速度计**

将 ADXL345 正确连接到树莓派或 MCU 的 SPI 接口：

```ini
[mcu rpi]
serial: /tmp/klipper_host_mcu

[adxl345]
cs_pin: rpi:None

[resonance_tester]
accel_chip: adxl345
probe_points:
    150, 150, 20   # 喷嘴位置（改为你的实际坐标）
```

**步骤二：运行自动校准**

```bash
# 在 SSH 中执行
cd ~/klipper
python scripts/graph_accelerometer.py /tmp/adxl345_raw_data.log
# 或者通过 Mainsail/Fluidd WebUI 的输入整形校准向导
```

**步骤三：测试不同频率**

```bash
# 测试 X 轴共振
python scripts/measure_input_shaper.py -i can0 -x

# 测试 Y 轴共振
python scripts/measure_input_shaper.py -i can0 -y
```

**步骤四：应用推荐参数**

校准完成后，Klipper 会给出类似以下建议：

```ini
[input_shaper]
shaper_freq_x: 57.6  # X 轴推荐整形频率
shaper_freq_y: 58.8  # Y 轴推荐整形频率
shaper_type_x: ei    # 推荐使用 ei（2-hump notch）类型
shaper_type_y: ei
shaper_type: 2hump_ei # 全局默认（针对 CoreXY 通常分别设置 XY 更优）
```

### 2.3 常见整形器类型对比

| 类型 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| `zvd` | 简单，延迟最低 | 对高频共振抑制弱 | 刚性好、低速机器 |
| `zv` | 延迟低，实用 | 中等抑制能力 | 大多数情况 |
| `ei`（2-hump）| 宽频抑制强 | 延迟稍高 | 皮带驱动 CoreXY |
| `mzv` | 综合性能好 | 配置复杂 | 追求最优质量 |

**大鱼 TT 推荐：** `ei` 或 `2hump_ei`，平衡了共振抑制和打印延迟。

### 2.4 验证效果

打印一个 Test Ringing（别名樱花测试块、 ringing tower）：

```bash
# Klipper 官方测试文件
~/klipper/scripts/printcores.py
```

观察波纹是否在可接受范围内。如仍有波纹，可适当降低 `shaper_freq_x/y`（降低 5-10%）。

---

## 三、Pressure Advance 精细调整

### 3.1 什么是 Pressure Advance？

Pressure Advance（压力提前，简称 PA）补偿耗材从熔融腔挤出时的压缩效应。没有 PA 时，拐角和直线切换处会出现**欠挤（under-extrusion）**和**过挤（over-extrusion）**。

### 3.2 粗调：线性 PA 测试

通过打印 PA tower 或测试块，找到基础值：

```bash
# 使用 Klipper 的 PA 测试宏（需在 cfg 中定义）
# 或手动用 Slic3r 切片一个 Tower，每 10mm 变化一次 PA 值
```

典型参考值：
- 近程挤出机（Bondtech 系列）：`0.04 - 0.08`
- 远程挤出机（Bowden）：`0.06 - 0.14`

### 3.3 精细调整：流量波形分析

粗调完成后，使用 Klipper 的 `TUNING_TOWER` 命令精细调整：

```bash
# 在 Klipper 控制台（Mainsail）执行
SET_PRESSURE_ADVANCE ADVANCE=0.06
# 观察第一层质量

# 更精细的方法：参数化测试
# 使用官方压力Advance测试方块，每层递增 0.005
```

**精细调整判断标准：**

| 现象 | 说明 PA 值 | 调整方向 |
|------|-----------|---------|
| 拐角过凸 | PA 值偏高 | 降低 0.005 |
| 拐角内缩 | PA 值偏低 | 提高 0.005 |
| 直线末端变细 | PA 值偏低 | 提高 0.005 |
| 拐角处有拉丝粘连 | PA 值偏高 | 降低 |

### 3.4 PA 与进料率（Flow）的配合

PA 值独立于 Flow（流量）设置：
- **PA** = 补偿熔腔压力，与喷嘴温度、耗材品牌相关
- **Flow** = 实际挤出量百分比

建议先调 PA，再微调 Flow。两者配合好可以让拐角和细节质量显著提升。

---

## 四、热床调平（Bltouch / Klicky）

### 4.1 Bltouch 安装与配置

Bltouch 是一款五点+网格热床调平传感器，通过探针测量实现自动调平。

**接线：**
- 信号线（白）→ 主板的 SERVO（PWM）针
- 电源（红+5V / 棕 GND）
- Z probe（黑）→ 主板的 Z min 针

**printer.cfg 示例：**

```ini
[bltouch]
sensor_pin: ^PC5          # Z min 信号脚（根据主板调整）
control_pin: PC6          # Bltouch 控制针
x_offset: 0.0             # 探针相对喷嘴的 X 偏移（实测填写）
y_offset: 0.0             # 探针相对喷嘴的 Y 偏移
speed: 5.0                # 探针下降速度 mm/s
stow_on_each_sample: True
probe_with_touch_mode: True
pin_up_reports_not_triggered: True
pin_up_touch_mode_reports_triggered: False

[bed_mesh]
speed: 150
horizontal_move_z: 10
mesh_radius: 40           # 网格半径（实测床面大小调整）
mesh_origin: 0, 0
bidirectional: True
bsg_gamma: 5              # bed_screw helper 参数
```

**归位与调平宏：**

```ini
[gcode_macro HOME]
gcode:
  G28
  _PROBE_INNER      # 可选：四点探测定平
  G0 X117.5 Y117.5 Z10 F3600  # 移到中心
  
[gcode_macro AUTO_Z_TILT]
gcode:
  PROBE_CALIBRATE
  Z_TILT_ADJUST
  SAVE_CONFIG
```

### 4.2 Klicky 安装与配置

Klicky 是一种低成本探针替代方案，使用机械开关触发：

**优势：**
- 成本极低（几毛钱零件）
- 不受磁场干扰（适合磁性热床）
- 可自行 3D 打印安装支架

**配置要点：**

```ini
[probe]
pin: ^PC5
x_offset: 0
y_offset: 0
speed: 5
lift_height: 5

[klicky]
# Klicky 特有的归位序列
```

> ⚠️ Klicky 对安装精度要求高，X/Y offset 必须实测，否则调平精度会受影响。

---

## 五、CAN 总线配置（SB2040 工具板）

### 5.1 CAN 总线概述

CAN 总线将工具板（如 FLY SB2040）通过双绞线连接到主板，大幅简化走线。对于大鱼 TT，推荐使用 **CAN 总线方案**，参考 docs/02-硬件改进/CAN总线改装指南.md。

### 5.2 关键配置要点

**主机端（主板）：**

```ini
[mcu]
serial: /dev/serial/by-id/your-mainboard-id
baud: 250000

[CAN bus]
can0_tx_pin: gpio4
can0_rx_pin: gpio5
can0_speed: 1000000
```

**工具板端（SB2040）：**

```ini
[mcu SB2040]
canbus_uuid: 8248a4b16ede   # 替换为实际 UUID
```

### 5.3 终端电阻

CAN 总线两端需要 120Ω 终端电阻确保信号完整性。确认 SB2040 端的终端电阻跳线已焊接。

### 5.4 常见问题排查

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| 查询不到 UUID | CAN_H/L 接反 | 互换 CAN_H 和 CAN_L |
| 刷写失败 | 电源或终端电阻问题 | 检查 24V 供电和终端电阻 |
| 通讯不稳定 | 波特率不匹配 | 确认主机和 SB2040 都是 1Mbps |

---

## 六、综合优化建议

1. **分步调参**：先机械后软件——先确认皮带张力、电机固定、散热安装，再调软件参数
2. **保存基准**：每次调参前 `SAVE_CONFIG`，出问题可回退
3. **记录变更**：用注释记录每次调整的参数和观察结果
4. **测试文件统一**：用同一个测试文件（如官方校准方块）对比效果
5. **固件更新**：Klipper 更新频繁，重大版本更新后建议重新校准输入整形

---

## 相关文档

- [CAN 总线改装指南](../02-硬件改进/CAN总线改装指南.md)
- [Klipper 固件配置完全指南](../02-硬件改进/Klipper固件配置完全指南.md)
- [BOSSAC 热床与热管理](./BOSSAC热床与热管理.md)
