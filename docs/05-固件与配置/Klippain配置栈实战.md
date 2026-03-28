# Klippain 配置栈实战

> 更新时间：2026-03-29
> 适用：大鱼TT / CoreXY / Klipper 用户
> 难度：中级（需要 Klipper 基础）

---

## 一、Klippain 简介

### 1.1 什么是 Klippain？

**Klippain** 是一个由社区维护的 Klipper 配置栈（Config Stack），由 B站 UP 主「工程师小林」等社区玩家推广。它提供了一套**开箱即用的 Klipper 配置模板**，包含了大量预优化的宏、脚本和校准流程。

**官方网站：**
- GitHub：https://github.com/Frix-7/klippain
- 社区讨论：B站搜索「Klippain 大鱼TT」

### 1.2 Klippain 解决了什么问题？

普通 Klipper 用户面临的痛点：
- 手动配置 `printer.cfg` 繁琐，容易出错
- 输入整形、PA、Flow 需要分别查找教程、分步调试
- 校准参数散布在不同文档中，缺乏系统性
- 新机器迁移配置麻烦

Klippain 把这些整合成**一键校准流程**，用户只需要执行几个宏，就能完成原本需要数小时的手动调试。

### 1.3 主要优势

| 特性 | 普通 Klipper | Klippain |
|------|------------|---------|
| 配置复杂度 | 高（需要手写大量参数）| 低（模块化，模板化）|
| 输入整形 | 手动运行加速度测试 | 一键自动分析 |
| 床网调平 | 手动运行 BED_MESH | 一键自动网格 |
| PA 校准 | 手动打印测试塔 | 一键自动化测试 |
| 多色/多挤出机 | 手动配置 | 模板支持 |
| 固件更新 | 手动同步配置 | 提供更新脚本 |

---

## 二、Klippain 安装

### 2.1 前置条件

- Klipper 已正常运行
- Moonraker / Mainsail 或 Fluidd 已配置
- SSH 访问权限
- ADXL345 加速度计（用于输入整形校准）

### 2.2 安装步骤

**方法一：SSH 一键安装**

```bash
# 克隆 Klippain 仓库
cd ~ && git clone https://github.com/Frix-7/klippain.git

# 运行安装脚本
cd klippain
chmod +x install.sh
./install.sh
```

**方法二：手动安装**

```bash
# 下载主配置文件
cp klippain/config/printer.example.cfg ~/printer_data/config/printer-klippain.cfg

# 下载 Klippain 宏
cp -r klippain/config/*.macros.cfg ~/printer_data/config/

# 重命名为 printer.cfg 并引用
# 在 printer.cfg 末尾添加：
[include printer-klippain.cfg]
```

### 2.3 首次配置

编辑 `printer-klippain.cfg`，填写机器特定参数：

```ini
# ====== 机器基本参数（必填）======
[printer]
kinematics: corexy
max_velocity: 500
max_z_velocity: 20

# 打印尺寸（根据大鱼TT版本选择）
# 235mm 版本：
bed_size: 235
max_z: 250
# 310mm 版本：
# bed_size: 310
# max_z: 310

# 喷嘴信息
nozzle_diameter: 0.4
filament_diameter: 1.75

# ADXL345 加速度计
[adxl345]
cs_pin: rpi:None

[resonance_tester]
accel_chip: adxl345
probe_points:
    117.5, 117.5, 20   # 235版中心坐标
```

---

## 三、一键校准流程

### 3.1 校准前准备

1. 确认热床已调平（手动或粗调）
2. 确认 Z offset 已设置
3. 预热热床和喷嘴至常用温度
4. 准备 SD 卡或确认 Moonraker 上传功能正常

### 3.2 输入整形（Input Shaper）一键校准

**执行宏：**

```
CALIBRATE_SHAPER
```

Klippain 会自动：
1. 在 X/Y 方向各运行 4-8 次加速度测试
2. 分析不同频率下的振动幅值
3. 生成共振图表（可在 Mainsail 查看）
4. 输出推荐的 shaper_type 和 shaper_freq

**示例输出：**

```
Input shaper calibration:
  X: shaper_freq=57.6 Hz, shaper_type=ei
  Y: shaper_freq=58.2 Hz, shaper_type=2hump_ei
```

将建议值填入配置，Klipper 会自动保存。

### 3.3 床网（Bed Mesh）一键校准

**执行宏：**

```
CALIBRATE_MESH
```

Klippain 会：
1. 自动探测定高（Z endstop 偏移）
2. 运行 5x5 或 7x7 网格探测
3. 生成等高线图，显示热床平整度
4. 将结果保存到 `[bed_mesh]` 配置

**可选高级网格：**

```
CALIBRATE_MESH VERBOSE=1 POINTS=7x7
```

### 3.4 Pressure Advance 一键校准

**执行宏：**

```
CALIBRATE_PA
```

Klippain 会打印一个 PA 测试塔，每层自动递增 PA 值：

