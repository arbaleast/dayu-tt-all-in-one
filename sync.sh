#!/bin/bash

# 大鱼TT封箱项目自动同步脚本
# 用法: ./sync.sh [commit message]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 大鱼TT封箱项目 - GitHub同步脚本 ===${NC}"
echo ""

# 检查是否在git仓库中
if [ ! -d .git ]; then
    echo -e "${RED}错误: 当前目录不是git仓库${NC}"
    exit 1
fi

# 获取当前分支
BRANCH=$(git branch --show-current)
echo -e "当前分支: ${YELLOW}$BRANCH${NC}"

# 检查远程仓库
if ! git remote -v > /dev/null 2>&1; then
    echo -e "${RED}错误: 没有配置远程仓库${NC}"
    echo "请运行: gh repo create 或手动添加remote"
    exit 1
fi

echo -e "远程仓库: ${YELLOW}$(git remote get-url origin)${NC}"
echo ""

# 检查状态
echo -e "${GREEN}>>> 检查文件状态...${NC}"
git status --short

# 检查是否有变更
if [ -z "$(git status --short)" ]; then
    echo -e "${YELLOW}没有需要提交的变更${NC}"
    echo -e "${GREEN}>>> 拉取远程更新...${NC}"
    git pull origin $BRANCH
    echo -e "${GREEN}同步完成！${NC}"
    exit 0
fi

echo ""

# 添加所有变更
echo -e "${GREEN}>>> 添加变更到暂存区...${NC}"
git add -A

# 提交信息
if [ -z "$1" ]; then
    COMMIT_MSG="Update: $(date +'%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

echo -e "提交信息: ${YELLOW}$COMMIT_MSG${NC}"

# 提交
git commit -m "$COMMIT_MSG"

# 推送到远程
echo -e "${GREEN}>>> 推送到GitHub...${NC}"
git push origin $BRANCH

echo ""
echo -e "${GREEN}=== 同步完成！ ===${NC}"
echo -e "仓库地址: ${YELLOW}https://github.com/arbaleast/dayu-tt-enclosure${NC}"
echo -e "更新时间: $(date)"
