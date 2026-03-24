# 大鱼TT Klipper 固件配置完全指南

> 更新时间：2026-03-24
> 适用：大鱼TT + Klipper + 小政K6 / 八爪鱼 / FLY主板
> 参考：大鱼DIY B站视频 + 思兼 Klipper 保姆教程

---

## 一、大鱼TT 调平方案对比

| 方案 | 原理 | 精度 | 难度 | 推荐度 |
|------|------|------|------|--------|
| **接近开关** | 金属触发 | 一般 | ⭐ 简单 | ⭐⭐⭐ |
| **Klicky 探针** | 机械开关+舵机 | 高 | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ |
| **BL-Touch** | 磁吸针 | 高 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **IDM 快速调平** | 光栅传感器 | 最高 | ⭐⭐⭐ | ⭐⭐⭐⭐ |

> ⚠️ **新手建议从接近开关开始**，有经验后升级 Klicky 体验自动调平

---

## 二、Klipper 基础配置检查

> 原文链接：https://www.klipper3d.org/zh/Config_checks.html

### 2.1 验证基础配置

连接 SSH，在 Fluidd 控制台执行：

```bash
# 检查主板连接
M122

# 查看温度传感器
QUERY_ADC

# 测试步进电机
STEPPER_BUZZ STEPPER=stepper_x
```

### 2.2 检查限位开关

```bash
# 查看限位状态（手动触发看数值变化）
ENDSTOPS

# 归位测试
G28
```

---

## 三、PID 校准

> 原文：https://mellow.klipper.cn/docs/DebugDoc/reference_configuration/optimum_usage/calibration/

### 3.1 挤出机 PID 校准

```bash
# 设置目标温度（根据耗材调整，PLA用220，PETG用250）
PID_CALIBRATE HEATER=extruder TARGET=220
```

校准完成后，自动保存到 printer.cfg。

### 3.2 热床 PID 校准

```bash
# 目标温度（根据热床类型调整，玻璃床60，硅胶床100）
PID_CALIBRATE HEATER=heater_bed TARGET=60
```

### 3.3 保存 PID 参数

校准完成后，Klipper 会提示将参数添加到 printer.cfg，或者手动添加：

```ini
[extruder]
control: pid
pid_kp: 23.5
pid_ki: 1.2
pid_kd: 68.5

[heater_bed]
control: pid
pid_kp: 78.5
pid_ki: 3.2
pid_kd: 350.0
```

---

## 四、挤出机步进值校准

### 4.1 理论计算

```
rotation_distance = 步进电机一圈的行程
                 = 周长 / 减速比
                 = (齿轮周长) / (驱动齿轮齿数 / 电机齿轮齿数)

# 大鱼TT标准减速比 50:10（5:1）
# 主动齿轮 10T，从动齿轮 50T
rotation_distance = (10mm × π) / 5 = 6.2832mm
```

### 4.2 实际测量校准

```bash
# 1. 标记100mm长 filament
# 2. 执行 extrusion test
TESTZ=-10  # 先回退10mm避免堵料
M109 S220
G1 E100 F100  # 挤出100mm
```

测量实际挤出量，调整 `rotation_distance` 直到准确。

### 4.3 校准后配置

```ini
[extruder]
rotation_distance: 22.67895  # 根据实际情况调整
microsteps: 16
full_steps_per_rotation: 200
gear_ratio: 50:10
```

---

## 五、网床校准（Mesh Bed Leveling）

### 5.1 生成网床

```bash
# 手动调平后，生成网床
BED_MESH_CALIBRATE
```

### 5.2 探针偏移（Probe Offset）

```bash
# 测试Z偏移
PROBE_CALIBRATE

# 之后运行
BED_MESH_CALIBRATE
```

### 5.3 printer.cfg 中的网床配置

```ini
[bed_mesh]
speed: 150
horizontal_move_z: 5
mesh_min: 10, 10
mesh_max: 225, 225
probe_count: 5, 5
algorithm: lagrange
tension: 0.2

[probe]
pin: ^PG6
x_offset: 0
y_offset: 0
z_offset: 0
speed: 10
```

---

## 六、输入整形（Input Shaper）

> 用途：消除打印过程中的共振，提升高速打印质量
> 参考：B站 `大鱼DIY - Klipper固件系列`

### 6.1 测试共振

```bash
# 测试 X 轴
RESONANCES AXIS=X

# 测试 Y 轴
RESONANCES AXIS=Y

# 注意：需要 ADXL345 加速度计才能运行此命令
```

### 6.2 分析结果

Klipper 会输出建议的输入整形器类型和参数，如：

```
Recommended input shaper for X: `input_shaper_type: zv, shaper_freq: 57.2 Hz`
```

### 6.3 配置示例

```ini
[input_shaper]
shaper_freq_x: 57.2
shaper_type_x: zv
shaper_freq_y: 53.8
shaper_type_y: zv
```

---

## 七、压力提前（Pressure Advance）

> 用途：减少过挤/欠挤，提升转角质量

### 7.1 测试方法

```bash
# 执行压力提前测试
PRESSURE_ADVANCE_CALIBRATE
```

Klipper 会打印测试图案，根据结果调整参数。

### 7.2 配置示例

```ini
[extruder]
pressure_advance: 0.05
pressure_advance_smooth_time: 0.004
```

### 7.3 经验值参考

| 耗材 | pressure_advance |
|------|-----------------|
| PLA | 0.02 - 0.04 |
| PETG | 0.04 - 0.06 |
| ABS | 0.05 - 0.08 |
| TPU | 0.08 - 0.15 |

---

## 八、Klicky 探针配置

