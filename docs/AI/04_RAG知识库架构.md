# RAG 知识库架构

> 让 AI 真正理解你的打印机——基于 Klipper 领域知识的 RAG 问答系统

---

## 1. 为什么 3D 打印需要 RAG？

通用 LLM（如 GPT-4、Qwen、Llama）的问题是：

- **不知道 Klipper**：不了解 `input_shaper`、`pressure_advance`、`bed_mesh` 的物理意义
- **不知道大鱼 TT**：不知道这台机器的电机参数、热床配置、历史故障
- **不知道你的经验**：你花了几十小时调试出来的最优参数，AI 一无所知
- **幻觉风险**：LLM 可能编造不存在的 Klipper G-code 命令

**RAG（检索增强生成）** 是解决以上问题的最佳方案：通过向量化检索相关知识，让 LLM 在真实、准确的领域知识基础上回答问题。

---

## 2. 推荐架构

### 完整技术栈

```
┌─────────────────────────────────────────────────────────────────┐
│                       RAG 知识库系统                              │
│                                                                 │
│  ┌──────────────┐                                               │
│  │  数据来源     │  Klipper 官方文档 / Voron 社区 / 大鱼 TT 经验  │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │  文档解析     │ ──▶ │  分块 (Chunk) │ ──▶ │  向量化      │   │
│  │  (Loader)    │     │  Overlap     │     │  (Embedding) │   │
│  └──────────────┘     └──────────────┘     └──────┬───────┘   │
│                                                    │            │
│                                                    ▼            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    向量数据库                              │  │
│  │              (Chroma / Qdrant / FAISS)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LangChain / LlamaIndex                       │  │
│  │              RAG Pipeline                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────┐     ┌──────────────┐                       │
│  │  Ollama      │ ◀── │  Query       │  用户提问              │
│  │  (LLM)       │     │  检索匹配     │                       │
│  └──────────────┘     └──────────────┘                       │
│                                                                 │
│  Moonraker API ────▶ Klipper 实时状态 ──▶ 知识库上下文         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 组件详解

#### 数据来源层

| 来源 | 内容 | 采集方式 |
|------|------|---------|
| Klipper 官方文档 | 配置参考、G-code 命令、故障排除 | 官方 GitHub / 网站抓取 |
| Klippain 文档 | 输入整形、PA、Flow 校准最佳实践 | Klippain GitHub |
| Voron 社区知识 | 硬件改装、调试经验、常见问题 | Discord 频道 + GitHub Issues |
| 大鱼 TT 内部知识 | 机器配置、历史故障记录、调参经验 | 手动维护 + 自动化采集 |
| Moonraker 日志 | 实时打印状态、错误日志、参数历史 | Moonraker API 拉取 |

#### 文档解析与分块

原始文档需要经过处理才能用于 RAG：

```python
# 文档分块策略
chunk_config = {
    "chunk_size": 512,           # 每块 token 数
    "chunk_overlap": 128,        # 重叠 token 数（保持上下文连续性）
    "separators": ["\n## ", "\n### ", "\n\n"],  # 按标题/段落分割
}
```

**分块原则**：
- 配置类文档（printer.cfg 示例）：按配置段落分块，每块 ~200–500 tokens
- 故障排查指南：按问题场景分块，每个块对应一个独立故障
- 教程类文档：按步骤分块，每块 ~300–800 tokens

#### 向量化（Embedding）

```python
# 推荐嵌入模型
embedding_models = {
    # 本地轻量（CPU 可跑）
    "nomic-embed-text": {
        "dimensions": 768,
        "performance": "中等精度，CPU 可用",
        "模型大小": "~140MB"
    },
    # 本地高质量（需 GPU）
    "bge-m3": {
        "dimensions": 1024,
        "performance": "高质量，中文支持好",
        "模型大小": "~1GB"
    },
    # 云端（最高精度）
    "text-embedding-3-large": {
        "dimensions": 3072,
        "performance": "最高精度",
        "成本": "按 token 计费"
    }
}
```

#### 向量数据库

| 数据库 | 特点 | 适用场景 |
|-------|------|---------|
| **Chroma** | 轻量、易用，Python 原生 | 个人/小规模部署（推荐）|
| **Qdrant** | 高性能，支持过滤，Rust 实现 | 生产环境 |
| **FAISS** | Facebook 开源，GPU 加速 | 超大规模数据 |
| **Milvus** | 云原生，分布式 | 企业级 |

#### LLM 层

```python
# 本地 LLM 推荐（通过 Ollama 运行）
local_llms = {
    "qwen2.5:7b": {
        "中文能力": "优秀",
        "Klipper 领域知识": "良好（需微调）",
        "硬件需求": "8GB RAM",
        "推理速度": "CPU: 10–15 tok/s"
    },
    "llama3.1:8b": {
        "中文能力": "中等",
        "Klipper 领域知识": "需 RAG 补充",
        "硬件需求": "8GB RAM",
        "推理速度": "CPU: 8–12 tok/s"
    },
    "deepseek-r1:7b": {
        "中文能力": "优秀",
        "推理能力": "最强",
        "硬件需求": "8GB RAM",
        "成本": "免费本地"
    }
}
```

---

## 3. 大鱼 TT 知识库内容

### 核心知识分类

```
📚 大鱼 TT 知识库
│
├── 📖 Klipper 官方文档
│   ├── 配置参考（printer.cfg 各模块）
│   ├── G-code 命令手册
│   ├── 故障排查指南
│   └── 传感器配置（ADXL345、MPU6050）
│
├── 🔧 校准实战知识
│   ├── Klippain Shaketune 使用指南
│   ├── PressureAdvance 校准最佳实践
│   ├── 床网探测参数优化
│   └── Flow 校准经验值
│
├── ⚠️ 故障排查手册
│   ├── Spaghetti 检测与处理
│   ├── Ringing / 振纹根治指南
│   ├── 层移（Layer Shift）原因分析
│   ├── 堵塞（Filanent）预防与处理
│   ├── 翘曲（Warp）解决方案
│   └── 热端温度异常排查
│
├── 🏭 大鱼 TT 专属知识
│   ├── 机器配置参数（step/mm、皮带轮比）
│   ├── 历史故障日志（Moonraker 导出）
│   ├── 已验证的最优参数组合
│   └── 硬件改装记录（AWD 等）
│
└── 📊 参数经验库
    ├── 耗材参数库（PLA / PETG / ABS / TPU）
    ├── 速度-质量平衡曲线
    └── 加速度-振动关系数据
