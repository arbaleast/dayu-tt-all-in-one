# 大鱼 TT 自我进化系统 — 完整设计

> 日期：2026-03-27
> 版本：v1.1（混合方案）
> 目标：实现 A（全自动故障恢复）+ B（参数自优化）+ C（远程监控+进化）+ D（AI 助手）

---

## 一、系统架构（混合方案）

```
用户
 └── 🧠 AI 助手层（自然语言控制 + 对话式交互）
        └── 📊 进化引擎（参数学习 + 经验积累）
              ├── 👁️ 视觉层（摄像头 + AI 缺陷检测）    ← Obico 提供
              ├── 📡 控制层（Klipper Moonraker API）
              ├── 🔧 执行层（自适应切片 + 参数引擎）
              └── 📈 数据层（SQLite 打印记录库）
```

**混合架构说明：**
- **Phase 0（即刻）：** Obico 直接接管视觉层，1-2 小时上线 AI 检测
- **Phase 1+：** 在 Obico 之上叠加自建进化引擎，Obico 管感知，NAS 管思考
- **数据流向：** Obico 检测 → SQLite 记录 → 进化模型学习 → 智能参数库

**三层分离设计：**
- **树莓派**（边缘计算）：摄像头采集 + Obico AI 推理 + 振动传感器 + Klipper 通信
- **本地 NAS**（大脑）：进化模型训练 + 长期数据存储 + AI 助手
- **用户设备**（入口）：Telegram / Web UI / 语音

**双传感器方案（Phase 3 增强）：**
- 视觉（Obico）：检测可见缺陷（错位/塌陷/拉丝/spaghetti）
- 振动（MPU6050）：检测不可见缺陷（层间分离/内部裂纹/挤出异常）

---

## 二、功能模块设计

### 模块 A：全自动故障恢复

**目标：** 打印失败时无需人工介入，系统自动分析原因、调整参数、重试

**数据流（混合方案）：**
```
摄像头逐层扫描 → Obico AI 缺陷检测（15+ 失败类型）
 → 失败类型判定（粘连/错位/拉丝/塌陷/分层）
 → 根因分析（参数溯源：温度/速度/层高/支撑）
 → 参数调整策略库（自建规则 + ML 混合）
 → Klipper API 下发新参数 → 重新打印该层或新任务
 → 记录本次修复经验到 SQLite（进化学习闭环）
```

**AI 缺陷检测模型：**
- **Obico 预训练模型（Phase 0 即上线）：** 支持 15+ 种失败类型，开箱即用
- **自建进化层（Phase 2）：** 用自己的失败照片微调 LoRA 模型，越用越准

**故障恢复策略示例：**
| 失败现象 | 根因 | 调整动作 |
|---------|------|---------|
| 底层粘连 | 热床温度过低 | +5°C 重新调平 |
| 顶层塌陷 | 模型悬空角度大 | 自动加支撑 + 降低速度 |
| 拉丝严重 | 回抽不足 + 温度高 | 回抽 +10mm，温度 -10°C |
| 错位层移 | 共振/丢步 | 触发 Input Shaping 重校准 |

---

### 模块 B：参数自优化

**目标：** 系统自动学习最优打印参数，无需手动调参

**输入数据：**
- 打印任务（元数据：模型文件、材料、尺寸）
- 打印结果（成功/失败、缺陷类型、质量评分）
- 传感器数据（温度曲线、电流曲线、振动频谱）

**进化算法：**
```
历史数据 → 特征提取（材料+几何+环境+机器状态）
 → 在线学习模型（轻量：scikit-learn / PyTorch Mobile）
 → 预测最优参数（层高、温度、速度、PA、冷却）
 → 输出 Klipper 配置片段 + OrcaSlicer 配置
 → 下次同类任务自动应用
```

