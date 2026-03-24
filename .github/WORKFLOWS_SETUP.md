# GitHub Actions 配置指南

## 当前状态

✅ **Issue模板** - 已配置  
✅ **文档** - 已完善  
⏳ **工作流** - 需要手动添加到GitHub

## 已配置的Issue模板

### 模板列表

1. **Bug 报告** (`bug_report.md`)
   - 问题描述
   - 复现步骤
   - 环境信息
   - 附件上传

2. **功能建议** (`feature_request.md`)
   - 功能描述
   - 使用场景
   - 预期效果
   - 实现方案

3. **分享你的作品** (`showcase.md`)
   - 作品展示
   - 使用方案
   - 成本统计
   - 经验分享

4. **资源分享** (`resource_share.md`)
   - 资源类型
   - 来源说明
   - 文件清单
   - 使用说明

### 使用方法

用户创建Issue时，GitHub会显示模板选择界面。

## 工作流配置（待添加）

由于OAuth权限限制，需要手动添加工作流。

### 步骤1: 在GitHub网页创建

1. 打开仓库: https://github.com/arbaleast/dayu-tt-enclosure
2. 点击 "Actions" 标签
3. 点击 "set up a workflow yourself"
4. 复制下面的配置

### 步骤2: 创建工作流文件

文件名: `.github/workflows/auto-sync.yml`

```yaml
name: Auto Sync

on:
  push:
    branches: [ master, main ]
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Git
      run: |
        git config user.name 'GitHub Actions'
        git config user.email 'actions@github.com'
    
    - name: Check changes
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          git add -A
          git commit -m "Auto sync: $(date +'%Y-%m-%d %H:%M:%S')"
          git push
        fi
```

### 步骤3: 提交工作流

点击 "Start commit" → "Commit new file"

## 本地工作流文件

工作流文件已保存在本地：
- `.github/workflows/auto-sync.yml` (需要手动上传)
- `.github/workflows/issue-manager.yml` (需要手动上传)

## 查看效果

配置完成后：
1. 打开 Actions 标签查看工作流运行状态
2. 创建 Issue 测试模板效果
3. 查看自动标签是否正确添加

## 参考

- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [Issue 模板文档](https://docs.github.com/cn/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
