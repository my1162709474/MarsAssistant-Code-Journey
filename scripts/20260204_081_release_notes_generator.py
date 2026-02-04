#!/usr/bin/env python3
"""
GitHub Release Notes Generator
自动从Git提交记录生成发布说明
"""

import subprocess
import json
import base64
from datetime import datetime, timedelta
from collections import defaultdict
import os

class ReleaseNotesGenerator:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
    
    def get_commits_since(self, days=7):
        """获取最近N天的提交记录"""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        result = subprocess.run(
            ["git", "log", f"--since={since_date}", "--pretty=format:%H|%s|%an|%ad", "--date=short"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                commits.append({
                    "sha": parts[0],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3]
                })
        return commits
    
    def categorize_commit(self, message):
        """根据提交消息分类提交类型"""
        msg_lower = message.lower()
        
        if any(kw in msg_lower for kw in ["feat", "feature", "add", "new"]):
            return "Features"
        elif any(kw in msg_lower for kw in ["fix", "bug", "issue", "resolve"]):
            return "Bug Fixes"
        elif any(kw in msg_lower for kw in ["perf", "optimize", "speed", "faster"]):
            return "Performance"
        elif any(kw in msg_lower for kw in ["docs", "doc", "readme", "comment"]):
            return "Documentation"
        elif any(kw in msg_lower for kw in ["refactor", "refactor", "cleanup", "structure"]):
            return "Refactoring"
        elif any(kw in msg_lower for kw in ["test", "coverage", "unit"]):
            return "Tests"
        else:
            return "Other"
    
    def group_by_category(self, commits):
        """按类别分组提交"""
        groups = defaultdict(list)
        for commit in commits:
            category = self.categorize_commit(commit["message"])
            groups[category].append(commit)
        return dict(groups)
    
    def generate_release_notes(self, version="1.0.0", days=7):
        """生成发布说明"""
        commits = self.get_commits_since(days)
        if not commits:
            return "# Release Notes\n\nNo commits found."
        
        groups = self.group_by_category(commits)
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        md = f"""# Release Notes - {version}

**Release Date:** {date_str}

---

## Summary
- **Total Commits:** {len(commits)}
- **Contributors:** {len(set(c['author'] for c in commits))}

---

"""
        category_order = ["Features", "Bug Fixes", "Performance", "Refactoring", "Tests", "Documentation", "Other"]
        
        for category in category_order:
            if category in groups:
                cat_commits = groups[category]
                emoji = {
                    "Features": "✨", "Bug Fixes": "🐛", "Performance": "⚡",
                    "Refactoring": "♻️", "Tests": "🧪", "Documentation": "📚", "Other": "📝"
                }
                md += f"### {emoji.get(category, '•')} {category}\n\n"
                for commit in cat_commits:
                    sha_short = commit["sha"][:7]
                    md += f"- {commit['message']} (`{sha_short}`)\n"
                md += "\n"
        
        # 添加详细提交列表
        md += f"""---

## All Commits

| Date | Author | Message | SHA |
|------|--------|---------|-----|
"""
        for commit in commits:
            sha_short = commit["sha"][:7]
            md += f"| {commit['date']} | {commit['author']} | {commit['message']} | `{sha_short}` |\n"
        
        return md
    
    def save_release_notes(self, version, output_file="RELEASE_NOTES.md", days=7):
        """保存发布说明到文件"""
        notes = self.generate_release_notes(version, days)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(notes)
        return notes

if __name__ == "__main__":
    # 示例用法
    generator = ReleaseNotesGenerator()
    
    # 生成发布说明
    notes = generator.generate_release_notes(
        version="1.0.0",
        days=7
    )
    
    print(notes)
    print("\n" + "="*50)
    print("✅ Release notes generated successfully!")
    print("📝 To save to file: generator.save_release_notes('1.0.0', 'RELEASE.md')")
