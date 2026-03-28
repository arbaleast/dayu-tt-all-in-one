# VLM 打印质量监控

> 利用视觉语言模型（VLM）和多 Agent 协作框架，让 AI 具备"看懂"打印质量的能力

---

## 1. VLM 质检 vs 传统故障检测

传统故障检测（如 Obico）本质上是**二分类问题**——有故障 / 无故障，依赖大量标注数据训练专用检测模型。

VLM（视觉语言模型）质检则更进一步：

- **可解释性**：不仅判断"有问题"，还能描述"哪里有问题、是什么类型的缺陷"
- **零样本泛化**：无需针对 3D 打印专门训练，GPT-4V 等模型自带通用视觉理解能力
- **语义推理**：能理解打印场景中的空间关系和物理因果（如"第三层右侧有过冲"）

这一方向仍处于学术前沿向生产过渡阶段，代表了 3D 打印质量监控的未来方向。

---

## 2. LLM-3D Print 多 Agent 框架

### 论文背景

LLM-3D Print 是当前最完整的 3D 打印 VLM 质检框架，发表于 *Additive Manufacturing*（2025 年 9月），[arXiv 链接](https://arxiv.org/abs/2408.14307)。

### 三 Agent 协作架构

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM-3D Print 闭环                       │
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   │   Monitor   │───▶│   Reasoner  │───▶│   Executor  │   │
│   │   Agent     │    │   Agent     │    │   Agent     │   │
│   └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │            │
│         ▼                  ▼                  ▼            │
│   逐层图像采集         缺陷根因分析       参数修正执行      │
│   质量评估             知识推理           Klipper API 调    │
│                                                             │
│   逐层循环：Monitor ───────────────────────────────▶        │
└─────────────────────────────────────────────────────────────┘
```

#### Monitor Agent（监控 Agent）

**职责**：逐层拍摄图像，评估当前层质量

**工作流程**：
1. 接收每层打印完成信号（Klipper `event_posession` 或 G-code 宏）
2. 触发摄像头拍摄当前层完整画面
3. 将图像 + 打印参数（speed / flow / temp / layer height）发送给 VLM
4. VLM 返回质量评分和缺陷描述

**输入示例**：
```
当前层：第 47 层 / 共 200 层
参数：speed=60mm/s, flow=98%, temp=215°C, layer_height=0.2mm
```

**输出示例**：
```
质量评分：7.5/10
检测到缺陷：轻微过冲（右侧拐角）
置信度：中（60%）
建议：降低 flow 至 96% 或提高 PA 0.002
```

#### Reasoner Agent（推理 Agent）

**职责**：综合多帧信息，进行缺陷根因分析

**工作流程**：
1. 收集 Monitor Agent 的历史评估记录
2. 分析缺陷的空间连续性（如连续 3 层同一位置出现过冲）
3. 结合领域知识（Klipper 参数物理意义、耗材特性）进行因果推理
4. 给出明确的根因判断，而非仅描述现象

**推理示例**：
```
问题：第 45–47 层连续出现右侧拐角过冲
分析：
  - 过冲仅出现在右侧拐角，同一角度重复出现
  - 温度、流量在第 40 层后无变化
  - PA 当前值为 0.045（低于该耗材推荐范围 0.05–0.06）
根因：PA 值偏低，无法补偿喷嘴压力延迟
建议：将 PA 从 0.045 调整至 0.052
```

#### Executor Agent（执行 Agent）

**职责**：通过 Klipper Moonraker API 动态修改参数，并验证效果

**可修改的参数**：

| 参数类别 | 可调参数 |
|---------|---------|
| 挤出 | `extrusion_multiplier`（Flow）、`pressure_advance` |
| 速度 | `max_velocity`、`max_accel` |
| 温度 | `heater_bed_temp`、`heater_core_temp` |
| Z 偏移 | `z_offset`（精细调整首层）|

**执行流程**：
```bash
# 通过 Moonraker API 修改参数
curl -X POST "http://localhost:7125/machine/smp/parameter" \
  -d '{"param": "extruder.pressure_advance", "value": 0.052}'

# 验证修改：重新评估第 48 层质量
# 如果质量提升 ≥ 阈值：参数写入配置文件（永久生效）
# 如果质量无改善：回滚参数，触发人工干预
```

### 完整闭环流程

```
Layer 47 完成
    ↓
Monitor Agent：拍摄 + VLM 评估 → 7.5/10，过冲
    ↓
Reasoner Agent：分析历史 3 层 → 根因 PA 偏低
    ↓
Executor Agent：修改 PA = 0.052 → 验证第 48 层
    ↓
Monitor Agent：第 48 层 → 9.2/10，质量改善 ✅
    ↓
Executor Agent：写入配置，PA=0.052 永久生效
    ↓
继续打印 → 下一层
```

---

## 3. 本地 VLM 方案：Moondream / Ollama 集成

### 为什么需要本地 VLM？

云端 VLM（如 GPT-4V）存在：
- **隐私问题**：打印画面上传外部服务器
- **成本**：GPT-4o 图像分析按次计费
- **延迟**：网络往返影响实时性
- **依赖**：断网即失效

**本地 VLM 是生产级部署的必要条件。**

### 推荐本地 VLM 方案

#### Moondream（推荐，轻量级）

[Moondream](https://github.com/vidursatija/Moondream) 是专为边缘设备优化的视觉模型：
- 参数量：约 1.8B
- 内存需求：~4GB RAM
- 支持 Ollama 格式，可直接通过 Ollama API 调用
- 推理速度：树莓派 4B 可达 5–10 FPS（图像分析场景足够）

```bash
# 安装 Moondream（通过 Ollama）
ollama pull moondream

# API 调用示例
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "moondream",
    "prompt": "这是一层 3D 打印的俯视图。请描述：1) 是否有任何可见缺陷（如过冲、欠冲、溢料） 2) 整体质量评分 1-10",
    "images": ["base64编码的图像数据"]
  }'