**自优化范围：**
- [ ] 温度 PID 自动整定
- [ ] 压力提前（PA）自动校准
- [ ] 输入整形（Input Shaping）频率检测
- [ ] 散热策略（不同材料的冷却曲线）
- [ ] 首层调平网格优化

**材料知识库：**
预置 PLA / PETG / ABS / TPU 的基础参数矩阵，AI 在此基础上针对大鱼 TT 的具体机型微调

---

### 模块 C：远程监控 + 进化

**目标：** 在任何地方监控打印状态，系统自动决定是否需要通知

**监控指标：**
- 实时视频流（低帧率省带宽）+ 时间轴缩略图
- 打印进度（Layer % / ETA）
- 温湿度曲线（热端、床温、腔温）
- 电机电流波形（挤出是否顺畅）
- AI 质量评分（实时 + 完成后）

**进化数据面板：**
```
/evolution
 ├── 🐟 机器健康分：92/100（上周 87）
 ├── 📈 成功率趋势：92% → 95% → 97%（近30天）
 ├── 🔥 Top 失败原因：TOP1 底层粘连(43%) TOP2 拉丝(28%)
 ├── ⚙️ 参数漂移检测：热端温度偏差 +3°C（需校准）
 └── 💡 进化建议：加装腔体温控后成功率+12%
```

**推送策略：**
- 真正失败时推送（AI 确认，非误报）
- 长期进化里程碑（成功率突破 95%、学会新材料）
- 异常根因发现（机器状态漂移）

---

### 模块 D：AI 助手（对话式控制）

**目标：** 自然语言控制打印机，"对话即操作"

**能力矩阵：**
| 功能 | 示例 | 实现方式 |
|------|------|---------|
| 查询状态 | "现在打印到哪了？" | Moonraker API → 语音回答 |
| 修改参数 | "把这个模型的速度降低 20%" | 参数解析 → Klipper 热更新 |
| 分析失败 | "上次打印为什么失败了？" | 查数据库 + AI 分析 |
| 建议优化 | "这个模型用什么参数最好？" | 进化模型推理 |
| 控制执行 | "暂停打印，调平后继续" | Klipper G-code 命令 |
| 生成报告 | "给我这个月的打印总结" | 数据统计 + LLM 总结 |

**实现方案：**
- 本地 LLM（如 Ollama Qwen/DeepSeek）保证隐私
- 语音输入输出（TTS）支持手机场景
- Telegram 作为主控入口（自然语言对话）

---

## 三、硬件配置清单

**基础改造预算（约 500 元）：**

| 组件 | 推荐型号 | 用途 | 价格 |
|------|---------|------|------|
| 摄像头 | 1080p USB 摄像头（旧手机也可用） | 视觉监控 | 0-150元 |
| 边缘设备 | 树莓派 4B（已有则无需购买） | AI 推理 + Klipper 主机 | 0-350元 |
| 温湿度传感器 | BME280 I2C | 腔体环境监测 | 20元 |
| 麦克风（可选） | USB 麦克风 | 语音控制 | 50元 |
| 智能插头 | 米家智能插座（支持功率监测） | 开关机 + 能耗统计 | 80元 |

**已有条件（零额外成本）：**
- 大鱼 TT 已刷 Klipper（Moonraker API 已启用）
- NAS 已就绪（进化模型训练 + 数据存储）
- 网络已通（内网访问）

---

## 四、进化数据模型

### SQLite 数据库（每台机器独立）

