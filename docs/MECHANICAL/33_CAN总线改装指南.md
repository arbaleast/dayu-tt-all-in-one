# 大鱼TT CAN 总线改装指南

> 更新时间：2026-03-24
> 适用：大鱼TT / 大鱼CC

---

## 一、CAN 总线是什么？为什么要用？

**传统接线方式：** 每个设备（挤出机、热敏、风扇等）都需要单独接线到主板，又多又乱。

**CAN 总线方式：** 所有设备串联在一条总线上，只需要 4 根线（CAN_H、CAN_L、GND、24V），大大简化走线。

**优点：**
- 接线简洁，维护方便
- 抗干扰能力强，信号稳定
- 支持热插拔（部分板子）
- 适合有多个工具头或多色打印的机器

---

## 二、推荐方案

### 方案一：FLY SB2040（主流选择 ⭐⭐⭐⭐⭐）

| 项目 | 参数 |
|------|------|
| 主控 | RP2040 |
| 驱动 | TMC2209（集成）|
| 加速度计 | ADXL345（内置）|
| 接口 | CAN 总线 + USB |
| 适用固件 | Klipper |
| 版本 | V1 / V2 |

**V1 vs V2 区别：** V2 优化了部分电路，基本功能一致。

**购买参考：**
- Mellow 官方店铺：https://mellow.klipper.cn/#/board/fly_sb2040/
- Aliexpress Mellow 店

### 方案二：BIGTREETECH EBB SB2209 CAN

| 项目 | 参数 |
|------|------|
| 主控 | STM32 |
| 驱动 | TMC2209 |
| 特点 | 性价比高 |

---

## 三、硬件清单

| 配件 | 数量 | 说明 |
|------|------|------|
| FLY SB2040 V1/V2 | 1块 | 工具板，放在打印头端 |
| FLY Gemini V2 / 八爪鱼 | 1块 | 主板，作为 CAN 总线适配器 |
| CAN 总线线束 | 若干 | 4 芯线，建议AWG20 |
| 120Ω 终端电阻 | 1个 | 接在总线最末端 |
| 24V 电源 | 1个 | 给 SB2040 供电 |

---

## 四、接线方式

### 4.1 SB2040 端口定义

```
┌─────────────────────────┐
│  DC  │  GND │ CAN_H │ CAN_L │
└─────────────────────────┘
  24V    地     CAN高   CAN低
```

### 4.2 总线拓扑

```
┌──────────────┐    CAN总线(4芯)    ┌──────────────┐
│  主板        │ ════════════════▶ │  SB2040      │
│  (Gemini V2) │                   │  (工具板)     │
│              │ ◀── 120Ω 终端电阻 │              │
└──────────────┘                   └──────────────┘
```

**注意：** 120Ω 终端电阻只接在总线最末端（通常是 SB2040 端），主板那侧不接。

---

## 五、Klipper 固件编译与刷写

### 5.1 编译 Klipper（主机端 SSH）

```bash
cd ~/klipper
make clean KCONFIG_CONFIG=config.sb2040v2
make menuconfig KCONFIG_CONFIG=config.sb2040v2
```

**menuconfig 设置：**

```
[*] Enable extra low-level configuration options
    Micro-controller Architecture → Raspberry Pi RP2040
    Bootloader offset → 16KiB bootloader
    Communication interface → CAN bus
    CAN RX gpio number → (4)
    CAN TX gpio number → (5)
    CAN bus speed → (1000000)
    GPIO pins to set at micro-controller startup → (gpio24)
```

保存退出，然后：

```bash
make KCONFIG_CONFIG=config.sb2040v2 -j4
```

编译完成后固件在 `~/klipper/out/klipper.bin`

### 5.2 安装 Katapult（CanBoot）引导程序

SB2040 出厂可能没有引导程序，需要先刷 Katapult。

参考：https://github.com/Arksine/CanBoot

### 5.3 查询 CAN UUID

刷完 Katapult 后，在主机上查询设备 UUID：

```bash
~/katapult/scripts/flash_can.py -i can0 -q
```

返回示例：
```
Detected uuid: 8248a4b16ede, Application: Katapult
```

记录下这个 UUID。

