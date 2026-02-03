#!/usr/bin/env python3
"""
GitHub自动化管理工具
GitHub Repository Management Tool

功能:
- 列出仓库文件
- 下载文件内容
- 创建/更新文件
- 提交代码
- 管理README

Author: MarsAssistant-Code-Journey
Date: 2026-02-03
"""

import os
import base64
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any


class GitHubManager:
    """GitHub仓库管理工具"""
    
    def __init__(self, token: str, owner: str, repo: str):
        """
        初始化GitHub管理器
        
        Args:
            token: GitHub Personal Access Token
            owner: 仓库所有者用户名
            repo: 仓库名称
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        发送API请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/{endpoint}"
        
        if data:
            response = requests.request(method, url, headers=self.headers, json=data)
        else:
            response = requests.request(method, url, headers=self.headers)
        
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def get_repository_info(self) -> Dict[str, Any]:
        """获取仓库信息"""
        return self._request("GET", f"repos/{self.owner}/{self.repo}")
    
    def list_files(self, path: str = "") -> List[Dict[str, Any]]:
        """
        列出仓库中的文件
        
        Args:
            path: 目录路径（空字符串表示根目录）
            
        Returns:
            文件列表
        """
        endpoint = f"repos/{self.owner}/{self.repo}/contents/{path}"
        return self._request("GET", endpoint)
    
    def get_file_content(self, path: str) -> str:
        """
        获取文件内容
        
        Args:
            path: 文件路径
            
        Returns:
            文件内容的Base64解码字符串
        """
        data = self._request("GET", f"repos/{self.owner}/{self.repo}/contents/{path}")
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8")
        return data.get("content", "")
    
    def create_or_update_file(
        self,
        path: str,
        content: str,
        message: str,
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建或更新文件
        
        Args:
            path: 文件路径
            content: 文件内容
            message: 提交信息
            sha: 文件SHA（更新时需要）
            
        Returns:
            API响应数据
        """
        endpoint = f"repos/{self.owner}/{self.repo}/contents/{path}"
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
        }
        
        if sha:
            data["sha"] = sha
        
        return self._request("PUT", endpoint, data)
    
    def delete_file(self, path: str, message: str, sha: str) -> Dict[str, Any]:
        """
        删除文件
        
        Args:
            path: 文件路径
            message: 提交信息
            sha: 文件SHA
            
        Returns:
            API响应数据
        """
        return self._request(
            "DELETE",
            f"repos/{self.owner}/{self.repo}/contents/{path}",
            {"message": message, "sha": sha}
        )
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
        """
        创建新分支
        
        Args:
            branch_name: 分支名称
            base_branch: 基础分支名称
            
        Returns:
            API响应数据
        """
        # 获取基础分支的SHA
        ref_data = self._request("GET", f"repos/{self.owner}/{self.repo}/git/refs/heads/{base_branch}")
        base_sha = ref_data["object"]["sha"]
        
        # 创建新分支
        return self._request(
            "POST",
            f"repos/{self.owner}/{self.repo}/git/refs",
            {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
            }
        )
    
    def get_commits(self, branch: str = "main", per_page: int = 10) -> List[Dict]:
        """
        获取提交历史
        
        Args:
            branch: 分支名称
            per_page: 每页数量
            
        Returns:
            提交列表
        """
        params = {"sha": branch, "per_page": per_page}
        endpoint = f"repos/{self.owner}/{self.repo}/commits"
        return self._request("GET", f"{endpoint}?sha={branch}&per_page={per_page}")
    
    def search_code(self, query: str) -> Dict[str, Any]:
        """
        搜索代码
        
        Args:
            query: 搜索关键词
            
        Returns:
            搜索结果
        """
        return self._request(
            "GET",
            f"search/code?q={query}+repo:{self.owner}/{self.repo}"
        )


def main():
    """主函数 - 演示使用"""
    
    # 配置（请替换为你的token）
    TOKEN = os.environ.get("GITHUB_TOKEN", "")
    OWNER = "my1162709474"
    REPO = "MarsAssistant-Code-Journey"
    
    if not TOKEN:
        print("❌ 请设置环境变量 GITHUB_TOKEN")
        return
    
    # 创建管理器实例
    github = GitHubManager(TOKEN, OWNER, REPO)
    
    # 示例：列出根目录文件
    print("📁 仓库文件列表:")
    files = github.list_files()
    for f in files:
        print(f"  - {f['name']} ({f['type']})")
    
    # 示例：获取仓库信息
    print("\n📊 仓库信息:")
    info = github.get_repository_info()
    print(f"  名称: {info['full_name']}")
    print(f"  描述: {info['description']}")
    print(f"  Stars: {info['stargazers_count']}")
    print(f"  Forks: {info['forks_count']}")


if __name__ == "__main__":
    main()
