#!/usr/bin/env python3
"""
GitHub Repository Contributor Stats
GitHub仓库贡献者统计分析工具

功能:
- 分析仓库贡献者的提交活动
- 计算贡献者排名
- 生成贡献热力图
- 统计提交时间分布
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import os


class GitHubContributorStats:
    """GitHub贡献者统计分析器"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_contributors(self) -> List[Dict]:
        """获取仓库贡献者列表"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contributors"
        params = {
            "per_page": 100,
            "anon": "true"
        }
        
        contributors = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching contributors: {response.status_code}")
                break
            
            data = response.json()
            if not data:
                break
            
            contributors.extend(data)
            page += 1
            
            # 防止请求过快
            import time
            time.sleep(0.5)
        
        return contributors
    
    def get_user_contributions(self, username: str, since: Optional[datetime] = None) -> Dict:
        """获取特定用户的贡献统计"""
        url = f"{self.base_url}/users/{username}/events/public"
        params = {"per_page": 100}
        
        if since:
            params["since"] = since.isoformat()
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            return {}
        
        events = response.json()
        
        # 统计事件类型
        event_counts = defaultdict(int)
        repo_events = 0
        
        for event in events:
            if event.get("repo", {}).get("name", "").startswith(f"{self.owner}/{self.repo}"):
                repo_events += 1
                event_counts[event["type"]] += 1
        
        return {
            "username": username,
            "total_events": len(events),
            "repo_events": repo_events,
            "event_breakdown": dict(event_counts)
        }
    
    def get_commit_activity_weekly(self) -> List[Dict]:
        """获取每周提交活动"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/stats/commit_activity"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return []
        
        return response.json()
    
    def get_participation_stats(self) -> Dict:
        """获取参与度统计"""
        contributors = self.get_contributors()
        weekly_activity = self.get_commit_activity_weekly()
        
        # 计算总贡献者
        total_contributors = len(contributors)
        
        # 计算平均提交
        if contributors:
            avg_contributions = sum(c.get("contributions", 0) for c in contributors) / total_contributors
            top_contributors = sorted(contributors, key=lambda x: x.get("contributions", 0), reverse=True)[:5]
        else:
            avg_contributions = 0
            top_contributors = []
        
        # 解析每周活动
        days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for week in weekly_activity[-4:]:  # 最近4周
            for day_idx, day_data in enumerate(week.get("days", [])):
                daily_distribution[days_of_week[day_idx]] += day_data
                for hour, count in enumerate(week.get("hours", [])):
                    if isinstance(count, list):
                        for h in count:
                            hourly_distribution[h] += day_data
                    else:
                        hourly_distribution[hour] += count
        
        return {
            "total_contributors": total_contributors,
            "average_contributions": avg_contributions,
            "top_contributors": [
                {
                    "login": c.get("login"),
                    "contributions": c.get("contributions"),
                    "avatar_url": c.get("avatar_url"),
                    "html_url": c.get("html_url")
                }
                for c in top_contributors
            ],
            "daily_distribution": dict(daily_distribution),
            "weekly_activity": weekly_activity[-1] if weekly_activity else {}
        }
    
    def generate_report(self) -> str:
        """生成Markdown格式的报告"""
        stats = self.get_participation_stats()
        
        report = f"""# GitHub仓库贡献者统计报告

## 仓库信息
- **Owner**: {self.owner}
- **仓库**: {self.repo}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计
- **总贡献者**: {stats['total_contributors']}
- **平均贡献数**: {stats['average_contributions']:.1f}

## Top 5 贡献者
| 排名 | 用户名 | 贡献数 | 头像 |
|------|--------|--------|------|
"""
        
        for i, contributor in enumerate(stats['top_contributors'], 1):
            report += f"| {i} | [{contributor['login']}]({contributor['html_url']}) | {contributor['contributions']} | ![avatar]({contributor['avatar_url']}) |\n"
        
        report += """
## 每日提交分布

"""
        for day, count in stats['daily_distribution'].items():
            bar = "█" * min(count // 10, 50) if count > 0 else "░"
            report += f"- **{day}**: {bar} ({count})\n"
        
        report += """
---

*由 GitHub Contributor Stats 工具自动生成*
"""
        
        return report
    
    def print_summary(self):
        """打印简洁摘要"""
        stats = self.get_participation_stats()
        
        print(f"\n{'='*60}")
        print(f"📊 GitHub仓库贡献者统计")
        print(f"📁 仓库: {self.owner}/{self.repo}")
        print(f"{'='*60}")
        print(f"👥 总贡献者: {stats['total_contributors']}")
        print(f"📈 平均贡献: {stats['average_contributions']:.1f}")
        
        print(f"\n🏆 Top 贡献者:")
        for i, c in enumerate(stats['top_contributors'], 1):
            print(f"  {i}. {c['login']} - {c['contributions']} 次提交")
        
        print(f"\n📅 每日活跃度:")
        for day, count in stats['daily_distribution'].items():
            print(f"  {day:10s}: {count:5d} commits")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitHub Repository Contributor Stats Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python github_contributor_stats.py -o my1162709474 -r MarsAssistant-Code-Journey
  python github_contributor_stats.py -o my1162709474 -r MarsAssistant-Code-Journey --export report.md
        """
    )
    
    parser.add_argument('-o', '--owner', required=True, help='仓库所有者用户名')
    parser.add_argument('-r', '--repo', required=True, help='仓库名称')
    parser.add_argument('-t', '--token', 
                       default=os.environ.get('GITHUB_TOKEN', ''),
                       help='GitHub Personal Access Token (可设置GITHUB_TOKEN环境变量)')
    parser.add_argument('--export', '-e', help='导出报告到文件')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--token-env', action='store_true', 
                       help='提示用户设置GITHUB_TOKEN环境变量')
    
    args = parser.parse_args()
    
    if args.token_env:
        print("请设置 GitHub Token 环境变量:")
        print("  export GITHUB_TOKEN=your_token_here")
        print("\n获取Token: https://github.com/settings/tokens")
        return
    
    if not args.token:
        print("❌ 需要 GitHub Personal Access Token")
        print("使用 --token 参数或设置 GITHUB_TOKEN 环境变量")
        print("\n获取Token: https://github.com/settings/tokens")
        return
    
    analyzer = GitHubContributorStats(args.token, args.owner, args.repo)
    
    if args.json:
        stats = analyzer.get_participation_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        analyzer.print_summary()
        
        report = analyzer.generate_report()
        
        if args.export:
            with open(args.export, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 报告已导出到: {args.export}")
        else:
            print(f"\n{report}")


if __name__ == '__main__':
    main()
