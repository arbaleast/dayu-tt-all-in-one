# SSH 访问配置完成指南

## 当前状态

✅ **项目已同步到GitHub**: https://github.com/arbaleast/dayu-tt-enclosure

✅ **SSH密钥已生成**: `~/.ssh/id_rsa.pub`

⏳ **待完成**: 将SSH公钥添加到GitHub账户

## 快速配置步骤

### 1. 查看你的SSH公钥

```bash
cat ~/.ssh/id_rsa.pub
```

输出示例：
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDaA+5YOkaiTHXkiy0D... arbaleast@pc
```

### 2. 添加到GitHub（二选一）

#### 方法A: 网页操作（推荐）

1. **复制公钥内容**
   ```bash
   cat ~/.ssh/id_rsa.pub | xclip -selection clipboard  # Linux
   # 或手动复制
   ```

2. **打开GitHub设置**
   - 访问: https://github.com/settings/keys
   - 或点击右上角头像 → Settings → SSH and GPG keys

3. **添加新密钥**
   - 点击绿色按钮 "New SSH key"
   - Title: 输入 `OpenClaw-PC`（或任意名称）
   - Key: 粘贴刚才复制的公钥
   - 点击 "Add SSH key"

#### 方法B: 使用脚本

```bash
./setup-ssh.sh
```

按照提示操作即可。

### 3. 测试SSH连接

```bash
ssh -T git@github.com
```

**成功提示**：
```
Hi arbaleast! You've successfully authenticated, but GitHub does not provide shell access.
```

### 4. 切换到SSH方式

```bash
# 进入项目目录
cd /home/arbaleast/.openclaw/workspace/projects/dayu-tt-enclosure

# 切换到SSH remote
git remote set-url origin git@github.com:arbaleast/dayu-tt-enclosure.git

# 验证
git remote -v
# 应该显示: git@github.com:arbaleast/dayu-tt-enclosure.git
```

### 5. 测试推送

```bash
./sync.sh "测试SSH连接"
```

如果不需要输入密码就推送成功，说明配置完成！

## 配置对比

| 方式 | 优点 | 缺点 | 适用场景 |
|-----|------|------|---------|
| **HTTPS + Token** | 配置简单 | Token可能过期 | 临时使用 |
| **SSH** | 安全、免密 | 需要初始配置 | 长期使用 ✅ |

## 配置完成后的使用

### 日常同步

```bash
# 快速同步（推荐）
./sync.sh "更新说明"

# 手动同步
git add -A
git commit -m "更新说明"
git push origin master
```

**特点**: 无需输入任何密码，自动认证

### 其他GitHub操作

```bash
# 拉取更新
git pull origin master

# 查看状态
git status

# 查看日志
git log --oneline -5
```

## 故障排除

### 问题: Permission denied (publickey)

**原因**: 公钥未添加到GitHub

**解决**: 按照上面的步骤2添加

### 问题: Could not resolve hostname github.com

**原因**: 网络问题

**解决**:
```bash
# 测试网络连接
ping github.com

# 检查DNS
nslookup github.com
```

### 问题: 每次都要输入密码

**原因**: 使用了HTTPS而不是SSH

**解决**:
```bash
# 检查当前方式
git remote -v

# 如果是https://开头，切换到SSH
git remote set-url origin git@github.com:arbaleast/dayu-tt-enclosure.git
```

## 安全提示

1. **私钥保护**: `~/.ssh/id_rsa` 文件不要分享给任何人
2. **公钥安全**: `~/.ssh/id_rsa.pub` 可以安全分享
3. **定期更换**: 建议每年更换一次SSH密钥
4. **多设备**: 每个设备使用不同的SSH密钥

## 相关文件

- `SSH_SETUP.md` - 详细配置说明
- `setup-ssh.sh` - 自动配置脚本
- `sync.sh` - 同步脚本（配置完成后使用）

## 下一步

配置完成后，你就可以：
1. ✅ 免密码推送代码到GitHub
2. ✅ 使用 `./sync.sh` 快速同步
3. ✅ 安全地管理你的项目

---

**请现在访问 https://github.com/settings/keys 添加你的SSH公钥**

添加完成后，运行 `./setup-ssh.sh` 验证配置
