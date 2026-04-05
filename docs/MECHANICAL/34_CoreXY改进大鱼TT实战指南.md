# CoreXY 改进大鱼 TT 实战指南

> 更新时间：2026-03-28  
> 参考来源：Voron Design 官方文档 + 社区改装经验  
> 定位：从 CoreXY 运动学原理到 Voron 改装方案的完整落地指南

---

## 一、大鱼 TT 当前状态

| 项目 | 现状 |
|------|------|
| 运动系统 | CoreXY（推测）|
| 框架 | TT150/TT235：2020 铝型材；TT310：2020/2040 |
| 固件 | Klipper ✅ |
| 皮带 | GT2 6mm（推测）|
| 线性导轨 | MGN12 或光轴（待确认）|
| Z 轴 | 单 Z 或 Trident 三 Z（改装中）|

---

## 二、Voron Design 核心技术参考

> 官方文档：https://docs.vorondesign.com/

### 2.1 Voron 运动系统设计原则

```
All Voron printers are built using CoreXY or CoreXZ configurations
to reduce the amount of moving mass, allowing increased
acceleration and speeds.
```

**关键要点：**
- **Genuine Gates Unitta 皮带** > 通用皮带（可靠性 + 性能）
- **F695 法兰轴承**作为惰轮（比 GT2 惰轮直径大，寿命更长）
- **MGN7/MGN9/MGN12** 线性导轨混用（按轴需求选择）
- 皮带宽度：6mm 或 **9mm**（大幅面用 9mm）

### 2.2 Voron 框架规格

| 型号 | 框架 | 皮带 |
|------|------|------|
| V0 | 1515 Makerbeam XL | GT2 6mm |
| V1/V2/Legacy | **2020 铝型材**（6mm槽宽）| GT2 6mm 或 9mm |
| Switchwire | 6030 + 3030 | — |
| **Trident** | **2020 铝型材** | **9mm 皮带** |

---

## 三、CoreXY 运动学核心改进

### 3.1 皮带系统（最关键）

#### 问题诊断
```
CoreXY 长距离传动的主要敌人：
1. 皮带弹性 → 反向间隙（backlash）
2. 皮筋效应 → 高速加速时的弹跳
3. 张紧力不均 → 两根皮带张力不同步
```

#### 改进方案

**方案 A：HTD 3M 皮带（推荐大幅面）**

| 参数 | GT2 | HTD 3M |
|------|-----|---------|
| 齿形 | 2mm 梯形 | 3mm 深弧形 |
| 适用行程 | ≤300mm | >300mm |
| 高速稳定性 | 一般 | **优秀** |
| 成本 | ¥40 | ¥80 |

**方案 B：Gates 9mm 皮带（Voron Trident 标准）**

- 皮带宽度提升 50%，刚性提升
- 适合 TT310（310mm 行程）
- 需配合对应规格皮带轮

**惰轮排列（关键设计）**

```
推荐：smooth → toothed → smooth
即：光轴惰轮 → 同步带轮 → 光轴惰轮

优势：
- 消除皮带振动节点
- 保持皮带与导轨平行
- 减少皮带与带轮啮合噪音
```

**弹簧自动张紧器**

- Nylock 螺母自锁结构
- 弹簧提供恒定张力，补偿皮带伸长
- 3D 打印设计参考：Voron 官方 AWD 套件

#### 皮带张力检测

```bash
# 音调频率法（Voron 标准）
# 皮带张力足 → 音调频率 > 100Hz
# 使用手机 APP 测量振动频率
```

---

### 3.2 框架刚性改进

#### 对角斜撑（Diagonal Bracing）

```
2020 铝型材框架在 XY 平面存在柔性
加对角撑杆可提升刚性 30-40%

安装方式：
- 框架四角对角线上
- 2020 撑杆 + 90度连接件
- 预算：¥100 + 半天
```

#### 2040 替换 X 梁

| 对比 | 2020 X梁 | 2040 X梁 |
|------|-----------|----------|
| 弯曲刚度 | 1× | **3.4×** |
| 成本增量 | — | ¥80 |
| 适用场景 | TT150/TT235 | **TT310** |

#### 顶板加固

- 铝型材 + **铝板或碳纤维板**（3-5mm）
- 减少框架"呼吸效应"
- TT310 打印时框架不晃动

---

### 3.3 线性导轨升级

**导轨选型参考（Voron）：**

| 导轨 | 特点 | 适用轴 |
|------|------|--------|
| MGN7 | 轻载紧凑 | Z 轴辅助 |
| MGN9C | 双轨防歪斜 | **X 轴（TT310）** |
| MGN12H | 高刚性重载 | Y 轴高速端 |

**大鱼 TT 升级建议：**
```
X 轴：MGN9C × 2（双轨，防歪斜）
Y 轴：MGN12H × 1
Z 轴：保持现有 或 Trident 三 Z 轴
```

> ⚠️ 导轨安装面必须精加工平面，导轨受弯会导致振动

---

### 3.4 Klipper 调校（不花钱的优化）

#### Input Shaper（核心）

```bash
# 在 Klipper 控制台执行
SHAPER_CALIBRATE

# 示例输出：
# X axis shaper: frequency 53.2 Hz
# Y axis shaper: frequency 38.4 Hz
# Recommended shaper_type: mzv
```

**调校后典型性能提升：**

