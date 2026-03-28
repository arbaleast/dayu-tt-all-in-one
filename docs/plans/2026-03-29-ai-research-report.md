# AI 技术调研 — 大鱼 TT 可用方案

> 调研时间：2026-03-29
> 来源：并行深度搜索（3路并发）
> 涵盖：AI 校准 / 故障检测 / VLM 质检 / RAG 知识管理 / 自演化控制 + Voron 社区改装

---

## 一、AI 自动校准

### Klipper Input Shaping（生产可用 ⭐⭐⭐⭐）

| 指标 | 数据 |
|------|------|
| 加速度上限 | 6,000–13,000 mm/s²（校准后）|
| Ringing 消除率 | 80–95% |
| 所需硬件 | ADXL345 加速度计（¥15）|
| 核心工具 | Klippain Shaketune（Mainsail/Fluidd WebUI 内完成）|

**推荐流程：** `ADXL345` → `TEST_RESONANCES` → `SHAPER_CALIBRATE` → `klippain-shaketune` 可视化

### PressureAdvanceCamera（自动化 PA 校准 ⭐⭐⭐⭐）

- 低价 USB 内窥镜拍摄打印线条，CV 自动测量最优 PA 值
- 完全替代传统打印测试塔
- 校准时间：分钟级（传统 10-30 分钟）

### Klippain 主配置栈（自动化工作流 ⭐⭐⭐⭐）

- 集成 Input Shaper + 自适应床网 + PA 标定 + Flow 标定 + 振动测量
- 校准时间从 ~2h → ~15min

---

## 二、AI 故障检测（生产级，开源生态丰富）

### Obico（原 Spaghetti Detective）⭐⭐⭐⭐⭐

| 指标 | 数据 |
|------|------|
| 检测类型 | spaghetti、blob、warp、layer shift、喷嘴堵塞 |
| 免费额度 | 每月 10 AI 小时 |
| 部署方式 | 云端 / 本地 Docker |
| Klipper 接入 | Moonraker-Obico 插件 |

**已集成到大鱼 TT 项目（Phase 0）。**

### OctoEverywhere Gadget ⭐⭐⭐⭐

- 免费无限量
- CNN 视觉故障检测 + 自动暂停
- 支持 Bambu Lab、Prusa、Creality 等主流机型

### OctoPrint-PiNozCam ⭐⭐⭐

- 树莓派本地运行，边缘推理
- 无需 GPU，ARM CPU 即可

### 3DPrintSentinel ⭐⭐⭐

- 完全本地化，复用 Obico 模型
- 数据不外传，隐私优先

---

## 三、VLM / LLM 打印质量监控（学术前沿）

### LLM-3D Print ⭐⭐⭐（最完整框架）

论文：[Additive Manufacturing, Sep 2025](https://arxiv.org/abs/2408.14307)

多 Agent 协作：
- **Monitor Agent**：逐层拍摄图像，评估质量
- **Reasoner Agent**：识别缺陷根因
- **Executor Agent**：通过 API 修改参数（flow/speed/temp/z-offset）

特点：无需训练数据，GPT-4o 等 VLM 本身具备 in-context learning 能力

### QA-VLM ⭐⭐⭐

VLM 对金属增材制造进行可解释质量评估，方法论可迁移至 FDM

### 学术论文列表

| 论文 | 方向 | 来源 |
|------|------|------|
| Real-time defect detection using lightweight CNN (IJAM 2024) | FDM 缺陷检测 | ResearchGate |
| LSTM-based FDM anomaly detection (2024) | 室温波动异常感知 | tandfonline |
| InspectVLM (ICCV 2025) | 统一 VLM 工业检测 | CVF |
| GPT-4V/LLaVA 工程设计评估 (Springer 2025) | VLM 缺陷识别 | Springer |

---

## 四、RAG 知识管理（高度可做，空白方向）

**现状：** 无专用 3D 打印 RAG 系统，但核心技术路径已成熟。

**推荐架构：**
```
Moonraker API（Klipper 状态读写）
    ↓
LangChain / LlamaIndex（RAG 框架）
    ↓
Ollama（本地 LLM + 嵌入）
    ↓
向量数据库（Chroma / Qdrant）
    ↓
3D 打印机专属知识库
  - Klipper 配置文档
  - 故障排查手册
  - 切片参数经验库
```

---

## 五、自演化控制系统

### LLM-3D Print 多 Agent 闭环（学术前沿）

Monitor → Reasoner → Executor 闭环：
- 缺陷检测 → 根因分析 → 参数修正 → 验证
- 无需人工干预

### Reinforcement Learning 闭环控制

论文：[ResearchGate 2026](https://www.researchgate.net/publication/401631922)
RL 实时自适应优化 3D 打印参数

---

## 六、Voron 社区高性能改装

### AWD Mod（All-Wheel Drive）⭐⭐⭐⭐⭐

| 配置 | 最高速度 | 最大加速度 |
|------|---------|----------|
| 普通 Voron 2.4 + IS | 300–400mm/s | 6,000–13,000 mm/s² |
| **Voron 2.4 + AWD + IS** | **600–1,000mm/s** | **20,000–100,000 mm/s²** |

套件：LDO CNC AWD Kit（专为 Voron V2.4 / Trident 设计）

### 皮带张力自动调节器 ⭐⭐⭐⭐

- CNC 加工免工具张力调节器
- 消除皮带走动导致的非均匀张力
- 配合 IS 后谐振频率提升 10-20%

### Klippain 配置栈（完整自动化校准）⭐⭐⭐⭐

集成：Input Shaper + 自适应床网 + PA + Flow + 振动测量

---

## 七、大鱼 TT 推荐技术路线

### 短期（立即可用）

| 升级 | 效果 | 成本 |
|------|------|------|
| Klippain Shaketune | IS 可视化自动校准 | ¥15（ADXL345）|
| Obico AI 故障检测 | 实时 spaghetti 检测 | 免费（基础版）|
| PressureAdvanceCamera | PA 分钟级自动化 | ¥30（USB 内窥镜）|

### 中期（1-2年）

| 升级 | 效果 | 成本 |
|------|------|------|
| AWD 四驱改装 | 速度 600mm/s+ | ¥350（LDO 套件）|
| CanBUS (SB2040) | 通信延迟 < 0.5ms | ¥150 |
| LLM-3D Print 本地化 | 多 Agent 自主质量监控 | 需要本地 LLM |

### 长期（构建壁垒）

| 方向 | 效果 | 说明 |
|------|------|------|
| RAG + 3D 打印知识库 | 专属 AI 问答助手 | 差异化最大 |
| 自演化参数优化 | 从历史中学习最优参数 | RL + LLM |

---

## 八、综合成熟度对比

| 方向 | 成熟度 | 大鱼 TT 可用性 |
|------|--------|--------------|
| AI 自动校准（IS/PA）| ⭐⭐⭐⭐ 生产级 | ✅ 立即可用 |
| AI 故障检测 | ⭐⭐⭐⭐ 生产级 | ✅ Obico 已集成 |
| VLM/LLM 质检 | ⭐⭐⭐ 学术+早期 | ⚠️ 需本地 VLM |
| RAG 知识管理 | ⭐⭐ 高度可做空白 | ⚠️ 需自建 |
| 自演化控制 | ⭐⭐⭐ 学术前沿 | ⚠️ 需 LLM 本地化 |
| AWD/高性能改装 | ⭐⭐⭐⭐ 生产级 | ⚠️ 需适配大鱼 TT |