```

### 知识采集自动化

部分知识可以通过脚本自动采集，减少人工维护成本：

```python
# 自动采集 Moonraker 打印历史
import asyncio
from moonraker import MoonrakerClient

async def harvest_print_history():
    client = MoonrakerClient("http://localhost:7125")
    
    # 获取最近 100 次打印记录
    history = await client.get_printer_objects("history")
    
    # 提取有价值的元数据
    for print_job in history.jobs:
        metadata = {
            "filename": print_job.filename,
            "duration": print_job.duration,
            "status": print_job.status,  # completed / failed / cancelled
            "error": print_job.fail_reason if print_job.failed else None,
            "params_used": print_job.virtual_sdcard.progress,
        }
        # 存入知识库（自动关联成功/失败标签）
```

---

## 4. RAG 问答示例

### 示例 1：Ringing 问题诊断

**用户问题**：
> "打印时拐角有明显的振纹，特别是在高速打印时更严重，是什么原因？"

**RAG 检索结果**（Top 3）：

```
1. [Klipper 官方] Input Shaping - 高速打印时由于机械谐振导致 ringing
   匹配度：95%
   摘要：输入整形通过在激励信号中引入整形滤波器来减少结构共振...

2. [Klippain 文档] Ringing 消除实战 - ADXL345 + Shaper Calibrate 步骤详解
   匹配度：88%
   摘要：使用 ADXL345 测量共振频率后，通过 SHAPER_CALIBRATE 计算最优参数...

3. [Voron 社区] 高速打印 ringing 解决方案
   匹配度：82%
   摘要：Voron 2.4 在 200mm/s+ 时常见的 ringing 问题可通过以下方式解决...