```sql
-- 打印任务表
CREATE TABLE print_jobs (
  id INTEGER PRIMARY KEY,
  model_name TEXT,
  material TEXT,          -- PLA/PETG/ABS/TPU
  file_hash TEXT,         -- 唯一识别模型
  started_at DATETIME,
  finished_at DATETIME,
  result TEXT,            -- success/failure/partial
  failure_type TEXT,      -- 失败分类（AI 判定）
  quality_score REAL,     -- AI 质量评分 0-100
  vibration_anomaly REAL, -- 振动异常分数 0-100（MPU6050）
  gcode_file TEXT
);

-- 打印层数据表（进化核心）
CREATE TABLE print_layers (
  id INTEGER PRIMARY KEY,
  job_id INTEGER,
  layer_height REAL,
  z_position REAL,
  speed_mult REAL,        -- 速度倍数
  temp_nozzle REAL,
  temp_bed REAL,
  fan_speed INTEGER,
  detection_result TEXT,  -- AI 层检结果
  anomaly_score REAL,     -- 异常分数
  FOREIGN KEY (job_id) REFERENCES print_jobs(id)
);

-- 参数调整记录表
CREATE TABLE param_adjustments (
  id INTEGER PRIMARY KEY,
  job_id INTEGER,
  param_name TEXT,
  old_value REAL,
  new_value REAL,
  trigger_reason TEXT,
  outcome TEXT,           -- improved/worsened/no_change
  FOREIGN KEY (job_id) REFERENCES print_jobs(id)
);

-- 模型参数知识库
CREATE TABLE param_knowledge (
  id INTEGER PRIMARY KEY,
  model_hash TEXT,         -- 模型指纹
  material TEXT,
  inferred_optimal_params TEXT,  -- JSON
  confidence REAL,
  updated_at DATETIME,
  sample_count INTEGER     -- 基于多少次打印
);
```

---

## 五、实施路线图（混合版）

### Phase 0：Obico 落地（即刻，1-2小时）
> 目标：零成本体验 AI 检测，验证硬件兼容性

- [ ] 注册 Obico.io 账号（免费层够用）
- [ ] 树莓派安装 Obico Agent（`wget` 一键脚本）
- [ ] 摄像头接入 + 角度调整（打印平台斜上方 45°）
- [ ] 连接大鱼 TT（Moonraker API 授权）
- [ ] Telegram 推送配置
- [ ] **验证：** 故意触发一次失败，观察 AI 检测效果
- **交付：** 实时视频 + AI 检测 + 失败推送

### Phase 1：远程监控 + 数据采集（周 1-3）
> 目标：C 模块核心功能上线，建立进化数据底座

- [ ] Obico 已接管：实时视频 + AI 检测 + Telegram 推送（Phase 0 成果）
- [ ] 部署 NAS 监控面板（Flask + Bootstrap，进度 + 温湿度）
- [ ] 接入 BME280 传感器（I2C → 树莓派 → MQTT → NAS）
- [ ] SQLite 数据库初始化（print_jobs / print_layers / param_adjustments / param_knowledge）
- [ ] Obico → SQLite 数据管道（每次打印完成后自动同步失败记录）
- [ ] 打印进度时间轴缩略图自动生成
- [ ] **验证：** 外出时远程观察一次完整打印，数据库有数据回流

### Phase 2：参数自优化（周 4-6）
> 目标：B 模块从数据积累到推理输出

- [ ] 特征工程管道（材料+几何+环境+机器状态）
- [ ] scikit-learn 训练脚本（NAS 上训练，树莓派只做推理）
- [ ] OrcaSlicer 参数自动导出（每次打印后更新知识库）
- [ ] 知识库推理 API（`/predict?model_hash=xxx&material=PLA`）
- [ ] **验证：** 同类模型第二次打印时参数与第一次不同（系统已学到东西）

### Phase 3：故障自动恢复（周 5-7）
> 目标：A 模块实现无需人工介入的闭环

- [ ] **MPU6050 加速度传感器接入**（~10元 I2C 模块）
  - 接线：VCC→3.3V / GND→GND / SDA→SDA / SCL→SCL
  - 树莓派启用 I2C：`sudo raspi-config` → Interface Options → I2C
  - Python 读取：`smbus2` + `mpu6050-registers` 库
- [ ] **振动特征提取**
  - 时域特征：RMS 加速度、峰值因子、峭度
  - 频域特征：FFT 主频、频谱熵
  - 打印正常 vs 异常的振动"指纹"对比
