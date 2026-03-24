#!/bin/bash

# GitHub SSH 快速配置脚本
# 用法: ./setup-ssh.sh

echo "=== GitHub SSH 配置助手 ==="
echo ""

# 检查SSH密钥
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "生成SSH密钥..."
    ssh-keygen -t rsa -b 4096 -C "$(whoami)@$(hostname)" -f ~/.ssh/id_rsa -N ""
fi

echo "你的SSH公钥:"
echo ""
cat ~/.ssh/id_rsa.pub
echo ""
echo "=================================="
echo ""
echo "请复制上面的公钥，然后:"
echo ""
echo "1. 打开 https://github.com/settings/keys"
echo "2. 点击 'New SSH key'"
echo "3. 粘贴公钥内容"
echo "4. 点击 'Add SSH key'"
echo ""
echo "完成后按回车继续..."
read

echo "测试SSH连接..."
ssh -T git@github.com 2>&1

if [ $? -eq 1 ]; then
    echo ""
    echo "✅ SSH配置成功！"
    echo ""
    echo "现在可以使用以下命令同步:"
    echo "  ./sync.sh '更新说明'"
else
    echo ""
    echo "❌ SSH连接失败"
    echo "请确认已添加公钥到GitHub"
fi
