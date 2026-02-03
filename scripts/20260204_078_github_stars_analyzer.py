"""
GitHub Stars Analyzer - GitHub收藏仓库分析工具
分析和管理用户star的GitHub仓库
"""

import requests
import json
from datetime import datetime
from collections import Counter
import os

class GitHubStarsAnalyzer:
    """GitHub Stars分析器"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_stars(self, username, per_page=100):
        """获取用户所有star的仓库"""
        stars = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{username}/starred"
            params = {"per_page": per_page, "page": page}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
            
            repos = response.json()
            if not repos:
                break
            
            stars.extend(repos)
            page += 1
        
        return stars
    
    def analyze_language_distribution(self, stars):
        """分析编程语言分布"""
        languages = [repo.get('language') for repo in stars if repo.get('language')]
        return Counter(languages)
    
    def analyze_topics(self, stars):
        """分析主题分布"""
        all_topics = []
        for repo in stars:
            topics = repo.get('topics', [])
            all_topics.extend(topics)
        return Counter(all_topics)
    
    def find_most_starred(self, stars, top_n=10):
        """找出star最多的仓库"""
        sorted_repos = sorted(stars, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        return sorted_repos[:top_n]
    
    def analyze_update_frequency(self, stars):
        """分析仓库更新频率"""
        recent = 0
        older = 0
        very_old = 0
        
        for repo in stars:
            updated = repo.get('updated_at', '')
            if updated:
                date = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")
                days_ago = (datetime.now() - date).days
                
                if days_ago < 30:
                    recent += 1
                elif days_ago < 365:
                    older += 1
                else:
                    very_old += 1
        
        return {"recent_30d": recent, "older": older, "very_old": very_old}
    
    def generate_report(self, username):
        """生成分析报告"""
        print(f"正在分析 {username} 的GitHub Stars...")
        
        stars = self.get_stars(username)
        print(f"共找到 {len(stars)} 个star的仓库\n")
        
        # 语言分布
        lang_dist = self.analyze_language_distribution(stars)
        print("=== 编程语言分布 ===")
        for lang, count in lang_dist.most_common(10):
            pct = count / len(stars) * 100
            print(f"  {lang}: {count} ({pct:.1f}%)")
        
        # Top仓库
        print(f"\n=== Top 10 Star仓库 ===")
        top_repos = self.find_most_starred(stars, 10)
        for i, repo in enumerate(top_repos, 1):
            print(f"  {i}. {repo['full_name']} ⭐ {repo['stargazers_count']}")
        
        # 更新频率
        print(f"\n=== 更新频率 ===")
        update_freq = self.analyze_update_frequency(stars)
        print(f"  30天内更新: {update_freq['recent_30d']}")
        print(f"  1年内更新: {update_freq['older']}")
        print(f"  1年以上未更新: {update_freq['very_old']}")
        
        return {
            "total_stars": len(stars),
            "language_distribution": dict(lang_dist),
            "top_repos": top_repos,
            "update_frequency": update_freq
        }
    
    def export_to_json(self, username, output_file="stars_analysis.json"):
        """导出分析结果到JSON"""
        report = self.generate_report(username)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存到: {output_file}")


def main():
    """主函数"""
    # 从环境变量获取token
    token = os.environ.get('GITHUB_TOKEN', '')
    
    if not token:
        print("请设置 GITHUB_TOKEN 环境变量")
        print("export GITHUB_TOKEN=your_token")
        return
    
    analyzer = GitHubStarsAnalyzer(token)
    
    # 分析指定用户的stars
    username = input("请输入GitHub用户名: ").strip()
    if username:
        analyzer.export_to_json(username)


if __name__ == "__main__":
    main()
