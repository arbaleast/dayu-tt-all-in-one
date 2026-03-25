# Cartographer 3D 传感器改装指南

> 更新时间：2026-03-25
> 适用：大鱼TT及同类 CoreXY 结构打印机
> 来源：Voron Design + Cartographer 官方文档

---

## 一、Cartographer 3D 是什么？

Cartographer 3D 是 Voron 社区开源的高精度主动隔振探针系统，替代传统的 TAP（Touch Away Probe）或 Klicky 探针。

**核心功能：**
1. 🔍 床面扫描（Bed Mesh）— 高精度网格校准
2. 🛡️ 主动隔振（Input Shaping）— 消除共振提升打印质量
3. 🔲 Z 轴限位 — 精确 Z=0 定位

---

## 二、与 TAP / Klicky 对比

| 特性 | Cartographer 3D | TAP | Klicky |
|------|----------------|-----|--------|
| 精度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 隔振功能 | ✅ 内置 | ❌ 无 | ❌ 无 |
| 安装复杂度 | 中等 | 简单 | 简单 |
| 成本 | ~¥150 | ~¥80 | ~¥50 |
| 热端兼容性 | 专用支架 | 专用支架 | 通用夹具 |
| 社区支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 为什么选 Cartographer？
- **打印质量提升明显**：主动隔振减少振纹，对高速打印尤其有效
- **一机多用**：探针+隔振二合一，减少硬件
- **适合封闭机箱**：非接触式，不受腔温影响

---

## 三、所需配件

| 配件 | 数量 | 备注 |
|------|------|------|
| Cartographer 传感器 | 1 | ADXL345 或专用模块 |
| 安装支架 | 1 | 3D 打印（Voron 开源文件） |
| M3 螺丝 | 若干 | 固定支架 |
| 杜邦线 | 若干 | 连接 MCU |
| （可选）ADXL345 模块 | 1 | 如果买的是散件 |

### ADXL345 vs 专用模块
- **ADXL345 散件**：便宜（¥20-30），需要自己接线
- **专用 Cartographer 模块**：自带 PCB，即插即用（¥80-150）

---

## 四、安装步骤

### 硬件安装

1. **打印安装支架**
   ```
   下载：Voron GitHub → Cartographer mount
   材料：PETG 或 ABS（封闭机箱内建议 ABS）
   层高：0.2mm
   填充：50%+
   ```

2. **固定传感器**
   ```
   1. 将 ADXL345 模块固定在支架上（注意方向标记）
   2. 支架安装到热端（冷却风扇旁边）
   3. 确保传感器 XY 方向与机架对齐
   ```

3. **接线（ADXL345 示例）**
   ```
   ADXL345    →    MCU
   ─────────────────────
   VCC        →    3.3V（或5V）
   GND        →    GND
   SDA        →    I2C SDA（如 PB7 on STM32）
   SCL        →    I2C SCL（如 PB6 on STM32）
   INT        →    任意 GPIO（用于触发）
   ```

### 固件配置（Klipper）

```ini
# adxl345 传感器配置
[adxl345]
cs_pin: PB6  # 根据实际调整

# 隔振输入整形
[input_shaper]
shaper_type: ei
shaper_freq_x: 40
shaper_freq_y: 40

# 床面扫描（使用 Cartographer）
[bed_mesh]
speed: 200
horizontal_move_z: 5
mesh_radius: 40
mesh_origin: 0, 0
billinear:
  resolution: 5
```

### 校准步骤

1. **测试传感器连接**
   ```bash
   # Klipper 控制台
   ACCELEROMETER_QUERY
   # 应返回 XYZ 加速度数据
   ```

2. **运行输入整形校准**
   ```bash
   # Klipper 控制台
   INPUT_SHAPER_CALIBRATION
   # 自动测试并给出推荐参数
   ```

3. **生成床面网格**
   ```bash
   # Klipper 控制台
   BED_MESH_CALIBRATE
   ```

---

## 五、Cartographer 在大鱼TT上的优势

| 问题 | TAP/Klicky 方案 | Cartographer 方案 |
|------|----------------|-----------------|
| 高速打印振纹 | 需手动调输入整形 | 自动隔振 |
| 封闭腔室探针可靠性 | 受热影响小 | 完全非接触 |
| 床面精度 | 一般 | 更高（多次采样平均） |
| 安装空间 | 需考虑碰撞 | 体积小，布局灵活 |

---

## 六、常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 无加速度数据输出 | I2C 地址或接线错误 | 检查 SDA/SCL 接的是否是同一组 I2C |
| 数值漂移 | 固定不稳 | 检查支架螺丝是否松动 |
| 隔振效果不明显 | 参数未优化 | 重新运行 `INPUT_SHAPER_CALIBRATION` |
| 床面扫描误差大 | 探针偏移 | 检查喷嘴与传感器相对位置 |

---

## 七、参考资料

- **Voron Cartographer 文档**：https://docs.vorondesign.com/
- **Cartographer GitHub**：https://github.com/Cartographer3D/
- **Voron 论坛讨论**：forum.vorondesign.com
- **中文教程**：B站搜索 "Cartographer 3D 探针"

---

## 八、升级建议

### 值得升级的情况 ✅
- 经常高速打印（>100mm/s）
- 打印件层纹明显
- 已经安装了封闭机箱
- 希望减少调试时间

### 不值得升级的情况 ❌
- 主要是低速打印（<60mm/s）
- 还没装 Klipper（Cartographer 需要 Klipper）
- 预算有限，Klicky 已够用
