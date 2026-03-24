# SSH 访问 GitHub 配置指南

## 当前状态

✅ **SSH密钥已存在**: `~/.ssh/id_rsa.pub`

## 配置步骤

### 步骤1: 复制SSH公钥

你的SSH公钥内容：

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDaA+5YOkaiTHXkiy0D/DIha6uzGazyaTBLle7Rlvwf+Hg3rp0byluWMMl1KFNzP7cUAJAAQyakmGKEwunRBpXjEH3S3vQVimmkJh4dS9ZHqYa98fVIJo7q1KRzeFfQvL1qU3GgKYTC42gaEOFyRbXzBXGdWffuHsQCsafgj75C2dsj978tmrpNIqRHaHW6VVMTC9/4IQYHmfdYfeny2feO9BOR0++WdSNXJjy6VzDaxqyLi420lDV4ZFkdBhcnU30E27CrVxUWl/gPhXfvnzPCXz3rRBoRihXuas2flhCDYXYGcb0DGOIX6W5tx4aTgPd1R15n90hhXSxR2PS3SlIBaa1q4KcXrCHcPsnu6Q4bRhN3DOdUBfQ2klYaDJx8+sw+HJ1XugdROeDoG7PM2eWxkok/VsHTwvaLE7UNfVIb6b83YpN9L28hGkMZjmPi/j+TwGlV/kn6obrwxOJqf+bjqL5r+ZWtfgxvq8Ks/XVMlnZkGZ+LaCntLvSU2Z7LYwM= arbaleast@pc
```

### 步骤2: 添加到GitHub账户

**方法A: 通过网页界面**

1. 打开 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 填写信息：
   - **Title**: `OpenClaw-PC` (或任意名称)
   - **Key type**: Authentication Key
   - **Key**: 粘贴上面的公钥内容
4. 点击 "Add SSH key"

**方法B: 通过命令行** (需要重新授权)

```bash
gh auth refresh -h github.com -s admin:public_key
gh ssh-key add ~/.ssh/id_rsa.pub --title "OpenClaw-PC"
```

### 步骤3: 测试SSH连接

```bash
ssh -T git@github.com
```

预期输出：
```
Hi arbaleast! You've successfully authenticated, but GitHub does not provide shell access.
```

### 步骤4: 验证项目配置

项目已配置为SSH访问：

```bash
cd /home/arbaleast/.openclaw/workspace/projects/dayu-tt-enclosure
git remote -v
```

应该显示：
```
origin	git@github.com:arbaleast/dayu-tt-enclosure.git (fetch)
origin	git@github.com:arbaleast/dayu-tt-enclosure.git (push)
```

## 使用方法

### 同步到GitHub

配置完成后，使用以下命令同步：

```bash
# 进入项目目录
cd /home/arbaleast/.openclaw/workspace/projects/dayu-tt-enclosure

# 使用同步脚本
./sync.sh "更新说明"

# 或手动同步
git add -A
git commit -m "更新说明"
git push origin master
```

**特点**: 无需输入密码，自动使用SSH密钥认证

## 故障排除

### 问题1: Permission denied (publickey)

**原因**: SSH密钥未添加到GitHub

**解决**: 按照步骤2添加公钥

### 问题2: Could not resolve hostname

**原因**: 网络问题或SSH配置错误

**解决**:
```bash
# 测试网络
ping github.com

# 检查SSH配置
cat ~/.ssh/config
```

### 问题3: 需要输入密码

**原因**: 使用了HTTPS而不是SSH

**解决**:
```bash
# 检查当前remote
git remote -v

# 如果是https，切换到ssh
git remote set-url origin git@github.com:arbaleast/dayu-tt-enclosure.git
```

## SSH配置优化

### 创建SSH配置文件

编辑 `~/.ssh/config`:

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
EOF

chmod 600 ~/.ssh/config
```

### 使用SSH代理（可选）

避免每次输入密钥密码（如果设置了密码）：

```bash
# 启动ssh-agent
eval "$(ssh-agent -s)"

# 添加密钥
ssh-add ~/.ssh/id_rsa
```

## 安全建议

1. **保护私钥**: 不要分享 `~/.ssh/id_rsa` 文件
2. **定期更换**: 建议每年更换一次SSH密钥
3. **多设备管理**: 为不同设备添加不同的SSH密钥
4. **撤销密钥**: 如果设备丢失，及时在GitHub撤销对应密钥

## 验证配置

运行以下命令验证所有配置：

```bash
echo "=== SSH密钥 ==="
ls -la ~/.ssh/

echo "=== SSH配置 ==="
cat ~/.ssh/config 2>/dev/null || echo "无配置文件"

echo "=== Git Remote ==="
git remote -v

echo "=== 连接测试 ==="
ssh -T git@github.com 2>&1 || echo "连接失败，请添加SSH密钥到GitHub"
```

---

**下一步操作**: 请打开 https://github.com/settings/keys 添加你的SSH公钥
