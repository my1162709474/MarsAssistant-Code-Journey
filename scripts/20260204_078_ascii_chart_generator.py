#!/usr/bin/env python3
"""
ASCII Chart Generator - ASCII艺术图表生成器
支持多种图表类型：柱状图、折线图、饼图、水平柱状图

作者: AI Assistant
日期: 2026-02-04
"""

import math
from typing import List, Dict, Optional


class ASCIIGraph:
    """ASCII图表生成器主类"""
    
    def __init__(self, width: int = 60, height: int = 20):
        self.width = width
        self.height = height
    
    def bar_chart(self, data: Dict[str, float], 
                  title: str = "Bar Chart") -> str:
        """生成垂直柱状图"""
        if not data:
            return "No data provided."
        
        labels = list(data.keys())
        values = list(data.values())
        max_val = max(values)
        min_val = min(values)
        
        lines = []
        lines.append(f"📊 {title}")
        lines.append("=" * self.width)
        
        if max_val == min_val:
            lines.append("█" * self.width)
            return "\n".join(lines)
        
        y_label_width = max(len(f"{max_val:.1f}"), len(f"{min_val:.1f}")) + 1
        num_bars = len(labels)
        bar_width = max(1, (self.width - num_bars - 10) // num_bars)
        gap = max(1, bar_width // 4)
        
        for row in range(self.height, 0, -1):
            y_val = min_val + (max_val - min_val) * (row - 1) / self.height
            line = f"{y_val:>{y_label_width}.1f} │ "
            
            for value in values:
                bar_height = int((value - min_val) / (max_val - min_val) * self.height)
                if bar_height >= row:
                    line += "█" * bar_width
                else:
                    line += " " * bar_width
                line += " " * gap
            
            lines.append(line)
        
        lines.append(" " * y_label_width + " └" + "─" * (self.width - y_label_width - 2))
        
        x_labels = ""
        for label in labels:
            label_str = label[:bar_width] if len(label) > bar_width else label
            x_labels += label_str.center(bar_width) + " " * gap
        lines.append(" " * (y_label_width + 2) + x_labels.rstrip())
        
        return "\n".join(lines)
    
    def horizontal_bar(self, data: Dict[str, float],
                      title: str = "Horizontal Bar Chart") -> str:
        """生成水平柱状图"""
        if not data:
            return "No data provided."
        
        max_val = max(data.values())
        
        lines = []
        lines.append(f"📊 {title}")
        lines.append("=" * self.width)
        
        max_label_len = max(len(label) for label in data.keys())
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_len = int(value / max_val * (self.width - max_label_len - 15))
            bar = "█" * bar_len
            percentage = value / max_val * 100
            lines.append(f"{label:>{max_label_len}} │ {bar} {value:.1f} ({percentage:.1f}%)")
        
        return "\n".join(lines)
    
    def line_chart(self, data: List[float],
                   title: str = "Line Chart",
                   labels: Optional[List[str]] = None) -> str:
        """生成折线图"""
        if not data:
            return "No data provided."
        
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        lines = []
        lines.append(f"📈 {title}")
        lines.append("=" * self.width)
        
        scaled = [int((v - min_val) / range_val * (self.height - 1)) for v in data]
        
        for row in range(self.height, -1, -1):
            y_val = min_val + (max_val - min_val) * row / self.height
            line = f"{y_val:>8.2f} │ "
            
            for i, s_val in enumerate(scaled):
                if s_val == row:
                    point = "●" if i == 0 or i == len(scaled) - 1 else "─"
                    line += point
                elif s_val > row:
                    line += " "
                else:
                    line += " "
            
            lines.append(line)
        
        lines.append(" " * 9 + "└" + "─" * (len(data) * 2 - 1))
        
        if labels:
            x_line = " " * 9
            for label in labels:
                label_str = label[:2] if len(label) > 2 else label
                x_line += label_str.center(2)
            lines.append(x_line)
        
        return "\n".join(lines)
    
    def pie_chart(self, data: Dict[str, float],
                  title: str = "Pie Chart") -> str:
        """生成ASCII饼图"""
        if not data:
            return "No data provided."
        
        total = sum(data.values())
        if total == 0:
            return "No data provided."
        
        lines = []
        lines.append(f"🥧 {title}")
        lines.append("=" * self.width)
        
        colors = ['█', '▓', '▒', '░', '▚', '▞', '▣', '◈']
        
        radius = min(self.width // 2 - 20, self.height // 2 - 4)
        center_x = radius + 10
        center_y = radius + 2
        
        pie = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if center_x - radius <= x <= center_x + radius:
                    dx = x - center_x
                    dy = center_y - y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist <= radius:
                        angle = math.atan2(dy, dx)
                        if angle < 0:
                            angle += 2 * math.pi
                        pct = angle / (2 * math.pi)
                        cumsum = 0
                        for i, (label, value) in enumerate(data.items()):
                            cumsum += value / total
                            if pct <= cumsum:
                                row.append(colors[i % len(colors)])
                                break
                        else:
                            row.append(' ')
                    else:
                        row.append(' ')
                else:
                    row.append(' ')
            pie.append(''.join(row))
        
        for i, line in enumerate(pie):
            if center_y - radius <= i <= center_y + radius:
                lines.append(line)
        
        lines.append("\n" + "─" * 40)
        lines.append("Legend:")
        for i, (label, value) in enumerate(data.items()):
            pct = value / total * 100
            lines.append(f"{colors[i % len(colors)]} {label}: {value:.1f} ({pct:.1f}%)")
        
        return "\n".join(lines)


def demo():
    """演示函数"""
    print("\n" + "=" * 60)
    print("🎨 ASCII Chart Generator Demo")
    print("=" * 60 + "\n")
    
    graph = ASCIIGraph(width=50, height=15)
    
    # 柱状图
    bar_data = {
        'Python': 85,
        'JavaScript': 72,
        'Rust': 68,
        'Go': 55,
        'TypeScript': 90,
        'C++': 60
    }
    print(graph.bar_chart(bar_data, "Programming Language Popularity"))
    print()
    
    # 水平柱状图
    hbar_data = {
        'Reading': 45,
        'Writing': 30,
        'Coding': 80,
        'Testing': 25,
        'Debugging': 35
    }
    print(graph.horizontal_bar(hbar_data, "Time Distribution (hours/week)"))
    print()
    
    # 折线图
    line_data = [23, 25, 28, 35, 42, 38, 45, 52, 48, 55, 62, 58]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    print(graph.line_chart(line_data, "Monthly Temperature", labels=months))
    print()
    
    # 饼图
    pie_data = {'Work': 8, 'Sleep': 7, 'Learning': 3, 'Entertainment': 4, 'Other': 2}
    print(graph.pie_chart(pie_data, "Daily Time Distribution"))


if __name__ == "__main__":
    demo()
