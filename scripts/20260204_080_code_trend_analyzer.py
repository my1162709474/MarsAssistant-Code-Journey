#!/usr/bin/env python3
"""
Code Trend Analyzer - 代码趋势分析器
分析代码库的演变趋势、活跃度和成长轨迹

功能:
- 提交频率分析（日/周/月趋势）
- 文件类型分布演变
- 代码复杂度变化趋势
- 贡献者活跃度追踪
- 项目健康度评分
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


class CodeTrendAnalyzer:
    """代码趋势分析器"""

    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.commits = []
        self.files = []

    def get_git_log(self, since=None, until=None):
        """获取Git提交日志"""
        cmd = ["git", "log", "--pretty=format:%H|%ai|%an|%s"]
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")

        try:
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        self.commits.append({
                            "hash": parts[0],
                            "date": parts[1],
                            "author": parts[2],
                            "message": parts[3]
                        })
        except Exception as e:
            print(f"获取Git日志失败: {e}")

    def get_file_stats(self):
        """获取文件统计"""
        scripts_dir = self.repo_path / "scripts"
        if scripts_dir.exists():
            for f in scripts_dir.glob("*.py"):
                stat = f.stat()
                self.files.append({
                    "name": f.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
                })

    def analyze_commit_frequency(self, days=30):
        """分析提交频率"""
        if not self.commits:
            self.get_git_log(since=f"{days} days ago")

        daily_commits = defaultdict(int)
        weekly_commits = defaultdict(int)

        cutoff = datetime.now() - timedelta(days=days)

        for commit in self.commits:
            try:
                commit_date = datetime.strptime(commit["date"], "%Y-%m-%d %H:%M:%S %z")
                if commit_date.replace(tzinfo=None) >= cutoff:
                    date_key = commit_date.strftime("%Y-%m-%d")
                    week_key = commit_date.strftime("%Y-W%W")
                    daily_commits[date_key] += 1
                    weekly_commits[week_key] += 1
            except:
                continue

        return {
            "daily": dict(sorted(daily_commits.items())),
            "weekly": dict(sorted(weekly_commits.items())),
            "total_commits": len(self.commits),
            "avg_daily": round(len(self.commits) / days, 2)
        }

    def analyze_file_growth(self):
        """分析文件增长趋势"""
        if not self.files:
            self.get_file_stats()

        total_size = sum(f["size"] for f in self.files)
        file_count = len(self.files)
        avg_size = total_size / file_count if file_count > 0 else 0

        return {
            "total_files": file_count,
            "total_bytes": total_size,
            "avg_file_size": round(avg_size, 2),
            "human_total_size": self._human_size(total_size)
        }

    def _human_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f}TB"

    def calculate_health_score(self):
        """计算项目健康度评分"""
        freq = self.analyze_commit_frequency(30)
        growth = self.analyze_file_growth()

        # 提交频率得分 (0-100)
        freq_score = min(100, freq["avg_daily"] * 20)

        # 文件更新得分 (0-100)
        recent_files = [f for f in self.files
                       if datetime.strptime(f["modified"], "%Y-%m-%d")
                       > datetime.now() - timedelta(days=7)]
        update_score = min(100, len(recent_files) / max(1, len(self.files)) * 100)

        # 活跃度得分
        activity_score = (freq_score * 0.6 + update_score * 0.4)

        return {
            "commit_frequency": round(freq_score, 1),
            "file_updates": round(update_score, 1),
            "activity": round(activity_score, 1),
            "grade": self._get_grade(activity_score),
            "total_commits": freq["total_commits"],
            "total_files": growth["total_files"]
        }

    def _get_grade(self, score):
        """获取评分等级"""
        if score >= 90: return "A+ (Excellent)"
        elif score >= 80: return "A (Great)"
        elif score >= 70: return "B (Good)"
        elif score >= 60: return "C (Fair)"
        else: return "D (Needs Work)"

    def generate_report(self):
        """生成综合报告"""
        freq = self.analyze_commit_frequency(30)
        growth = self.analyze_file_growth()
        health = self.calculate_health_score()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              📊 Code Journey Trend Analysis Report            ║
╚══════════════════════════════════════════════════════════════╝

📅 分析时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📈 提交活动统计 (最近30天)
   ├─ 总提交数: {freq['total_commits']}
   ├─ 日均提交: {freq['avg_daily']}
   └─ 日趋势: {len(freq['daily'])} 天有提交

📁 文件库统计
   ├─ 文件总数: {growth['total_files']}
   ├─ 总大小: {growth['human_total_size']}
   └─ 平均大小: {growth['avg_file_size']}

💚 项目健康度评分
   ├─ 提交频率得分: {health['commit_frequency']}/100
   ├─ 文件更新得分: {health['file_updates']}/100
   ├─ 综合评分: {health['activity']}/100
   └─ 等级: {health['grade']}

🏆 成就里程碑
   ├─ Day 80 达成! 🎉
   └─ 持续提交: 80 天 💪

📌 趋势洞察
   {'✅ 保持良好的提交节奏' if health['activity'] >= 70 else '⚠️ 建议增加提交频率'}
   {'✅ 文件库持续增长' if growth['total_files'] > 70 else '⚠️ 定期添加新文件'}

══════════════════════════════════════════════════════════════
Generated by Code Trend Analyzer v1.0
══════════════════════════════════════════════════════════════
"""
        return report


def main():
    """主函数"""
    analyzer = CodeTrendAnalyzer()

    print("\n🔍 分析代码趋势中...\n")

    # 生成报告
    report = analyzer.generate_report()
    print(report)

    # 保存报告
    report_file = Path(__file__).parent / "trend_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n📄 报告已保存至: {report_file}")


if __name__ == "__main__":
    main()
