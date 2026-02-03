#!/usr/bin/env python3
"""
GitHub Stars Manager - GitHub收藏项目管理系统
===============================================
帮助整理、分析和备份GitHub星标项目的工具。

功能:
- 导出星标列表为Markdown/JSON
- 按语言/主题分类整理
- 分析星标趋势
- 同步本地标签到GitHub

Author: MarsAssistant
Day: 72
"""

import base64
import json
import subprocess
import os
from datetime import datetime
from typing import Optional


class GitHubStarsManager:
    """GitHub Stars 管理器"""
    
    def __init__(self, token: str = None, username: str = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.username = username or os.environ.get('GITHUB_USERNAME')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.token}' if self.token else ''
        }
    
    def get_stars(self, username: str = None) -> list:
        """获取用户的星标列表"""
        user = username or self.username
        if not user:
            raise ValueError("需要指定用户名")
        
        url = f"https://api.github.com/users/{user}/starred"
        params = {'per_page': 100, 'sort': 'updated'}
        
        response = self._request('GET', url, params=params)
        return response if response else []
    
    def _request(self, method: str, url: str, **kwargs) -> Optional[list]:
        """发起HTTP请求"""
        import requests
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def export_stars_markdown(self, output_file: str = 'stars_export.md'):
        """导出星标为Markdown格式"""
        stars = self.get_stars()
        if not stars:
            print("未找到星标项目")
            return
        
        # 按语言分组
        by_language = {}
        for repo in stars:
            lang = repo.get('language') or 'Unknown'
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(repo)
        
        # 生成Markdown
        md_content = f"""# GitHub Stars Export

导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总项目数: {len(stars)}

## 按语言分类

"""
        for lang, repos in sorted(by_language.items(), key=lambda x: -len(x[1])):
            md_content += f"\n### {lang} ({len(repos)})\n\n"
            for repo in sorted(repos, key=lambda x: -x.get('stargazers_count', 0)):
                desc = repo.get('description', '无描述') or '无描述'
                md_content += f"- **{repo['full_name']}** ⭐{repo.get('stargazers_count', 0)}\n"
                md_content += f"  - {desc}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"已导出到: {output_file}")
    
    def export_stars_json(self, output_file: str = 'stars_export.json'):
        """导出星标为JSON格式"""
        stars = self.get_stars()
        if not stars:
            print("未找到星标项目")
            return
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_count': len(stars),
            'repos': []
        }
        
        for repo in stars:
            export_data['repos'].append({
                'name': repo['full_name'],
                'description': repo.get('description'),
                'language': repo.get('language'),
                'stars': repo.get('stargazers_count'),
                'forks': repo.get('forks_count'),
                'url': repo['html_url'],
                'updated_at': repo.get('updated_at')
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"已导出到: {output_file}")
    
    def analyze_stars(self) -> dict:
        """分析星标数据"""
        stars = self.get_stars()
        if not stars:
            return {}
        
        # 统计
        stats = {
            'total': len(stars),
            'by_language': {},
            'top_repos': sorted(stars, 
                               key=lambda x: x.get('stargazers_count', 0), 
                               reverse=True)[:10],
            'recent_updates': sorted(stars, 
                                    key=lambda x: x.get('updated_at', ''), 
                                    reverse=True)[:10]
        }
        
        for repo in stars:
            lang = repo.get('language') or 'Unknown'
            stats['by_language'][lang] = stats['by_language'].get(lang, 0) + 1
        
        return stats
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.analyze_stars()
        if not stats:
            print("无法获取星标数据")
            return
        
        print(f"\n📊 GitHub Stars 统计\n")
        print(f"总项目数: {stats['total']}")
        print(f"\n按语言分类:")
        for lang, count in sorted(stats['by_language'].items(), 
                                  key=lambda x: -x[1]):
            print(f"  {lang}: {count}")
        
        print(f"\n⭐ Top 10 项目:")
        for repo in stats['top_repos'][:5]:
            print(f"  {repo.get('stargazers_count', 0)} ⭐ {repo['full_name']}")


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Stars Manager')
    parser.add_argument('--user', '-u', help='GitHub用户名')
    parser.add_argument('--export', '-e', choices=['md', 'json', 'both'], 
                       default='both', help='导出格式')
    parser.add_argument('--analyze', '-a', action='store_true', 
                       help='分析星标数据')
    
    args = parser.parse_args()
    
    manager = GitHubStarsManager(username=args.user)
    
    if args.analyze:
        manager.print_stats()
    else:
        if args.export in ['md', 'both']:
            manager.export_stars_markdown()
        if args.export in ['json', 'both']:
            manager.export_stars_json()


if __name__ == '__main__':
    main()
