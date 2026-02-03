#!/usr/bin/env python3
"""
GitHub Contribution Heatmap Simulator
生成模拟的GitHub贡献热力图

功能：
- 生成每日贡献数据
- 创建热力图可视化
- 统计贡献趋势
"""

import random
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os

class ContributionHeatmap:
    """GitHubi��格贡献热力图生成器"""
    
    def __init__(self, year=2026, start_month=1):
        self.year = year
        self.start_date = datetime(year, start_month, 1)
        self.contributions = defaultdict(int)
        self.levels = [0, 1, 3, 5, 8, 12]  # GitHub贡献级别
        
    def generate_random_contributions(self, days=365, max_daily=15):
        """生成随机贡献数据"""
        for i in range(days):
            date = self.start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            # 70%的天数有贡献，贡献量随机
            if random.random() < 0.7:
                level = random.randint(0, 5)
                self.contributions[date_str] = random.randint(
                    self.levels[level], 
                    self.levels[min(level+1, 5)] if level < 5 else max_daily
                )
            else:
                self.contributions[date_str] = 0
        return self.contributions
    
    def get_level(self, count):
        """根据贡献数量返回级别"""
        if count == 0:
            return 0
        elif count <= 1:
            return 1
        elif count <= 3:
            return 2
        elif count <= 5:
            return 3
        elif count <= 8:
            return 4
        else:
            return 5
    
    def print_heatmap(self, weeks=52):
        """打印热力图（ASCII版本）"""
        print(f"\n📊 GitHub Contribution Heatmap - {self.year}")
        print("=" * 60)
        
        # 星期标签
        days = ["Sun", "Mon", "Wed", "Fri"]
        print("".join([f"{d:>12}" for d in days]))
        
        # 按周显示
        current = self.start_date
        for week in range(weeks):
            row = ""
            for day in range(7):
                if current.year == self.year:
                    date_str = current.strftime("%Y-%m-%d")
                    count = self.contributions.get(date_str, 0)
                    level = self.get_level(count)
                    # 颜色块
                    blocks = ["░", "▁", "▂", "▃", "▅", "█"]
                    row += f"{blocks[level]:>12}"
                current += timedelta(days=1)
            print(row)
            if current.year > self.year:
                break
        
        print("=" * 60)
        self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        total = sum(self.contributions.values())
        active_days = sum(1 for v in self.contributions.values() if v > 0)
        total_days = len(self.contributions)
        
        print(f"\n📈 统计信息:")
        print(f"  • 总贡献数: {total}")
        print(f"  • 活跃天数: {active_days}/{total_days} ({active_days/total_days*100:.1f}%)")
        print(f"  • 日均贡献: {total/total_days:.1f}")
        print(f"  • 最忙日期: {max(self.contributions, key=self.contributions.get)}")
    
    def export_json(self, filename="contributions.json"):
        """导出为JSON格式"""
        data = {
            "year": self.year,
            "contributions": dict(self.contributions),
            "stats": {
                "total": sum(self.contributions.values()),
                "active_days": sum(1 for v in self.contributions.values() if v > 0)
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 已导出到 {filename}")


def demo():
    """演示函数"""
    print("🎯 GitHub Contribution Heatmap Generator")
    print("-" * 50)
    
    # 创建热力图生成器
    heatmap = ContributionHeatmap(year=2026)
    
    # 生成365天随机贡献数据
    heatmap.generate_random_contributions(days=365, max_daily=20)
    
    # 显示热力图
    heatmap.print_heatmap(weeks=52)
    
    # 导出数据
    heatmap.export_json()
    
    return heatmap


if __name__ == "__main__":
    demo()
