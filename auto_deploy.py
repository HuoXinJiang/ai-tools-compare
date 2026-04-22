#!/usr/bin/env python3
"""AI-Tools-Compare 纯标准库部署脚本 - 无需额外依赖"""

import os
import subprocess
import sys
import urllib.request
import urllib.error
import json
from datetime import datetime


def load_token():
    """从 ~/.netrc 读取 GitHub token"""
    netrc_path = os.path.expanduser("~/.netrc")
    
    if os.path.exists(netrc_path):
        try:
            with open(netrc_path, "r") as f:
                content = f.read()
                for line in content.split("\n"):
                    if line.strip().startswith("password"):
                        token = line.strip().split()[1]
                        print(f"✅ 从 ~/.netrc 读取到 Token")
                        return token
        except Exception as e:
            print(f"❌ 读取 ~/.netrc 失败：{e}")
    
    # 检查环境变量
    for var in ["GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"]:
        token = os.environ.get(var)
        if token:
            print(f"✅ 从环境变量 {var} 读取到 Token")
            return token
    
    return None


def http_request(method, url, headers=None, data=None, params=None):
    """HTTP 请求工具函数"""
    
    # 添加查询参数
    if params:
        if "?" in url:
            url += "&" + urllib.parse.urlencode(params)
        else:
            url += "?" + urllib.parse.urlencode(params)
    
    # 构建请求
    req = urllib.request.Request(url)
    
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    
    if data:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    
    # 发送请求
    try:
        response = urllib.request.urlopen(req, timeout=30)
        return response.getcode(), response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 500, str(e)


def github_deploy():
    project_dir = "/Users/algea/workspace/AI-Tools-Compare"
    repo_name = "ai-tools-compare"
    
    print("\n🚀 AI-Tools-Compare 自动化部署脚本")
    print("=" * 50)
    
    # 读取 Token
    token = load_token()
    
    if not token:
        print("\n⚠️  未找到 GitHub Token")
        print("\n  请按以下步骤获取 Token:")
        print("  1. 访问：https://github.com/settings/tokens")
        print("  2. 点击 'Generate new token' -> 'Generate new token (classic)'")
        print("  3. 设置过期时间")
        print("  4. 选择权限：repo (全部勾选)")
        print("  5. 复制生成的 Token")
        print("\n  然后将 Token 复制到以下命令：")
        print("  echo 'machine github.com login oauth2 password YOUR_TOKEN' > ~/.netrc")
        print("\n  然后重新运行此脚本")
        return False
    
    # 设置 Git 配置
    subprocess.run(["git", "config", "--global", "user.email", "deploy@algea.local"], cwd=project_dir)
    subprocess.run(["git", "config", "--global", "user.name", "AI Deploy Bot"], cwd=project_dir)
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 创建或获取仓库
    print("\n📦 创建 GitHub 仓库...")
    
    # 检查仓库是否已存在
    status, response_body = http_request("GET", "https://api.github.com/user/repos", headers=headers, params={"per_page": 100})
    
    repo_exists = False
    if status == 200:
        repos = json.loads(response_body)
        for repo in repos:
            if repo["name"] == repo_name:
                print(f"✅ 仓库已存在，将更新内容")
                repo_exists = True
                break
    
    if not repo_exists:
        # 创建新仓库
        status, response_body = http_request(
            "POST",
            "https://api.github.com/user/repos",
            headers=headers,
            data={
                "name": repo_name,
                "description": "AI Code Editor Comparison 2026 - Features, Pricing, and Reviews",
                "private": False,
                "auto_init": False
            }
        )
        
        if status == 201:
            repo_data = json.loads(response_body)
            print(f"✅ 创建新仓库成功！")
            print(f"   URL: {repo_data.get('html_url', '')}")
        else:
            print(f"❌ 创建仓库失败：{status}")
            print(response_body)
            return False
    
    # 获取仓库 URL
    clone_url = f"https://oauth2:{token}@github.com/algea/{repo_name}.git"
    
    # 设置远程仓库
    subprocess.run(["git", "remote", "remove", "origin"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", clone_url], cwd=project_dir)
    subprocess.run(["git", "add", "."], cwd=project_dir)
    subprocess.run(["git", "commit", "-m", f"Deploy site - {datetime.now().strftime('%Y-%m-%d %H:%M')}"], cwd=project_dir)
    subprocess.run(["git", "branch", "-M", "main"], cwd=project_dir)
    
    print("\n📤 推送到 GitHub...")
    result = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 推送成功！")
        print(f"\n🎉 部署完成！")
        print(f"\n📊 下一步:")
        print(f"   1. 访问仓库：https://github.com/algea/{repo_name}")
        print(f"   2. 进入 Settings > Pages")
        print(f"   3. 选择 Source: main branch")
        print(f"   4. 点击 Save")
        print(f"\n   等待 1-2 分钟后访问：https://algea.github.io/{repo_name}/")
        print(f"\n📚 内容:")
        print(f"   - 25 个 AI 工具对比页面")
        print(f"   - 价格对比、功能对比、免费工具推荐")
        print(f"   - 完整的 SEO 优化")
        
        # 启用 GitHub Pages
        print("\n🔧 自动启用 GitHub Pages...")
        status, response_body = http_request(
            "PUT",
            "https://api.github.com/repos/algea/ai-tools-compare/pages",
            headers=headers,
            data={
                "source": {"branch": "main", "path": "/"}
            }
        )
        
        if status in [200, 201]:
            print("✅ GitHub Pages 已启用！")
            print(f"\n🌐 你的网站即将上线：")
            print(f"   https://algea.github.io/ai-tools-compare/")
            print(f"\n   （可能需要 1-2 分钟才能访问）")
        else:
            print("⚠️  需要手动启用 GitHub Pages（见上面步骤）")
        
        return True
    else:
        print(f"❌ 推送失败")
        print(result.stderr)
        return False


if __name__ == "__main__":
    try:
        github_deploy()
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