| 参数 | 调校前 | Input Shaper 后 |
|------|--------|-----------------|
| 加速度 | 2000 mm/s² | **8000-15000 mm/s²** |
| 打印速度 | 50mm/s | **150-250mm/s** |
| 鬼影/振纹 | 明显 | 几乎消除 |

#### 其他 Klipper 优化参数

```yaml
# printer.cfg 参考
[printer]
max_velocity: 300
max_accel: 15000
max_accel_to_decel: 10000
square_corner_velocity: 5

[input_shaper]
shaper_freq_x: 53
shaper_freq_y: 38
shaper_type: mzv
```

---

## 四、Voron 改装方案落地

### 4.1 AWD 四驱改装（LDO CNC AWD Kit）

> 来源：Voron 社区 aTinyShellScript + MasturMynd 设计，LDO Motors 生产

**原理：** 将 CoreXY 的 X/Y 各 1 个电机 → 各 2 个电机（四电机同步）

**效果：**
- 消除皮带两侧张力不均
- 提升 X/Y 定位精度
- 减少高速打印时的皮带跳齿

**套件内容：**
- 2× 电机座（适配 LDO 电机）
- 2× 惰轮组件（法兰轴承）
- 皮带张紧机构
- 硬件螺丝

**适配性分析：**

| 条件 | 适合改装 AWD |
|------|-------------|
| 电机型号 | LDO-xxxx（需确认孔距）|
| 框架 | 2020 型材 |
| 改装目标 | 高速打印（>200mm/s）|

**大鱼 TT 改装评估：**
- 套件专为 Voron 2020 框架设计
- 理论上可移植，需核实孔位规格
- 优先级：🟡 P1（效果好但需适配）

---

### 4.2 Trident 三 Z 轴改装（已在项目中）

> 参考：`三叉戟Trident改装指南.md`

**核心收益：**
- 三 Z 轴同步，平台更水平
- 减少 Z 向抖动
- 支持多色 AMS/eratank 升级

---

### 4.3 闭环步进电机

> 参考：`42闭环电机改装实战采购指南.md`

**结论（Voron 社区共识）：**

| 场景 | 评价 |
|------|------|
| X/Y 轴 | ❌ 不推荐（皮带弹性是机械问题，闭环解决不了）|
| Z 轴 | ✅ 推荐（三 Z 同步，保证平台水平）|
| 挤出机 | ✅ 推荐（堵料检测）|

---

## 五、改装 BOM 清单

### P0 优先级（立即可做）

| 配件 | 规格 | 数量 | 预估成本 |
|------|------|------|----------|
| Gates 皮带 | GT2 6mm 或 9mm | 2条 | ¥60-120 |
| HTD 3M 皮带轮 | 20T GT2 | 4个 | ¥40 |
| F695 轴承 | 内径 6mm | 8个 | ¥30 |
| 弹簧张紧器 | 3D 打印 | 2套 | ¥0 |

### P1 优先级（高收益）

| 配件 | 规格 | 数量 | 预估成本 |
|------|------|------|----------|
| 2040 X 梁 | 310mm 长 | 1根 | ¥80 |
| 对角斜撑 | 2020 撑杆 | 2根 | ¥50 |
| MGN9C 导轨 | 350mm | 2根 | ¥120 |
| MGN12H 导轨 | 350mm | 1根 | ¥80 |
| LDO AWD 套件 | Trident/V2.4 | 1套 | ¥350 |

### P2 优先级（可选）

| 配件 | 规格 | 数量 | 预估成本 |
|------|------|------|----------|
| 0.6mm 喷嘴 | 全金属 | 3个 | ¥30 |
| 0.8mm 喷嘴 | 全金属 | 2个 | ¥30 |
| 40W 热端 | 全金属 | 1套 | ¥120 |
| Trident Z 轴套件 | 3Z 轴 | 1套 | ¥400 |

---

## 六、实施路线图

```
Phase 0: 皮带系统升级
  → HTD 3M 或 Gates 9mm 皮带
  → 弹簧自动张紧器
  → F695 轴承惰轮
  预计效果：速度 +50%，精度提升

Phase 1: Klipper Input Shaper 精调
  → SHAPER_CALIBRATE 全流程
  → 加速度从 2000 → 10000+ mm/s²
  预计效果：速度 ×3-5

Phase 2: 框架刚性加固
  → 2040 X 梁替换
  → 对角斜撑
  → 顶板加固
  预计效果：框架振动减少 40%

Phase 3: Trident 三 Z 轴
  → 移植 Voron Trident 方案
  → 三 Z 同步控制
  预计效果：Z 轴稳定性大幅提升

Phase 4: AWD 四驱（可选）
  → LDO CNC AWD 套件
  → 四电机同步调校
  预计效果：消除皮带侧向跳动
```

---

## 七、参考资料

| 来源 | 链接 | 用途 |
|------|------|------|
| Voron 官方文档 | docs.vorondesign.com | 核心技术规范 |
| Voron 社区论坛 | forum.vorondesign.com | 改装经验 |
| LDO AWD 套件 | ldomotion.com/products/ldocncawdkit | 四驱改装 |
| CoreXY 运动学 | 3ddistributed.com/corexy-3d-printer | 皮带路径设计 |
| Voron Reddit | reddit.com/r/voroncorexy | 社区改装案例 |

---

*文档基于 Voron Design 官方开源资料 + 社区改装经验整理，供大鱼 TT 改装参考。*
