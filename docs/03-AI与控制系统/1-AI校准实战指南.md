# AI 校准实战指南

> 本指南基于 2026-03-29 AI 技术调研成果，面向大鱼 TT 用户的实用操作手册。

---

## 1. ADXL345 + Klippain Shaketune 输入整形校准

### 硬件准备

| 项目 | 规格/型号 | 参考成本 |
|------|----------|---------|
| 加速度计 | ADXL345 | ¥15 |
| 连接线 | 4Pin Dupont 线 | 随机附送 |
| 安装座 | 3D 打印磁吸座（可选）| 约 ¥5 |

ADXL345 是一款三轴加速度计，能够精确测量打印机在打印过程中的振动频率。通过分析这些频率数据，Klipper 可以计算出最优的输入整形（Input Shaping）参数，显著减少打印过程中的 **ringing**（回响/振纹）缺陷。

### 连接方式

ADXL345 通过 SPI 接口连接至树莓派（或运行 Klipper 的 SBC）：

```
ADXL345 VCC  → 3.3V（注意不是 5V，避免损坏）
ADXL345 GND  → GND
ADXL345 SDA  → SPI MOSI（如 GPIO 10）
ADXL345 SCL  → SPI SCLK（如 GPIO 11）
ADXL345 CS   → 任意 GPIO（如 GPIO 8）
ADXLXY SDO  → GND（地址拉低，地址 0x53）
```

> ⚠️ **警告**：ADXL345 只能使用 3.3V 供电，接到 5V 会立即烧毁传感器。

### 校准流程

**Step 1：在 Klipper 配置文件中添加 ADXL345 传感器定义**

```ini
[resonance_tester]
accel_chip: adxl345
# 或通过树莓派 SPI 直接连接
adxl345:
```

**Step 2：执行共振测试**

```bash
# 确认 ADXL345 正常通信
ADXL_QUERY

# 执行 X 轴共振测试（打印头在 X 方向往复运动）
TEST_RESONANCES AXIS=X

# 执行 Y 轴共振测试
TEST_RESONANCES AXIS=Y
```

测试过程中，打印机各轴会进行一系列往复运动。ADXL345 会记录振动数据。**建议在打印平台空载状态下进行此测试。**

**Step 3：运行输入整形校准**

```bash
# 基于测试数据，自动计算最优 Input Shaping 参数
SHAPER_CALIBRATE
```

校准完成后，Klipper 会输出推荐的 Input Shaping 频率和类型（如 `zv`、`mzv`、`ei`、`什么都没` 等），并自动写入配置文件。

**Step 4：使用 Klippain Shaketune 可视化分析（推荐）**

Klippain Shaketune 是 Klippain 发行版内置的可视化工具，提供比原生 Klipper `SHAPER_CALIBRATE` 更详细的分析图表：

- **功率谱密度（PSD）图**：显示各频率下的振动强度
- **输入整形效果对比图**：直观展示整形前后 ringing 抑制效果
- **推荐轴参数卡片**：清晰显示最优频率和整形器类型

在 Mainsail 或 Fluidd WebUI 中，找到 **Machine → Shaper Calibration** 即可进入可视化界面，一键完成校准。

### 校准后预期性能

| 指标 | 校准前（默认）| 校准后（参考值）|
|------|-------------|--------------|
| 最大安全加速度 | 1,000–2,000 mm/s² | **6,000–13,000 mm/s²** |
| Ringing 消除率 | — | **80–95%** |
| 打印速度提升 | — | 同比可提升 2–3× |
| 适用机型 | — | Voron 2.4 / Trident / 大鱼 TT |

> 💡 **经验值**：在 Voron 2.4 300mm 机型上，使用 Klippain Shaketune 校准后，加速度从 ~2,000mm/s² 提升至 ~10,000mm/s²，200mm/s 打印下视觉几乎无 ringing 痕迹。

### 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| `ADXL345 not found` | SPI 未启用 / 接线错误 | 检查 `/boot/config.txt` 中 `dtparam=spi=on` 是否开启；确认接线牢固 |
| 校准后 ringing 反而更明显 | 测试时平台上有残留打印件 | 移除平台上的所有物体后重新测试 |
| 加速度上限报错 | 加速度计未正确固定 | 使用磁吸座或扎带固定 ADXL345，避免测量噪声 |

---

## 2. PressureAdvanceCamera 自动化 PA 校准（USB 内窥镜方案）

### 什么是 Pressure Advance？

Pressure Advance（压力提前，简称 PA）是 Klipper 中用于补偿耗材流速与喷嘴压力之间物理延迟的参数。PA 值设置不当会导致：

- **出丝过粗/过细**：拐角处出丝量跟不上运动变化
- **过冲/欠冲**：直线末端出现堆叠或缺口
- **表面波纹**：特别是小角度拐角处

### 传统 PA 校准的痛点

传统方法需要打印一个 PA 测试塔，耗费 10–30 分钟，且依赖人工观察来判断最优值。这对新手不友好，且结果主观性较强。

### PressureAdvanceCamera 方案

**所需硬件：低价 USB 内窥镜（¥30 左右）**

这种方案使用计算机视觉（CV）自动分析打印线条的过冲/欠冲程度，无需人工判断，实现**分钟级自动化校准**。

### 工作原理

1. 内窥镜固定于喷嘴附近，俯视拍摄打印线条
2. 软件实时识别线条边缘，计算过冲量（overshoot）和欠冲量（undershoot）
3. 自动搜索最优 PA 值，使过冲/欠冲最小化

### 实施步骤

