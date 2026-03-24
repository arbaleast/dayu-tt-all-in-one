# GitHub Actions 工作流说明

## 自动同步工作流 (auto-sync.yml)

### 触发条件

1. **代码推送** - 推送到 master/main 分支时
2. **Pull Request** - 创建PR时
3. **定时任务** - 每天凌晨3点自动检查
4. **手动触发** - 在Actions页面手动运行

### 功能

- ✅ 自动检测本地变更
- ✅ 自动提交并推送
- ✅ 同步远程更新
- ✅ 生成同步报告
- ✅ 发送状态通知

### 使用方法

#### 方式1: 自动触发
正常推送代码即可自动触发：
```bash
git push origin master
```

#### 方式2: 手动触发
1. 打开 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择 "Auto Sync and Deploy"
4. 点击 "Run workflow"
5. 选择同步类型：
   - `auto` - 自动模式
   - `force` - 强制同步
   - `dry-run` - 试运行（不实际推送）

### 同步报告

每次同步后会在日志中生成报告：
- 同步时间
- 当前分支
- 最新提交
- 变更状态
- 最近提交历史

## Issue 管理工作流 (issue-manager.yml)

### 功能

自动为 Issue 添加标签：

| 关键词 | 自动标签 |
|-------|---------|
| bug, 错误, 问题 | `bug` |
| feature, 建议, 新增 | `enhancement` |
| doc, 文档 | `documentation` |
| stl, 模型 | `3d-model` |
| question, 疑问, 怎么 | `question` |

### 示例

创建 Issue 时标题包含 "Bug"：
```
[Bug] 皮带张紧器安装不上
```

自动添加 `bug` 标签。

## Issue 模板

### 可用模板

1. **Bug 报告** - 报告问题或错误
2. **功能建议** - 提出新功能或改进
3. **分享你的作品** - 展示封箱成果
4. **资源分享** - 分享STL文件或其他资源

### 使用方法

创建 Issue 时点击 "Get started" 选择对应模板。

## 查看工作流状态

### 方法1: GitHub网页
1. 打开仓库页面
2. 点击 "Actions" 标签
3. 查看工作流运行历史

### 方法2: 状态徽章
在 README.md 中添加：
```markdown
![Auto Sync](https://github.com/arbaleast/dayu-tt-enclosure/workflows/Auto%20Sync%20and%20Deploy/badge.svg)
```

## 故障排除

### 工作流运行失败

1. 查看详细日志
   - Actions 页面 → 点击失败的运行 → 查看日志

2. 常见问题
   - **权限错误**: 检查 `GITHUB_TOKEN` 权限
   - **网络错误**: 重新运行工作流
   - **冲突错误**: 手动解决冲突后推送

### 重新运行工作流

1. 进入 Actions 页面
2. 找到失败的运行
3. 点击右上角 "Re-run jobs"

## 自定义配置

### 修改定时任务

编辑 `.github/workflows/auto-sync.yml`：
```yaml
schedule:
  # 每天凌晨3点
  - cron: '0 3 * * *'
  # 每周一早上8点
  - cron: '0 8 * * 1'
```

Cron 格式说明：
- `分 时 日 月 星期`
- `*` 表示任意
- 例如：`0 3 * * *` 表示每天3:00

### 添加新的工作流

在 `.github/workflows/` 目录创建新的 `.yml` 文件。

## 安全说明

- 工作流使用 `GITHUB_TOKEN` 自动认证
- 不要在工作流中硬编码敏感信息
- 使用 GitHub Secrets 存储密钥

## 参考链接

- [GitHub Actions 文档](https://docs.github.com/cn/actions)
- [工作流语法](https://docs.github.com/cn/actions/using-workflows/workflow-syntax-for-github-actions)
- [Issue 模板](https://docs.github.com/cn/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