> 视频教程：B站 `【开源】保姆级Klicky配置指南`（BV1qjUHYHEbG）
> 文档参考：Scribd `大鱼TT Klicky配置教程`

### 8.1 Klicky 优点

- 比接近开关更精准
- 避免热飘问题（接近开关最大缺陷）
- Z 偏移自动补偿
- 可做倾斜校准

### 8.2 硬件要求

| 配件 | 说明 |
|------|------|
| Klicky 支架 | 3D 打印（MakerWorld 下载）|
| MG90s / SG90 舵机 | **不要用 MG996**（电流过大）|
| Klicky 探针 | 机械开关 |
| 舵机延长线（可选）| 杜邦线 |

### 8.3 printer.cfg 配置

```ini
[probe]
pin: PG6
x_offset: 0
y_offset: 0
z_offset: 0
speed: 5
lift_speed: 15
drop_speed: 15
```

```ini
[servo klicky_servo]
pin: PC5
maximum_servo_angle: 180
minimum_pulse_width: 0.001
maximum_pulse_width: 0.002
initial_angle: 10

[force_move]
force_move_timeout: 10
```

### 8.4 Klicky 宏

```ini
[homing_override]
axes: z
gcode:
  Attach_Probe
  G28 Z
  Probe
  Detach_Probe

[respond]
```

### 8.5 详细视频教程

| 标题 | BV号 |
|------|------|
| 【开源】保姆级Klicky配置指南！大鱼TT适用 | BV1qjUHYHEbG |
| 大鱼TT，z限位+舵机klicky，可自动调平 | BV198411k7Sf |
| Klipper保姆教程 实例讲解 快速上手 | - |

---

## 九、完整 printer.cfg 参考

> 大鱼DIY 官方配置参考：https://github.com/arbaleast/bigfish-tt-extentions

```ini
# 大鱼TT 基础配置（简化版）
# 蓝色部分需根据实际硬件调整

[stepper_x]
step_pin: PF0
dir_pin: PF1
enable_pin: !PD0
microsteps: 16
rotation_distance: 40
endstop_pin: ^PG9

[stepper_y]
step_pin: PF2
dir_pin: PF3
enable_pin: !PC0
microsteps: 16
rotation_distance: 40
endstop_pin: ^PG10

[stepper_z]
step_pin: PC6
dir_pin: PA14
enable_pin: !PA15
microsteps: 16
rotation_distance: 8
endstop_pin: ^PG2

[extruder]
step_pin: PA9
dir_pin: PA10
enable_pin: !PC4
microsteps: 16
rotation_distance: 22.67895
gear_ratio: 50:10
heater_pin: PA1
sensor_type: EPCOS100K
sensor_pin: PC2
control: pid
pid_kp: 23.5
pid_ki: 1.2
pid_kd: 68.5

[heater_bed]
heater_pin: PA2
sensor_type: NTC100K
sensor_pin: PC5
control: pid
pid_kp: 78.5
pid_ki: 3.2
pid_kd: 350.0

[fan]
pin: PC7

[probe]
pin: PG6
x_offset: 0
y_offset: 0
z_offset: 0

[input_shaper]
shaper_freq_x: 57.2
shaper_type_x: zv
shaper_freq_y: 53.8
shaper_type_y: zv

[bed_mesh]
speed: 150
mesh_min: 10, 10
mesh_max: 225, 225
probe_count: 5, 5
```

---

## 十、大鱼DIY 官方 Klipper 视频教程

| 标题 | BV号 | 内容 |
|------|------|------|
| 搭载Klipper固件的高速3D打印机DIY之大鱼TT | BV1ak4y1A78e | 完整装机+调试+固件 |
| Klipper固件之摄像头配置指南 | BV1RC4y1E7tj | 摄像头配置 |
| 【开源】保姆级Klicky配置指南 | BV1qjUHYHEbG | Klicky自动调平 |
| 大鱼TT，z限位+舵机klicky | BV198411k7Sf | Klicky+Z倾斜校准 |
| Klipper保姆教程 快速上手 | - | 新手入门 |
| klipper配置之printer.cfg保姆级教程 | - | 配置文件详解 |
| 保姆教程 klipper安装后调试 | - | 完整调试流程 |

---

## 十一、常用调平命令速查

```bash
# 归位
G28

# 测试温度
TEMPERATURE_WAIT HEATER=extruder TARGET=220

# PID校准
PID_CALIBRATE HEATER=extruder TARGET=220
PID_CALIBRATE HEATER=heater_bed TARGET=60

# 网床校准
BED_MESH_CALIBRATE

# 探针校准
PROBE_CALIBRATE

# 探针偏移校准
Z_ENDSTOP_CALIBRATE

# 保存配置
SAVE_CONFIG

# 步进电机测试
STEPPER_BUZZ STEPPER=stepper_x

# 查看加速度计数据（需ADXL345）
ACCELEROMETER_QUERY

# 共振测试
RESONANCES AXIS=X
RESONANCES AXIS=Y

# 压力提前测试
PRESSURE_ADVANCE_CALIBRATE
```

---

## 十二、大鱼TT 改装后配置变更清单

| 改装件 | 需要修改的配置 |
|--------|--------------|
| 42闭环电机 | `rotation_distance`，驱动电流 |
| Klicky探针 | `[probe]`、`[servo]`、`[homing_override]` |
| CAN总线SB2040 | 新增MCU配置，挤出机配置迁移 |
| 摄像头 | Crowsnest配置，`webcamd.conf` |
| 热床 | `heater_bed` 的 `pid_kp/ki/kd` 需重新校准 |
| 挤出机升级 | `rotation_distance`、`gear_ratio` 重新计算 |