- [ ] **LSTM 异常检测模型**（Bhattacharya 2024 方案）
  - 训练数据：正常打印 + 已知失败场景
  - 推理：实时流，失败概率超过阈值 → 触发暂停
- [ ] **双传感器融合决策**
  - Obico（视觉）+ MPU6050（振动）同时报警 → 高置信度，立即停机
  - 任一传感器报警 → 降速 + 记录，等下一个确认信号
- [ ] 故障分类引擎（基于 Phase 2 积累的数据微调）
- [ ] 规则 + ML 混合决策引擎（根因分析 → 参数调整映射）
- [ ] Klipper 参数热更新（Moonraker SET + RESTART）
- [ ] 自动重试 + 层恢复（从失败层继续打印逻辑）
- [ ] 修复效果评估（重试成功率统计）
- [ ] **验证：** 模拟故障，打印机自动发现、自动调整、打印成功

> **参考论文：** Bhattacharya et al. 2024, Procedia CS — "振动+LSTM"方案
> **硬件成本：** MPU6050 ~10元，无需额外 PCB

### Phase 4：AI 助手（周 6-8）
> 目标：D 模块实现自然语言控制

- [ ] Ollama 本地 LLM 部署（Qwen2.5-7B 或 DeepSeek）
- [ ] 对话式控制框架（意图识别 → 参数操作 → 反馈）
- [ ] 意图分类：查询/修改/分析/建议/控制/报告
- [ ] TTS 语音播报（打完一句话主动播报）
- [ ] **验证：** 用自然语言完成一次完整打印参数设置

### Phase 5：系统集成 & 收尾（周 8-10）
> 目标：所有模块串联，全自动进化闭环

- [ ] 完整进化闭环演示（A→B→C→D 联动）
- [ ] Web 控制面板（含 AI 助手 UI）
- [ ] 导出迁移脚本（其他 Klipper 机器可复用）
- [ ] 文档完善（更新 AI校准进化实战指南.md）

---

## 六、技术栈选型

| 层级 | 技术 | 理由 |
|------|------|------|
| AI 推理 | Ollama + Qwen2.5-7B | 本地隐私、免费、成熟 |
| 视觉模型 | Obico / Ultralytics YOLOv8 | 15+ 预训练失败类型 + 可微调 |
| 进化学习 | scikit-learn + PyTorch | 轻量模型适合树莓派/NAS |
| 固件通信 | Moonraker REST API | Klipper 官方，无缝集成 |
| 数据库 | SQLite | 零运维，NAS 存储 |
| 消息推送 | Telegram Bot API | 即时、可靠、免费 |
| 时序数据 | InfluxDB（可选） | 温湿度/电流长期存储 |
| 控制面板 | Flask + Bootstrap | 轻量、自己可控 |

---

## 七、风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|------|------|------|
| 树莓派算力不足 | 中 | 高 | 先用 NAS 训练模型，树莓派只做推理 |
| Klipper 参数热更新丢失 | 低 | 高 | 每次更新前备份配置到 NAS |
| AI 误报导致错误重试 | 中 | 中 | 设置置信度阈值（>80% 才自动执行） |
| 摄像头夜间失效 | 低 | 低 | 补光灯或用夜视摄像头 |
| 进化模型过拟合 | 中 | 中 | 定期用随机参数对照实验 |

---

## 八成功标准

- [ ] 连续 10 次打印，AI 全部正确判断状态
- [ ] 同类模型第三次打印时，参数已与第一次不同（证明已学习）
- [ ] 一次自动故障恢复成功（无需人工介入）
- [ ] 用自然语言完成一次"查询状态 + 修改参数 + 开始打印"

---

*设计完成。混合方案优势：Phase 0 当晚体验，Phase 1-5 逐步叠加，不重复造轮子。*
