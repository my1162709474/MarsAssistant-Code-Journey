#!/usr/bin/env python3
"""
Git Commit Pattern Analyzer - Git 提交模式分析与可视化工具

分析 Git 仓库的提交模式，生成提交热力图、时间分布图表和统计数据。
支持本地仓库和远程仓库分析。

功能:
- 提交频率热力图（年度视图）
- 星期/小时提交分布
- 提交消息长度统计
- 提交者活跃度排名
- 提交模式可视化
"""

import subprocess
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class GitCommitAnalyzer:
    """Git 提交模式分析器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.commits = []
    
    def run_git_command(self, args: List[str]) -> str:
        """执行 git 命令"""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""
        except FileNotFoundError:
            print("Error: git command not found")
            return ""
    
    def fetch_commits(self, max_count: int = 1000) -> List[Dict]:
        """获取提交历史"""
        # git log format: hash|author_name|author_date|author_email|subject|body
        format_str = "%H|%an|%ai|%ae|%s|%b"
        cmd = ["log", f"-{max_count}", f"--format={format_str}", "--no-merges"]
        
        output = self.run_git_command(cmd)
        lines = output.strip().split('\n') if output.strip() else []
        
        self.commits = []
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split('|', 5)
            if len(parts) >= 5:
                commit = {
                    'hash': parts[0],
                    'author': parts[1],
                    'date': datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S %z"),
                    'email': parts[3],
                    'subject': parts[4],
                    'body': parts[5] if len(parts) > 5 else ""
                }
                self.commits.append(commit)
        
        return self.commits
    
    def analyze_by_day_of_week(self) -> Dict[int, int]:
        """按星期分析提交分布 (0=周一, 6=周日)"""
        day_counts = defaultdict(int)
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        for commit in self.commits:
            weekday = commit['date'].weekday()
            day_counts[weekday] += 1
        
        return {day_names[k]: v for k, v in sorted(day_counts.items())}
    
    def analyze_by_hour(self) -> Dict[int, int]:
        """按小时分析提交分布"""
        hour_counts = defaultdict(int)
        
        for commit in self.commits:
            hour = commit['date'].hour
            hour_counts[hour] += 1
        
        return dict(sorted(hour_counts.items()))
    
    def analyze_by_month(self) -> Dict[str, int]:
        """按月份分析提交分布"""
        month_counts = defaultdict(int)
        month_names = ['1月', '2月', '3月', '4月', '5月', '6月', 
                       '7月', '8月', '9月', '10月', '11月', '12月']
        
        for commit in self.commits:
            month = commit['date'].month
            month_counts[month_names[month - 1]] += 1
        
        return month_counts
    
    def get_author_stats(self) -> List[Tuple[str, int, int]]:
        """获取提交者统计"""
        author_counts = defaultdict(int)
        author_lines = defaultdict(int)
        
        for commit in self.commits:
            author_counts[commit['author']] += 1
            author_lines[commit['author']] += len(commit['body'].split('\n'))
        
        stats = []
        for author, count in sorted(author_counts.items(), key=lambda x: -x[1]):
            avg_lines = author_lines[author] / count if count > 0 else 0
            stats.append((author, count, avg_lines))
        
        return stats[:20]  # Top 20
    
    def get_commit_message_stats(self) -> Dict:
        """获取提交消息统计"""
        subjects = [c['subject'] for c in self.commits]
        bodies = [c['body'] for c in self.commits if c['body'].strip()]
        
        subject_lengths = [len(s) for s in subjects]
        body_lengths = [len(b) for b in bodies] if bodies else [0]
        
        return {
            'avg_subject_length': sum(subject_lengths) / len(subjects) if subjects else 0,
            'max_subject_length': max(subject_lengths) if subjects else 0,
            'commits_with_body': len(bodies),
            'total_commits': len(self.commits),
            'body_percentage': (len(bodies) / len(self.commits) * 100) if self.commits else 0
        }
    
    def get_weekly_activity(self) -> Dict[str, int]:
        """获取每周活跃度"""
        # Find the date range
        if not self.commits:
            return {}
        
        start_date = min(c['date'] for c in self.commits).date()
        end_date = max(c['date'] for c in self.commits).date()
        
        # Create a dictionary of date -> commit count
        date_counts = defaultdict(int)
        for commit in self.commits:
            date_key = commit['date'].date()
            date_counts[date_key] += 1
        
        # Group by week
        week_counts = defaultdict(int)
        current = start_date
        while current <= end_date:
            week_start = current - timedelta(days=current.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_commits = sum(1 for date, count in date_counts.items() 
                             if week_start <= date <= week_end)
            week_label = week_start.strftime("%Y-%m-%d")
            week_counts[week_label] = week_commits
            
            current += timedelta(days=7)
        
        return week_counts
    
    def generate_heatmap_data(self, year: int = None) -> Dict[Tuple[int, int], int]:
        """生成热力图数据 (星期 x 小时)"""
        heatmap_data = defaultdict(int)
        
        for commit in self.commits:
            if year and commit['date'].year != year:
                continue
            weekday = commit['date'].weekday()
            hour = commit['date'].hour
            heatmap_data[(weekday, hour)] += 1
        
        return dict(heatmap_data)
    
    def print_summary(self):
        """打印分析摘要"""
        if not self.commits:
            print("No commits found!")
            return
        
        print("\n" + "="*60)
        print("Git Commit Pattern Analysis Summary")
        print("="*60)
        
        print(f"\n📊 Basic Statistics:")
        print(f"  Total commits: {len(self.commits)}")
        
        print(f"\n📅 Date Range:")
        if self.commits:
            first_commit = min(c['date'] for c in self.commits)
            last_commit = max(c['date'] for c in self.commits)
            print(f"  First commit: {first_commit.date()}")
            print(f"  Last commit: {last_commit.date()}")
            days = (last_commit.date() - first_commit.date()).days + 1
            print(f"  Days span: {days} days")
            print(f"  Average commits/day: {len(self.commits)/days:.2f}")
        
        print(f"\n🗓️ Top Days by Week:")
        day_stats = self.analyze_by_day_of_week()
        sorted_days = sorted(day_stats.items(), key=lambda x: -x[1])
        for day, count in sorted_days[:3]:
            print(f"  {day}: {count} commits")
        
        print(f"\n⏰ Top Hours:")
        hour_stats = self.analyze_by_hour()
        sorted_hours = sorted(hour_stats.items(), key=lambda x: -x[1])
        for hour, count in sorted_hours[:3]:
            print(f"  {hour:02d}:00 - {count} commits")
        
        print(f"\n👥 Top Contributors:")
        author_stats = self.get_author_stats()[:5]
        for author, count, _ in author_stats:
            print(f"  {author}: {count} commits")
        
        print(f"\n📝 Commit Message Stats:")
        msg_stats = self.get_commit_message_stats()
        print(f"  Avg subject length: {msg_stats['avg_subject_length']:.1f} chars")
        print(f"  Commits with body: {msg_stats['commits_with_body']} ({msg_stats['body_percentage']:.1f}%)")


class CommitVisualizer:
    """提交数据可视化器"""
    
    def __init__(self, analyzer: GitCommitAnalyzer):
        self.analyzer = analyzer
    
    def plot_all(self, output_path: str = None):
        """生成所有可视化图表"""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available. Skipping visualization.")
            return
        
        if not self.analyzer.commits:
            print("No commits to visualize.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Git Commit Pattern Analysis', fontsize=14, fontweight='bold')
        
        # 1. Weekly distribution
        ax1 = axes[0, 0]
        day_stats = self.analyzer.analyze_by_day_of_week()
        days = list(day_stats.keys())
        counts = list(day_stats.values())
        bars1 = ax1.bar(days, counts, color='steelblue', edgecolor='navy')
        ax1.set_title('Commits by Day of Week')
        ax1.set_ylabel('Number of Commits')
        for bar, count in zip(bars1, counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontsize=9)
        
        # 2. Hourly distribution
        ax2 = axes[0, 1]
        hour_stats = self.analyzer.analyze_by_hour()
        hours = list(range(24))
        hour_counts = [hour_stats.get(h, 0) for h in hours]
        ax2.bar(hours, hour_counts, color='coral', edgecolor='darkred')
        ax2.set_title('Commits by Hour of Day')
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Number of Commits')
        ax2.set_xticks(range(0, 24, 2))
        
        # 3. Monthly distribution
        ax3 = axes[1, 0]
        month_stats = self.analyzer.analyze_by_month()
        months = list(month_stats.keys())
        month_counts = list(month_stats.values())
        ax3.bar(months, month_counts, color='seagreen', edgecolor='darkgreen')
        ax3.set_title('Commits by Month')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Number of Commits')
        
        # 4. Top contributors
        ax4 = axes[1, 1]
        author_stats = self.analyzer.get_author_stats()[:10]
        authors = [a[0][:15] for a in author_stats]
        author_counts = [a[1] for a in author_stats]
        ax4.barh(authors, author_counts, color='mediumpurple', edgecolor='purple')
        ax4.set_title('Top Contributors')
        ax4.set_xlabel('Number of Commits')
        ax4.invert_yaxis()
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Chart saved to: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_heatmap(self, output_path: str = None):
        """生成提交热力图"""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available. Skipping heatmap.")
            return
        
        if not self.analyzer.commits:
            print("No commits for heatmap.")
            return
        
        heatmap_data = self.analyzer.generate_heatmap_data()
        
        # Create a 7x24 matrix
        matrix = [[heatmap_data.get((day, hour), 0) for hour in range(24)] for day in range(7)]
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hour_labels = [f'{h:02d}' for h in range(24)]
        
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
        
        ax.set_xticks(range(24))
        ax.set_xticklabels(hour_labels)
        ax.set_yticks(range(7))
        ax.set_yticklabels(day_labels)
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        ax.set_title('Commit Activity Heatmap (GitHub-style)')
        
        plt.colorbar(im, ax=ax, label='Number of Commits')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Heatmap saved to: {output_path}")
        else:
            plt.show()
        
        plt.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Commit Pattern Analyzer')
    parser.add_argument('path', nargs='?', default='.', help='Repository path')
    parser.add_argument('-n', '--max-commits', type=int, default=1000, 
                       help='Maximum number of commits to analyze')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output file for charts')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization')
    parser.add_argument('--heatmap', action='store_true',
                       help='Generate heatmap only')
    
    args = parser.parse_args()
    
    # Check if path is a git repository
    if not os.path.exists(os.path.join(args.path, '.git')):
        print(f"Error: {args.path} is not a git repository")
        sys.exit(1)
    
    # Create analyzer and fetch commits
    analyzer = GitCommitAnalyzer(args.path)
    analyzer.fetch_commits(args.max_commits)
    
    # Print summary
    analyzer.print_summary()
    
    # Generate visualizations
    if not args.no_viz and MATPLOTLIB_AVAILABLE:
        visualizer = CommitVisualizer(analyzer)
        
        if args.heatmap:
            output_path = args.output or 'commit_heatmap.png'
            visualizer.plot_heatmap(output_path)
        else:
            output_path = args.output or 'commit_analysis.png'
            visualizer.plot_all(output_path)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