```

**LLM 综合回答**：
> 基于 Klipper Input Shaping 原理，您遇到的 ringing 是由于打印机在高速转向时产生的机械谐振未被抑制造成的。建议按以下步骤处理：
>
> 1. 安装 ADXL345 加速度计（¥15）
> 2. 运行 `TEST_RESONANCES` 测试 X/Y 轴
> 3. 运行 `SHAPER_CALIBRATE` 计算最优 IS 参数
> 4. 使用 Klippain Shaketune 可视化验证效果
>
> 校准后预期可将 ringing 消除 80–95%，加速度上限可提升至 6000–13000 mm/s²。

### 示例 2：PA 值推荐

**用户问题**：
> "我用的是 eSUN PLA，PA 值应该设置多少？"

**RAG 检索结果**：
```
1. [参数经验库] eSUN PLA 参数推荐
   匹配度：93%
   摘要：eSUN PLA 推荐 PA 值范围 0.03–0.05，默认建议 0.04...

2. [Klipper 文档] Pressure Advance 调优指南
   匹配度：85%
   摘要：不同耗材的 PA 值受材料压缩性和喷嘴直径影响...
```

**LLM 回答**：
> eSUN PLA 的推荐 PA 值为 **0.04**（默认值），可在 0.03–0.05 之间微调。建议使用 PressureAdvanceCamera（USB 内窥镜）进行自动化校准，分钟级即可获得精确值。

---

## 5. 实施路径

### Phase 1：基础 RAG（1–2 周）

**目标**：建立最小可用知识库，实现 Klipper 知识问答。

| 步骤 | 内容 | 工作量 |
|------|------|-------|
| 1 | 安装 Ollama，拉取 embedding 模型（nomic-embed-text）| 0.5h |
| 2 | 搭建 Chroma 向量数据库 | 0.5h |
| 3 | 手动上传 Klipper 官方文档（约 50 篇）| 2–3h |
| 4 | 实现简单 RAG Pipeline（LangChain）| 2–3h |
| 5 | Web UI 界面（可选，Streamlit 快速原型）| 1–2h |

**验收标准**：用户提问"什么是 Input Shaping"，系统能返回准确答案。

### Phase 2：自动知识采集（2–4 周）

| 步骤 | 内容 | 工作量 |
|------|------|-------|
| 1 | Moonraker API 集成，自动采集打印历史 | 3–5h |
| 2 | 自动将故障日志解析入库 | 2–3h |
| 3 | 增量更新机制（新文档自动分块+向量化）| 3–5h |
| 4 | 参数经验库结构化存储（JSON/SQLite）| 2–3h |

### Phase 3：知识库质量提升（持续）

| 方向 | 内容 |
|------|------|
| 反馈闭环 | 用户对回答的满意/不满意的反馈自动进入知识库 |
| 知识蒸馏 | 从 LLM 回答中提取新的结构化知识 |
| 多模态 | 支持图片（如缺陷照片）检索 |
| 微调 | 积累足够数据后 fine-tune 专用 Klipper LLM |

---

## 6. 技术选型汇总

| 组件 | 推荐选型 | 替代方案 |
|------|---------|---------|
| LLM | Ollama + DeepSeek-R1:7b / Qwen2.5:7b | GPT-4o（云端）|
| Embedding | Nomic Embed Text（本地）/ BGE-M3（高精度）| OpenAI text-embedding-3 |
| 向量库 | Chroma（个人）/ Qdrant（生产）| FAISS / Milvus |
| RAG 框架 | LangChain / LlamaIndex（任选）| 纯 Python 手写 |
| API 网关 | Moonraker（Klipper 原生）| FastAPI 封装 |
| 前端 | Streamlit（快速原型） / Gradio | React WebApp |

---

## 7. 参考资源

- [LangChain RAG 官方文档](https://python.langchain.com/)
- [LlamaIndex 官方文档](https://www.llamaindex.ai/)
- [Chroma 向量数据库](https://www.trychroma.com/)
- [Ollama 官方](https://ollama.com/)
- [Klipper 官方文档](https://www.klipper.info/)
- [Klippain GitHub](https://github.com/Frix-x/klippain)

---

> **下一步**：[自我演化控制系统](./5-自我演化控制系统.md) — 从"工具使用者"到"自我改进者"，了解大鱼 TT 的 AI 自我演化完整路径。
