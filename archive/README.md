# 📦 项目归档说明

## 历史迁移记录

### 2026-03-22 项目整合

本次整合将三个分散的大鱼TT相关项目合并为统一的 **dayu-tt-all-in-one** 全能资料库。

---

## 原项目

### 1. 大鱼TT改进方案
- **原路径**: `/home/arbaleast/.openclaw/workspace/大鱼TT改进方案/`
- **内容**: 5个Markdown文档，涵盖硬件升级、软件配置、预算清单等
- **迁移至**: `docs/00-入门指南/`
- **状态**: ✅ 已整合

### 2. dayu-tt-enclosure (封箱项目)
- **原路径**: `/home/arbaleast/.openclaw/workspace/projects/dayu-tt-enclosure/`
- **内容**: 封箱方案专项，包括官方、汪汪队射手、李炫键等方案
- **迁移至**: `docs/01-封箱方案/`
- **状态**: ✅ 已整合
- **GitHub**: https://github.com/arbaleast/dayu-tt-enclosure (保留)

### 3. dayu-tt-all-in-one (本项目)
- **原路径**: `/home/arbaleast/.openclaw/workspace/projects/dayu-tt-all-in-one/`
- **角色**: 作为整合后的主项目
- **状态**: ✅ 主干项目

---

## 文件迁移映射

| 原项目 | 原文件 | 新位置 |
|--------|--------|--------|
| 大鱼TT改进方案 | 1-硬件升级方案.md | docs/00-入门指南/ |
| 大鱼TT改进方案 | 2-软件固件配置.md | docs/00-入门指南/ |
| 大鱼TT改进方案 | 3-配件清单与预算.md | docs/00-入门指南/ |
| 大鱼TT改进方案 | 4-安装指南索引.md | docs/00-入门指南/ |
| 大鱼TT改进方案 | 5-参考资料.md | docs/00-入门指南/ |
| dayu-tt-enclosure | docs/*.md | docs/01-封箱方案/ |
| dayu-tt-enclosure | bom/*.csv | docs/01-封箱方案/ |
| dayu-tt-enclosure | docs/42闭环电机/* | docs/01-封箱方案/42闭环电机/ |

---

## 旧项目处理方式

### 建议保留（只读）
- `/home/arbaleast/.openclaw/workspace/大鱼TT改进方案/` - 保留历史记录
- `/home/arbaleast/.openclaw/workspace/projects/dayu-tt-enclosure/` - 保留GitHub仓库

### 后续维护
- **只更新** `dayu-tt-all-in-one/` 项目
- 旧项目添加 **DEPRECATED** 标记指向新项目
- GitHub仓库保留，但README指向新整合项目

---

## 整合优势

1. **单一入口** - 所有资料在一个项目内
2. **统一结构** - 清晰的分类编号
3. **避免重复** - 消除文档冗余
4. **便于维护** - 一次更新，全项目同步

---

*整合日期: 2026-03-22*