**Step 1：安装 USB 内窥镜并调整角度**

将 USB 内窥镜安装在喷嘴侧面或前方支架上，确保能清晰俯视正在打印的直线（建议使用专用的 [Klipper PA 校准宏](https://github.com/kyleseeley/PressureAdvanceCamera)）。

**Step 2：运行 PA 校准宏**

```bash
# 启动 PA 自动校准流程
PA_CALIBRATE
```

宏会自动打印一段包含多个 PA 值段的测试图案，同时内窥镜持续拍摄，软件实时分析。

**Step 3：获取最优 PA 值**

校准完成后，软件会输出最优 PA 值：

```
Recommended Pressure Advance: 0.045
```

**Step 4：将结果写入配置**

```ini
# 在 printer.cfg 中添加或更新
[extruder]
pressure_advance: 0.045
pressure_advance_lookahead_time: 0.040
```

### 与 Klippain 集成

Klippain 发行版已集成 PressureAdvanceCamera 校准流程，可在 WebUI 中一键启动，自动完成 PA 校准，无需手动敲命令。

---

## 3. Klippain 配置栈（IS + 床网 + PA + Flow 一键校准）

### Klippain 是什么？

[Klippain](https://github.com/Frix-x/klippain) 是一个 Klipper 发行版（Distribution），集成了 Klipper 周边最实用的校准工具链，通过精心设计的配置模板和自动化宏，将原本需要数小时的手动校准工作压缩到 **15 分钟左右**。

### 核心功能模块

| 模块 | 功能 | 节省时间 |
|------|------|---------|
| **Input Shaper** | 共振测试 + IS 参数自动计算 | ~30min |
| **自适应床网** | 智能探测热床不平整，自动生成补偿网格 | ~20min |
| **PA 标定** | PressureAdvance 自动化校准 | ~15min |
| **Flow 标定** | 耗材流量系数校准 | ~10min |
| **振动分析** | 使用 ADXL345 分析各轴谐振 | ~10min |

### 一键校准流程

Klippain 提供高度自动化的校准宏，只需按顺序执行几个宏即可完成全部校准：

```bash
# 1. 初始化 Klippain 配置栈
KLIPPAIN_INIT

# 2. 运行完整校准序列（包含 IS + 床网 + PA + Flow）
KLIPPAIN_CALIBRATE_ALL
```

`KLIPPAIN_CALIBRATE_ALL` 宏会自动：
1. 运行共振测试（X/Y 轴）
2. 计算最优 Input Shaping 参数
3. 执行床网探测（默认 7×7 网格）
4. 运行 PA 校准（如果配置了内窥镜）
5. 执行 Flow 校准
6. 生成综合校准报告

### 配置模板

Klippain 提供开箱即用的配置模板，适配 Voron 系列、Prusa、LDO 机型等。配置文件结构清晰，注释详细，新手也能理解每项参数的含义。

```ini
# Klippain 配置模板片段
[input_shaper]
# 建议在运行 SHAPER_CALIBRATE 后自动生成
shaper_freq_x: 39.2
shaper_type_x: ei
shaper_freq_y: 40.4
shaper_type_y: ei

[bed_mesh]
# 7×7 网格，采样点 49 个
mesh_min: 20, 20
mesh_max: 280, 280
probe_count: 7,7
```

### 为大鱼 TT 适配 Klippain

大鱼 TT 基于 Voron TT 改型，电机配置和床尺寸与 Voron 2.4 接近，可直接使用 Klippain 的 Voron 2.4 配置模板，然后根据实际硬件参数调整以下内容：

- 电机步数（step_per_mm）
- 皮带轮齿数（gear_ratio）
- 热床尺寸和加热功率
- 热端型号（V6 / Dragon / Clockwork 等）

---

## 4. 校准后预期性能总览

| 性能指标 | 原始状态 | AI 校准后 | 提升幅度 |
|---------|---------|----------|---------|
| 最大加速度 | 1,000–2,000 mm/s² | 6,000–13,000 mm/s² | **5–10×** |
| Ringing 消除率 | — | 80–95% | 显著视觉改善 |
| 拐角过冲/欠冲 | 明显 | 基本消除 | 质量↑ |
| PA 校准时间 | 10–30 min（手动）| **1–3 min（自动）**| 10× 效率提升 |
| 床网精度 | 手动垫片 | 49 点自动探测 | 一致性↑ |
| 综合校准时间 | ~2 小时（分散）| **~15 分钟（一键）**| 8× 效率提升 |

---

## 5. 硬件推荐清单

| 设备 | 型号/规格 | 参考链接 |
|------|---------|---------|
| 加速度计 | ADXL345（3.3V SPI）| 淘宝/拼多多 ¥10–20 |
| USB 内窥镜 | USB 微型摄像头（≥30 万像素）| ¥30–50 |
| 安装座 | 3D 打印磁吸 ADXL345 座 | 社区开源文件 |
| 内窥镜支架 | 3D 打印可调节支架 | 社区开源文件 |

---

## 6. 参考资源

- [Klippain GitHub](https://github.com/Frix-x/klippain)
- [Klipper Input Shaping 官方文档](https://www.klipper.info/)
- [PressureAdvanceCamera GitHub](https://github.com/kyleseeley/PressureAdvanceCamera)
- [Klipper Shaper Calibration 文档](https://www.klipper.org.cn/)

---

> **下一步**：[故障检测系统](./2-故障检测系统.md) — 了解如何通过 Obico AI、OctoEverywhere 和 3DPrintSentinel 实现打印过程的实时故障监控。
