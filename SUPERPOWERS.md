# 大鱼TT — Superpowers 项目宪章

> 本项目采用 Superpowers AI Agent 协作框架

## 1. 角色定义

| 角色 | 职责领域 | 核心任务 |
|------|---------|---------|
| 机械专家 | MECHANICAL | 框架分析、STL选型、硬件改进、封箱方案 |
| 热管理专家 | THERMAL | 腔体温控、加热系统、散热设计 |
| 固件专家 | FIRMWARE | Klipper配置、引脚定义、宏开发 |
| AI专家 | AI | Input Shaper、ADXL345、智能化 |
| 测试工程师 | VALIDATION | 测试验证件、量化指标、验收标准 |

## 2. 工作流程

所有任务必须遵循以下流程：

1. **Brainstorming** — 理解需求，探索方案
2. **Spec** — 输出设计文档并获批
3. **Plan** — 编写实现计划
4. **Implementation** — 执行实现
5. **Verification** — 验证交付物
6. **Delivery** — 收尾交付

## 3. 决策规则

- 单领域决策：领域负责人自主决定
- 跨领域决策：涉及多领域时，负责人协商；无法达成共识时，提请仲裁
- 架构级变更：需更新 SPEC.md + 相关 DOMAIN.md

## 4. 文档规范

- 文件命名：`序号_标题.md`（两位数字）
- 每领域独立 `DOMAIN.md` 索引
- 新增文档必须同步更新索引
