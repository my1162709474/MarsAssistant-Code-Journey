#!/usr/bin/env python3
"""
GitHub Trending Repository Crawler
GitHub趋势仓库爬虫工具 - 自动抓取GitHub热门仓库

Author: MarsAssistant
Day: 80
"""

import requests
import json
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class GitHubTrending:
    """GitHub Trending 爬虫类"""
    
    BASE_URL = "https://api.github.com"
    TRENDING_URL = "https://github.com/trending"
    
    # 支持的语言列表
    SUPPORTED_LANGUAGES = {
        'python': 'Python',
        'javascript': 'JavaScript', 
        'typescript': 'TypeScript',
        'java': 'Java',
        'go': 'Go',
        'rust': 'Rust',
        'cpp': 'C++',
        'c': 'C',
        'ruby': 'Ruby',
        'php': 'PHP',
        'swift': 'Swift',
        'kotlin': 'Kotlin',
        'scala': 'Scala',
        'shell': 'Shell',
        'vue': 'Vue',
        'angular': 'Angular',
        'react': 'React',
        'jupyter-notebook': 'Jupyter Notebook'
    }
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化爬虫
        
        Args:
            token: GitHub Personal Access Token (可选，用于提高API限制)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Trending-Crawler/1.0'
        })
        
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        
        # API限制追踪
        self.rate_limit_remaining = float('inf')
        self.rate_limit_reset = None
    
    def _check_rate_limit(self):
        """检查并更新API限制"""
        try:
            response = self.session.get(f"{self.BASE_URL}/rate_limit")
            if response.status_code == 200:
                data = response.json()
                # 搜索API的限制
                search_limit = data.get('resources', {}).get('search', {})
                self.rate_limit_remaining = search_limit.get('remaining', float('inf'))
                self.rate_limit_reset = search_limit.get('reset')
        except:
            pass
    
    def search_trending_repos(
        self,
        language: str = None,
        created_since: str = None,
        stars: str = None,
        per_page: int = 30,
        page: int = 1
    ) -> List[Dict]:
        """
        搜索趋势仓库
        
        Args:
            language: 编程语言
            created_since: 创建时间 (daily/weekly/monthly)
            stars: 最少stars数量
            per_page: 每页数量
            page: 页码
            
        Returns:
            仓库列表
        """
        # 构建查询
        query_parts = []
        
        if language and language.lower() in self.SUPPORTED_LANGUAGES:
            query_parts.append(f"language:{language}")
        
        if created_since:
            # 将 daily/weekly/monthly 转换为日期
            days_map = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            days = days_map.get(created_since.lower(), 1)
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query_parts.append(f"created:>={since_date}")
        
        if stars:
            query_parts.append(f"stars:>={stars}")
        
        # 排序
        query_parts.append("sort:stars")
        
        query = " ".join(query_parts)
        
        # API调用
        url = f"{self.BASE_URL}/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(per_page, 100),
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            
            # 更新速率限制
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                self.rate_limit_reset = int(reset_time)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            elif response.status_code == 403:
                print("⚠️ API速率限制已达到，请稍后再试或提供token")
                return []
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return []
    
    def parse_trending_page(self, language: str = None, timeframe: str = 'daily') -> List[Dict]:
        """
        解析GitHub Trending页面 (备用方案)
        
        Args:
            language: 编程语言
            timeframe: 时间范围 (daily/weekly/monthly)
            
        Returns:
            仓库列表
        """
        url = self.TRENDING_URL
        if language:
            url += f"/{language}"
        url += f"?since={timeframe}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 简化解析 - 返回URL列表
                import re
                repo_pattern = r'/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+'
                repos = re.findall(repo_pattern, response.text)
                
                # 去重
                unique_repos = list(set(repos))[:25]
                
                return [{
                    'full_name': repo.strip('/'),
                    'html_url': f"https://github.com{repo}"
                } for repo in unique_repos]
            
            return []
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return []
    
    def get_repo_details(self, owner: str, repo: str) -> Optional[Dict]:
        """
        获取仓库详细信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名
            
        Returns:
            仓库详情字典
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"❌ 获取仓库详情失败: {e}")
            return None
    
    def analyze_trending(self, repos: List[Dict]) -> Dict:
        """
        分析趋势数据
        
        Args:
            repos: 仓库列表
            
        Returns:
            分析结果
        """
        if not repos:
            return {}
        
        languages = {}
        total_stars = 0
        total_forks = 0
        has_description = 0
        
        for repo in repos:
            total_stars += repo.get('stargazers_count', 0)
            total_forks += repo.get('forks_count', 0)
            
            lang = repo.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
            
            if repo.get('description'):
                has_description += 1
        
        return {
            'total_repos': len(repos),
            'total_stars': total_stars,
            'avg_stars': round(total_stars / len(repos), 1),
            'total_forks': total_forks,
            'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
            'description_coverage': round(has_description / len(repos) * 100, 1)
        }
    
    def export_json(self, repos: List[Dict], filename: str):
        """
        导出为JSON格式
        
        Args:
            repos: 仓库列表
            filename: 文件名
        """
        output = {
            'generated_at': datetime.now().isoformat(),
            'total_count': len(repos),
            'repos': repos
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已导出JSON: {filename}")
    
    def export_csv(self, repos: List[Dict], filename: str):
        """
        导出为CSV格式
        
        Args:
            repos: 仓库列表
            filename: 文件名
        """
        if not repos:
            print("⚠️ 没有数据可导出")
            return
        
        fieldnames = ['full_name', 'html_url', 'description', 'language', 
                      'stargazers_count', 'forks_count', 'open_issues_count',
                      'created_at', 'updated_at', 'owner.login']
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for repo in repos:
                row = {field: repo.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"✅ 已导出CSV: {filename}")
    
    def export_markdown(self, repos: List[Dict], filename: str, title: str = None):
        """
        导出为Markdown格式
        
        Args:
            repos: 仓库列表
            filename: 文件名
            title: 标题
        """
        if title is None:
            title = f"GitHub Trending Repositories - {datetime.now().strftime('%Y-%m-%d')}"
        
        md_lines = [
            f"# {title}\n",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"总数量: {len(repos)}\n",
            "---\n\n"
        ]
        
        for i, repo in enumerate(repos, 1):
            md_lines.append(f"## {i}. {repo.get('full_name', 'Unknown')}\n")
            md_lines.append(f"- ⭐ Stars: {repo.get('stargazers_count', 0)}")
            md_lines.append(f" | 🍴 Forks: {repo.get('forks_count', 0)}")
            md_lines.append(f" | 🐛 Issues: {repo.get('open_issues_count', 0)}\n")
            md_lines.append(f"- 🏷️ Language: {repo.get('language', 'N/A')}\n")
            
            if repo.get('description'):
                md_lines.append(f"\n📝 {repo.get('description')}\n")
            
            md_lines.append(f"\n🔗 [View on GitHub]({repo.get('html_url', '')})\n")
            md_lines.append("\n---\n\n")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(''.join(md_lines))
        
        print(f"✅ 已导出Markdown: {filename}")


def demo():
    """演示函数"""
    print("🚀 GitHub Trending Crawler Demo")
    print("=" * 50)
    
    # 创建爬虫实例
    crawler = GitHubTrending()
    
    # 检查速率限制
    print("\n📊 检查API速率限制...")
    crawler._check_rate_limit()
    print(f"剩余请求: {crawler.rate_limit_remaining}")
    
    # 搜索趋势仓库 (Python语言)
    print("\n🔍 搜索Python趋势仓库...")
    repos = crawler.search_trending_repos(
        language='python',
        stars='100',
        per_page=10
    )
    
    if repos:
        print(f"\n✅ 找到 {len(repos)} 个仓库\n")
        
        # 显示前5个
        for i, repo in enumerate(repos[:5], 1):
            print(f"{i}. {repo.get('full_name')}")
            print(f"   ⭐ {repo.get('stargazers_count')} | 🍴 {repo.get('forks_count')}")
            print(f"   🏷️ {repo.get('language')}")
            print()
        
        # 分析结果
        analysis = crawler.analyze_trending(repos)
        print("📈 数据分析:")
        print(f"   - 总Stars: {analysis.get('total_stars')}")
        print(f"   - 平均Stars: {analysis.get('avg_stars')}")
        print(f"   - 语言分布: {analysis.get('languages')}")
        
        # 导出文件
        print("\n💾 导出数据...")
        crawler.export_json(repos, 'trending_repos.json')
        crawler.export_csv(repos, 'trending_repos.csv')
        crawler.export_markdown(repos, 'trending_repos.md')
    else:
        print("❌ 未找到仓库或API限制")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='GitHub Trending Repository Crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python github_trending.py --language python --stars 100
  python github_trending.py --language javascript --output json
  python github_trending.py --language go --timeframe weekly
        """
    )
    
    parser.add_argument('-l', '--language', 
                        help='编程语言 (python/javascript/go/rust等)')
    parser.add_argument('-s', '--stars', type=int, default=100,
                        help='最少stars数量 (默认: 100)')
    parser.add_argument('-p', '--per-page', type=int, default=30,
                        help='每页数量 (默认: 30)')
    parser.add_argument('-o', '--output', 
                        choices=['json', 'csv', 'markdown', 'all'],
                        default='all',
                        help='输出格式 (默认: all)')
    parser.add_argument('-t', '--timeframe',
                        choices=['daily', 'weekly', 'monthly'],
                        default='daily',
                        help='时间范围 (默认: daily)')
    parser.add_argument('--token',
                        help='GitHub Personal Access Token (可选)')
    parser.add_argument('--demo', action='store_true',
                        help='运行演示')
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        return
    
    # 创建爬虫
    crawler = GitHubTrending(token=args.token)
    
    print(f"🔍 搜索趋势仓库: {args.language or '全部'} | Stars ≥ {args.stars}")
    
    # 搜索
    repos = crawler.search_trending_repos(
        language=args.language,
        stars=str(args.stars),
        per_page=args.per_page
    )
    
    if repos:
        print(f"\n✅ 找到 {len(repos)} 个仓库\n")
        
        # 分析
        analysis = crawler.analyze_trending(repos)
        print("📈 统计:")
        print(f"   总Stars: {analysis.get('total_stars')}")
        print(f"   平均Stars: {analysis.get('avg_stars')}")
        print(f"   语言分布: {list(analysis.get('languages', {}).items())[:5]}")
        
        # 导出
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        lang_prefix = args.language or 'all'
        
        if args.output in ['json', 'all']:
            crawler.export_json(repos, f'trending_{lang_prefix}_{timestamp}.json')
        if args.output in ['csv', 'all']:
            crawler.export_csv(repos, f'trending_{lang_prefix}_{timestamp}.csv')
        if args.output in ['markdown', 'all']:
            crawler.export_markdown(repos, f'trending_{lang_prefix}_{timestamp}.md')
    else:
        print("❌ 未找到仓库")


if __name__ == '__main__':
    main()
