#!/usr/bin/env python3
"""
GitHub 仓库健康度分析器
分析仓库的活跃度、贡献者情况、代码增长趋势

Author: AI Code Journey
Date: 2026-02-04
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict


class RepoHealthAnalyzer:
    """GitHub 仓库健康度分析器"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repo_info(self) -> dict:
        """获取仓库基本信息"""
        response = requests.get(self.base_url, headers=self.headers)
        return response.json()
    
    def get_commits(self, since: datetime = None) -> list:
        """获取提交历史"""
        params = {"per_page": 100}
        if since:
            params["since"] = since.isoformat()
        
        all_commits = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(
                f"{self.base_url}/commits",
                headers=self.headers,
                params=params
            )
            commits = response.json()
            
            if not commits:
                break
            
            all_commits.extend(commits)
            page += 1
            
            if len(commits) < 100:
                break
        
        return all_commits
    
    def get_contributors(self) -> list:
        """获取贡献者列表"""
        response = requests.get(
            f"{self.base_url}/contributors",
            headers=self.headers,
            params={"per_page": 100}
        )
        return response.json()
    
    def analyze_commit_patterns(self, commits: list) -> dict:
        """分析提交模式"""
        if not commits:
            return {}
        
        # 按星期统计
        weekday_counts = defaultdict(int)
        # 按小时统计
        hourly_counts = defaultdict(int)
        
        for commit in commits:
            date_str = commit["commit"]["committer"]["date"]
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            weekday_counts[dt.weekday()] += 1
            hourly_counts[dt.hour] += 1
        
        return {
            "weekday_distribution": dict(weekday_counts),
            "hourly_distribution": dict(hourly_counts),
            "total_commits": len(commits)
        }
    
    def calculate_health_score(self, info: dict, commit_patterns: dict) -> dict:
        """计算仓库健康度评分"""
        score = 100
        
        # 检查仓库年龄
        created_at = datetime.fromisoformat(
            info["created_at"].replace("Z", "+00:00")
        )
        age_days = (datetime.now() - created_at).days
        
        if age_days > 365:
            score -= 10  # 老仓库但提交不活跃
        
        # 检查最近提交
        if commit_patterns.get("total_commits", 0) > 0:
            recent_commits = sum(1 for c in commit_patterns["weekday_distribution"].values())
            if recent_commits < 10:
                score -= 20
        else:
            score -= 50  # 没有提交
        
        # 检查是否有多个贡献者
        score += min(20, len(commit_patterns.get("weekday_distribution", {})) * 2)
        
        return {
            "overall_score": max(0, min(100, score)),
            "age_days": age_days,
            "is_active": score > 60
        }
    
    def generate_report(self) -> str:
        """生成健康度报告"""
        print("🔍 分析仓库健康度...")
        
        # 获取数据
        info = self.get_repo_info()
        commits = self.get_commits(since=datetime.now() - timedelta(days=30))
        contributors = self.get_contributors()
        patterns = self.analyze_commit_patterns(commits)
        health = self.calculate_health_score(info, patterns)
        
        # 生成报告
        report = f"""
# 📊 仓库健康度报告

## 基本信息
- **仓库名称**: {info.get('full_name', 'N/A')}
- **描述**: {info.get('description', '无描述')}
- **创建时间**: {info.get('created_at', 'N/A')[:10]}
- **星标数**: ⭐ {info.get('stargazers_count', 0)}
- **分支数**: {info.get('forks_count', 0)}
- **开放Issue数**: {info.get('open_issues_count', 0)}

## 提交活动（最近30天）
- **总提交数**: {patterns.get('total_commits', 0)}
- **星期分布**: {patterns.get('weekday_distribution', {})}
- **时间分布**: {patterns.get('hourly_distribution', {})}

## 贡献者
- **贡献者数量**: {len(contributors) if isinstance(contributors, list) else 'N/A'}

## 健康度评估
- **综合评分**: {health['overall_score']}/100
- **仓库年龄**: {health['age_days']} 天
- **活跃状态**: {'✅ 活跃' if health['is_active'] else '⚠️ 需要关注'}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return report


def main():
    """主函数"""
    # 配置
    import os

# 从环境变量获取token，避免硬编码
TOKEN = os.environ.get("GITHUB_TOKEN", "your_token_here")
    OWNER = "my1162709474"
    REPO = "MarsAssistant-Code-Journey"
    
    # 分析并生成报告
    analyzer = RepoHealthAnalyzer(TOKEN, OWNER, REPO)
    report = analyzer.generate_report()
    
    # 打印报告
    print(report)
    
    # 保存报告
    with open("repo_health_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n✅ 报告已保存到 repo_health_report.md")


if __name__ == "__main__":
    main()