```

#### Ollama（模型运行平台）

[Ollama](https://ollama.com/) 是本地 LLM / VLM 推理的事实标准：
- 支持 Llama 3.1、Qwen2.5、Mistral 等主流开源模型
- 支持视觉模型：llava、moondream、qwen2-vl
- 通过 REST API 与 Klipper / Moonraker 集成
- 一键启动，无需 GPU（CPU 推理可用）

```bash
# 安装 Ollama（Linux）
curl -fsSL https://ollama.com/install.sh | sh

# 拉取视觉模型
ollama pull llava:latest      # 通用来聊模型（7B）
ollama pull moondream:latest   # 轻量视觉模型

# 后台运行服务
ollama serve
```

### 本地 VLM 质检服务架构

```
┌──────────────────────────────────────────────────────────────┐
│                      本地 VLM 质检系统                         │
│                                                              │
│   Klipper (Klipper 打印中)                                   │
│       │                                                      │
│       ▼ event (layer complete)                              │
│   Moonraker API ──────────────┐                              │
│                               │                              │
│   ┌───────────────────────────▼───────────────┐              │
│   │          VLM 质检服务（本地）              │              │
│   │                                           │              │
│   │  Camera ──▶ Frame ──▶ Ollama (Moondream) │              │
│   │                              │            │              │
│   │                     Quality Report        │              │
│   │                              │            │              │
│   │                     [缺陷阈值?]            │              │
│   │                    是/否 ────▶ 决策        │              │
│   └───────────────────────────────────────────┘              │
│                               │                              │
│   Moonraker API ◀────── 告警 / 参数调整                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 性能基准（树莓派 4B / 8GB）

| 模型 | 图像分析延迟 | 内存占用 | 适用场景 |
|------|------------|---------|---------|
| moondream | 2–5 秒/图 | 3–4 GB | 实时质检（推荐）|
| llava-7b | 5–10 秒/图 | 6–7 GB | 高精度分析 |
| qwen2-vl | 3–7 秒/图 | 5–6 GB | 中文界面优先 |

---

## 4. 逐层图像评估流程

### 触发机制

每层打印完成时，Klipper 发送 `layer_complete` 事件，触发图像采集：

```python
# moonraker.conf 中的 gcode_macro
[gcode_macro LAYER_COMPLETE]
gcode:
  _CAPTURE_AND_ANALYZE

[gcode_shell_command capture_analyze]
command: /root/vlm质检/capture_and_analyze.sh
timeout: 30
```

### 采集参数

| 参数 | 值 | 说明 |
|------|---|------|
| 分辨率 | 640×480（可调）| 平衡清晰度与传输速度 |
| 角度 | 俯视（90°）| 最能反映层质量 |
| 光照 | 建议补光 | LED 环可减少阴影 |
| 触发时机 | 层完成后 2s | 等待运动停止再拍摄 |

### 评估指标体系

VLM 质检采用多维度评分：

| 维度 | 权重 | 说明 |
|------|------|------|
| 轮廓清晰度 | 20% | 边缘是否平滑，有无溢料 |
| 表面质量 | 25% | 有无气泡、杂质、变色 |
| 尺寸精度 | 20% | 尺寸是否符合预期 |
| 层间一致性 | 20% | 与相邻层的一致性 |
| 缺陷严重度 | 15% | 过冲/欠冲/spaghetti 等缺陷 |

### 决策阈值

```yaml
quality_thresholds:
  excellent: 9.0  # >= 9.0，继续打印
  good: 7.5       # 7.5-9.0，记录并继续
  warning: 6.0    # 6.0-7.5，发送告警，建议检查
  critical: 0.0   # < 6.0，暂停打印，等待人工确认
```

---

## 5. 大鱼 TT 的 VLM 质检实施路径

### Phase 1：基础设施（立即可做）

1. 在树莓派或 x86 小主机上安装 Ollama
2. 拉取 moondream 模型，本地测试图像分析 API
3. 编写 Klipper 宏，实现每层拍照触发
4. 简单 Demo：VLM 返回质量文字描述（无自动干预）

### Phase 2：集成监控（1–3 个月）

1. 将 Ollama VLM 推理服务封装为 Moonraker 插件
2. 实现 Monitor Agent：逐层采集 + VLM 推理 + 评分
3. 实现 Reasoner Agent：简单规则引擎（连续 3 层警告则暂停）
4. 对接 OctoEverywhere / Obico 作为备选告警渠道

### Phase 3：完整闭环（中期目标）

1. 实现完整的 Executor Agent，通过 Moonraker API 修改 Klipper 参数
2. 从历史打印数据中学习，建立参数 → 质量映射知识库
3. 实现自我演化控制（见 [自我演化控制系统](./5-自我演化控制系统.md)）

---

## 6. 参考资源

- [LLM-3D Print 论文 (arXiv:2408.14307)](https://arxiv.org/abs/2408.14307)
- [Ollama 官网](https://ollama.com/)
- [Moondream GitHub](https://github.com/vidursatija/Moondream)
- [QA-VLM：金属增材制造 VLM 质检 (arXiv)](https://arxiv.org/)
- [InspectVLM (ICCV 2025)](https://cvf.anyang.ac.kr/)

---

> **下一步**：[RAG知识库架构](./4-RAG知识库架构.md) — 构建大鱼 TT 专属的 Klipper 知识助手，让 AI 能回答"我的打印机为什么会有 ringing"。