```
Layer 1: PA=0.02
Layer 2: PA=0.03
Layer 3: PA=0.04
...
Layer 10: PA=0.11
```

打印完成后，根据塔壁的平整度和拐角质量，人工判断最佳 PA 值。Klippain 提供了**拐角测量工具**（Corner measuring）在 WebUI 中直接输入测量结果，自动计算最优值。

### 3.5 Flow 校准

**执行宏：**

```
CALIBRATE_FLOW
```

打印一个 20mm 校准方块，测量实际壁厚，与理论值对比后自动计算 Flow 补偿：

```ini
# Klippain 会自动填写
[extruder]
# flow_ratio: 0.975  # 自动计算的结果
```

---

## 四、从 Klippain 获取最佳参数

### 4.1 解读校准报告

Klippain 在 Mainsail 的**配置顾问（Config Advisor）**面板中，会显示所有关键参数的建议值：

| 参数 | 含义 | 正常范围 |
|------|------|---------|
| `shaper_freq_x/y` | 输入整形频率 | 40-80 Hz（CoreXY）|
| `shaper_type` | 整形器类型 | ei / 2hump_ei |
| `pressure_advance` | 压力提前值 | 0.04-0.08（近程）|
| `flow_ratio` | 流量比例 | 0.95-1.05 |
| `mesh_interpolation` | 网格插值方式 | lagrange / bicubic |

### 4.2 精细微调建议

一键校准完成后，建议进行以下微调：

1. **过冲/欠冲检查**：打印一个小齿轮，观察齿形是否清晰
2. **拐角过凸检查**：打印十字结构，观察拐角是否内缩或外凸
3. **表面波纹检查**：打印高速测试块，检查 Ringing 是否在可接受范围

---

## 五、与 Klipper 原生配置对比

### 5.1 配置结构对比

| 方面 | Klipper 原生 | Klippain |
|------|------------|---------|
| 配置文件 | 单一 printer.cfg | 模块化（多个 .cfg）|
| 校准方式 | 手动执行各项测试 | 宏一键驱动 |
| 参数查找 | 需要阅读官方文档 | 注释详尽，一目了然 |
| 更新维护 | 手动同步 | 提供 update.sh 一键更新 |
| 社区支持 | 官方论坛 | B站 + GitHub Issues |
| 学习曲线 | 陡峭 | 较平缓 |

### 5.2 性能对比

理论上 Klippain 和原生 Klipper 性能完全一致，因为 Klippain 本质上是**配置模板而非修改版固件**。实际测试中两者打印质量无显著差异。

但 Klippain 的优化参数（特别是输入整形和 PA）经过社区大量机器验证，减少了新手踩坑的概率。

### 5.3 何时选择 Klippain？

**推荐使用 Klippain：**
- 刚入手 Klipper，想快速上手
- 希望系统性完成全套校准
- 不喜欢折腾配置，想开箱即用

**建议继续用原生 Klipper：**
- 机器有特殊定制需求（如多色、CAN 总线复杂拓扑）
- 已经是 Klipper 老用户，已有的配置运行良好
- 需要深度定制宏逻辑

---

## 六、Klippain 进阶用法

### 6.1 自定义校准参数

在 `printer-klippain.cfg` 中可以覆盖默认值：

```ini
# 强制使用更高精度的床网
[bed_mesh]
horizontal_move_z: 5          # 降低抬升高度（加快速度）
mesh_radius: 80               # 扩大网格范围
probe_count: 9,9              # 9x9 网格

# 使用 lagrange 插值（更适合非线性床面）
mesh_interpolation: lagrange
```

### 6.2 多色打印支持

Klippain 提供多挤出机模板：

```ini
# 使用 Klippain 的 multi_extruder 模板
[include klippain/config/multiextruder/*.cfg]
```

### 6.3 自动化维护脚本

Klippain 提供定期校准提醒：
- 每次换耗材后建议重新校准 PA
- 每 500 小时建议重新校准输入整形
- 热床更换后必须重新校准床网

---

## 七、常见问题

### Q1: Klippain 和 Klipper 版本兼容性？
确保 Klippain 与当前 Klipper 主版本兼容，GitHub 页面有版本对应说明。

### Q2: 安装后 Klipper 无法启动？
检查是否有重复配置——确保 `[include]` 路径正确，且没有同时加载旧配置文件。

### Q3: 校准结果不理想？
- 检查机械状态（皮带张力、电机固定、热床平整）
- 确认 ADXL345 传感器固定牢固（使用尼龙扎带，避免晃动）
- 床网探测前确保热床已预热至工作温度

---

## 相关文档

- [Klipper 深度优化指南](./Klipper深度优化指南.md)
- [Klipper 固件配置完全指南](../02-硬件改进/Klipper固件配置完全指南.md)
- [CAN 总线改装指南](../02-硬件改进/CAN总线改装指南.md)