### 5.4 通过 CAN 总线刷 Klipper 固件

```bash
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/klipper/out/klipper.bin -u 8248a4b16ede
```

刷写成功会显示进度条和 `File downloaded successfully`。

### 5.5 验证

再次查询确认应用已切换为 Klipper：

```bash
~/katapult/scripts/flash_can.py -i can0 -q
```

返回：
```
Detected uuid: 8248a4b16ede, Application: Klipper
```

---

## 六、printer.cfg 配置示例

### 6.1 主机 MCU（主板）

```ini
[mcu]
serial: /dev/serial/by-id/your-mainboard-serial
baud: 250000

[CAN bus]
can0_tx_pin: gpio4
can0_rx_pin: gpio5
can0_speed: 1000000
```

### 6.2 工具板 SB2040

```ini
[mcu SB2040]
canbus_uuid: 8248a4b16ede

[board_pins SB2040]
aliases:
  EXT_EN=gpio7
  EXT_STEP=gpio9
  EXT_DIR=gpio10
  EXT_UART=gpio8
  LIMIT_0=gpio25
  LIMIT_1=gpio28
  LIMIT_2=gpio29
  FAN0=gpio13
  FAN1=gpio14
  FAN2=gpio15
  TH0=gpio27
  TH1=gpio26
  HE0=gpio6
  RGBLED=gpio12
  ADXL=gpio1
  PT100=gpio22

[extruder]
step_pin: SB2040:EXT_STEP
dir_pin: !SB2040:EXT_DIR
rotation_distance: 22.67895
gear_ratio: 50:10
microsteps: 16
full_steps_per_rotation: 200
heater_pin: SB2040:HE0
sensor_pin: SB2040:TH0
sensor_type: ATC Semitec 104GT-2

[heater_fan hotend_fan]
pin: SB2040:FAN1
max_power: 1.0
kick_start_time: 0.5
heater: extruder
heater_temp: 50.0

[temperature_sensor SB2040_mcu]
sensor_type: temperature_mcu
mcu: SB2040

[temperature_fan]
sensor_type: temperature_mcu
control: watermark
pin: SB2040:FAN0
target_temp: 45
```
> ⚠️ rotation_distance 需要根据实际挤出机和减速比调整

---

## 七、常见问题

### Q1: flash_can.py 查询不到设备
- 检查 CAN 总线是否正确连接（CAN_H/CAN_L 不要接反）
- 确认 24V 电源已接通
- 检查终端电阻是否安装

### Q2: 刷写失败
- 确认使用的是正确版本的固件（V1 用 config.sb2040，V2 用 config.sb2040v2）
- 检查 UUID 是否正确

### Q3: Klipper 连接不上 SB2040
- 确认 printer.cfg 中的 `canbus_uuid` 与实际 UUID 一致
- 检查 `can0_speed` 设置为 1000000

### Q4: 主板端如何选型？
- **FLY Gemini V2** — FLY 自家主板，CAN 支持好
- **八爪鱼 Octopus Pro** — 社区常用，需要额外配置 CAN 适配

---

## 八、大鱼CC CAN 改装案例

**来源：** B站 `大鱼CC 四叉戟` 视频

- 使用 SB2040 + 碳纤维 X 轴改装
- 搭配 FLY MiniPad 上位机
- 三叉戟/四叉戟布局（多色打印）

---

## 九、参考资源

| 资源 | 链接 |
|------|------|
| Mellow 官方文档（SB2040 V2 CAN）| https://mellow-3d.github.io/fly_sb2040_v2_klipper_can.html |
| Mellow 官方文档（SB2040 V1 CAN）| https://mellow-3d.github.io/fly_sb2040_v1_klipper_can.html |
| Mellow 配置示例（V2）| https://mellow-3d.github.io/fly_sb2040_v2_klipper_config.html |
| CanBoot/Katapult 源码 | https://github.com/Arksine/CanBoot |
| Klipper 官方 | https://www.klipper3d.com/ |
| Klipper CAN 总线配置指南 | https://github.com/HRading/klipper_canbus_setup |
| B站 - 大鱼CC四叉戟 | https://www.bilibili.com/video/BV1x44y1T7Bq/ |
