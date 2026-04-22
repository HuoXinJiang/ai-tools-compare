#!/bin/bash
# AI-Tools-Compare 一键部署脚本

set -e

echo "🚀 开始部署 AI-Tools-Compare..."

# 检查 gh 是否已安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安装"
    echo "请先安装：brew install gh"
    echo "然后登录：gh auth login"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "⚠️  未登录 GitHub"
    echo "请先运行：gh auth login"
    exit 1
fi

cd "$(dirname "$0")"

echo "📦 创建 GitHub 仓库..."
gh repo create ai-tools-compare     --public     --description "AI Code Editor Comparison 2026 - Features, Pricing, and Reviews"     --source .     --push     --default-branch main     --allow-empty 2>/dev/null || echo "仓库已存在，跳过创建"

echo "
✅ 仓库已创建并推送！"

# 获取仓库信息
REPO_URL=$(gh repo view --json url -q url 2>/dev/null || echo "")

if [ -n "$REPO_URL" ]; then
    echo "
📊 仓库信息:"
    echo "   URL: $REPO_URL"
    echo "
🎉 下一步:"
    echo "1. 访问仓库设置页面"
    echo "2. 进入 Settings > Pages"
    echo "3. 启用 GitHub Pages (Source: main branch, / (root directory))"
    echo "4. 等待约 1-2 分钟后访问：https://algea.github.io/ai-tools-compare/"
fi

echo "
✨ 部署完成！"
