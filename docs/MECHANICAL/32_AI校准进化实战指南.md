# AI 校准进化实战指南

> 文档版本：v2.0（混合方案）
> 更新日期：2026-03-27

---

## 概述：大鱼 TT 自我进化系统

大鱼 TT + Klipper + Fluidd，已接入 Phase 0 混合方案，逐步实现自我进化。

**架构原则：**
- Obico 管感知（视觉 AI 检测），NAS 管思考（进化引擎），不重复造轮子
- 数据全部本地存储，不依赖云端

---

## Phase 0：Obico AI 检测（即刻）

### 硬件状态
- [x] Klipper 固件（Fluidd WebUI）
- [x] Debian 树莓派
- [x] USB 摄像头

### 安装步骤

**Step 1：注册 Obico 账号**
- 地址：https://app.obico.io
- 注册后获取 **Server Link Code**（6位字母）

**Step 2：SSH 进树莓派安装 Agent**

```bash
wget -O install.sh https://raw.githubusercontent.com/TheSpaghettiDetective/obico-server/master/scripts/install.sh
sudo bash install.sh
```

安装过程选择：
- Printer type → `Klipper (Fluidd/Mainsail)`
- Moonraker 地址 → `http://<树莓派IP>:80`
- Server Link Code → 填 Step 1 的 6 位码

**Step 3：Telegram Bot 配置**
1. Telegram 搜索 @BotFather → /newbot → 记下 Token
2. Obico 网页 → Settings → Notifications → 填入 Token
3. 关注自己创建的 Bot → 发送 /start

**Step 4：摄像头角度**
- 距平台 25-30cm，斜下 45°
- 喷嘴和整层打印面都在画面内

### 验证标准
- [ ] App 实时画面正常
- [ ] 制造一次失败（Telegram 3 分钟内收到通知）
- [ ] App 可远程暂停/取消打印

---

## Phase 1：数据采集 + NAS 监控（1-3 周）

**目标：** 建立进化数据底座

- [ ] SQLite 数据库初始化（print_jobs / print_layers / param_adjustments / param_knowledge）
- [ ] NAS 监控面板（Flask + Bootstrap）
- [ ] BME280 腔体传感器（I2C → MQTT → NAS）
- [ ] Obico → SQLite 数据管道

### 数据库设计

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
  failure_type TEXT,      -- AI 判定失败类型
  quality_score REAL,     -- AI 质量评分 0-100
  gcode_file TEXT
);

-- 参数调整记录
CREATE TABLE param_adjustments (
  id INTEGER PRIMARY KEY,
  job_id INTEGER,
  param_name TEXT,
  old_value REAL,
  new_value REAL,
  trigger_reason TEXT,
  outcome TEXT            -- improved/worsened/no_change
);

-- 参数知识库
CREATE TABLE param_knowledge (
  id INTEGER PRIMARY KEY,
  model_hash TEXT,
  material TEXT,
  inferred_optimal_params TEXT,  -- JSON
  confidence REAL,
  updated_at DATETIME,
  sample_count INTEGER
);
```

---

## Phase 2：参数自优化引擎（4-6 周）

**目标：** 系统自动学习最优参数，不用手动调

- [ ] 特征工程管道（材料+几何+环境+机器状态）
- [ ] scikit-learn 训练脚本（NAS 训练，树莓派推理）
- [ ] OrcaSlicer 参数自动导出
- [ ] 推理 API：`/predict?model_hash=xxx&material=PLA`

---

## Phase 3：故障自动恢复闭环（5-7 周）

**目标：** 失败后无需人工介入，自动分析+调整+重试

- [ ] **MPU6050 振动传感器接入**（~10元，I2C 直连树莓派）
  - 接线：VCC→3.3V / GND→GND / SDA→SDA / SCL→SCL
  - 树莓派启用 I2C：`sudo raspi-config` → Interface Options → I2C
- [ ] 振动特征提取（时域 RMS + 频域 FFT 主频）
- [ ] LSTM 异常检测（Bhattacharya 2024 方案）
- [ ] 双传感器融合：Obico（视觉）+ 振动（MPU6050）
- [ ] Klipper 参数热更新 + 自动重试

### 双传感器协同

| 传感器 | 检测目标 | 优势 |
|--------|---------|------|
| Obico 视觉 | 错位/spaghetti/塌陷 | 直观，可远程确认 |
| MPU6050 振动 | 内部层间分离/挤出异常 | 视觉盲区，提前预警 |

---

## Phase 4：AI 助手对话控制（6-8 周）

**目标：** 自然语言控制打印机

- [ ] Ollama 本地 LLM 部署（Qwen2.5-7B）
- [ ] 意图识别：查询/修改/分析/建议/控制/报告
- [ ] Telegram AI 对话入口

---

## Phase 5：系统集成收尾（8-10 周）

- [ ] 完整进化闭环演示
- [ ] Web 控制面板（含 AI 助手 UI）
- [ ] 导出可复用迁移脚本

---

## 详细设计文档

完整架构、技术选型、风险分析见：
`docs/plans/2026-03-27-self-evolving-design.md`
