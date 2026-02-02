#!/usr/bin/env python3
"""
ASCII Chart Generator - 终端ASCII图表生成器 📊
==============================================
一个用于在终端中生成ASCII条形图、折线图和饼图的工具。

支持功能:
- 水平/垂直条形图
- 折线图
- 简单的饼图(字符模式)
- 多数据集对比
- 颜色支持(可选)
- 导出到文件
"""

import sys
import os
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 颜色配置(可选依赖)
try:
    from termcolor import colored
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False


class ChartType(Enum):
    """图表类型枚举"""
    HORIZONTAL_BAR = "horizontal_bar"
    VERTICAL_BAR = "vertical_bar"
    LINE = "line"
    STACKED_BAR = "stacked_bar"


class ColorPalette(Enum):
    """预设颜色调色板"""
    RAINBOW = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
    PASTEL = ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF']
    NEON = ['#FF00FF', '#00FFFF', '#FF00FF', '#00FF00']
    EARTH = ['#8B4513', '#228B22', '#4169E1', '#FFD700', '#DC143C']
    GRAYSCALE = ['#1a1a1a', '#4d4d4d', '#808080', '#b3b3b3', '#e6e6e6']


@dataclass
class DataPoint:
    """数据点"""
    label: str
    value: float
    color: Optional[str] = None


@dataclass
class DataSeries:
    """数据系列(用于多数据集)"""
    name: str
    data: List[DataPoint]
    color: Optional[str] = None


class ASCIIGraphics:
    """ASCII图形生成器核心类"""
    
    # 块字符用于条形图
    BLOCKS = {
        'full': '█',
        'seven_eighths': '▉',
        'three_quarters': '▊',
        'five_eighths': '▋',
        'half': '▌',
        'three_eighths': '▍',
        'quarter': '▎',
        'eighth': '▏',
    }
    
    # 折线图字符
    LINE_CHARS = {
        'horizontal': '─',
        'vertical': '│',
        'corner_tl': '┌',
        'corner_tr': '┐',
        'corner_bl': '└',
        'corner_br': '┘',
        'cross': '┼',
        'tee_up': '┴',
        'tee_down': '┬',
        'tee_left': '┤',
        'tee_right': '├',
        'dot': '·',
        'line': '━',
    }
    
    # 饼图字符
    PIE_CHARS = ['●', '○', '◐', '◑', '◓', '◒', '◑', '◕', '◔', '◷']
    
    def __init__(self, width: int = 60, height: int = 20, use_colors: bool = True):
        """
        初始化ASCII图形生成器
        
        Args:
            width: 图表宽度(字符数)
            height: 图表高度(行数)
            use_colors: 是否使用颜色
        """
        self.width = width
        self.height = height
        self.use_colors = use_colors and HAS_TERMCOLOR
        
    def _get_color(self, color: Optional[str], text: str) -> str:
        """获取带颜色的文本"""
        if color and self.use_colors:
            return colored(text, color)
        return text
        
    def _get_char_width(self, char: str) -> int:
        """获取字符宽度(CJK字符宽度为2)"""
        return 2 if '\u4e00' <= char <= '\u9fff' else 1
        
    def _truncate_label(self, label: str, max_width: int) -> str:
        """截断标签以适应最大宽度"""
        current_width = sum(self._get_char_width(c) for c in label)
        if current_width <= max_width:
            return label
            
        # 尝试在中间截断
        half = (max_width - 3) // 2
        return label[:half] + "..." + label[-half:] if half > 0 else "..."
    
    def _calculate_bar_length(self, value: float, max_value: float, 
                               available_width: int) -> int:
        """计算条形长度"""
        if max_value == 0:
            return 0
        ratio = value / max_value
        return int(ratio * available_width)
    
    def _calculate_bar_height(self, value: float, max_value: float,
                               available_height: int) -> int:
        """计算条形高度"""
        if max_value == 0:
            return 0
        ratio = value / max_value
        return max(1, int(ratio * available_height))
    
    def generate_horizontal_bar_chart(
        self,
        data: List[DataPoint],
        title: str = "",
        show_values: bool = True,
        bar_char: str = "█",
        label_width: int = 15,
        value_format: str = "{:.1f}"
    ) -> str:
        """
        生成水平条形图
        
        Args:
            data: 数据点列表
            title: 图表标题
            show_values: 是否显示数值
            bar_char: 条形字符
            label_width: 标签宽度
            value_format: 数值格式
            
        Returns:
            ASCII图表字符串
        """
        if not data:
            return "No data provided."
            
        # 计算最大值
        max_value = max(d.value for d in data)
        available_width = self.width - label_width - 15  # 留出数值显示空间
        
        # 构建图表
        lines = []
        
        # 标题
        if title:
            padding = (self.width - len(title)) // 2
            lines.append(" " * padding + title + "\n")
        
        # 边框顶部
        top_border = "┌" + "─" * (self.width - 2) + "┐"
        lines.append(top_border)
        
        # 数据行
        for point in data:
            # 标签
            truncated_label = self._truncate_label(point.label, label_width - 2)
            label_line = f"│ {truncated_label:<{label_width - 1}}"
            
            # 计算条形
            bar_length = self._calculate_bar_length(
                point.value, max_value, available_width
            )
            bar = bar_char * bar_length
            
            # 颜色处理
            if point.color:
                bar = self._get_color(point.color, bar)
            
            # 数值
            if show_values:
                value_str = value_format.format(point.value)
                line = f"{label_line}│ {bar} {value_str}"
            else:
                line = f"{label_line}│ {bar}"
                
            lines.append(line)
        
        # 底部边框
        bottom_border = "└" + "─" * (self.width - 2) + "┘"
        lines.append(bottom_border)
        
        # 刻度
        scale_line = f"│ {' ' * label_width}│" + "0" + " " * (available_width - 2) + str(int(max_value))
        lines.append(scale_line)
        
        return "\n".join(lines)
    
    def generate_vertical_bar_chart(
        self,
        data: List[DataPoint],
        title: str = "",
        show_labels: bool = True,
        bar_char: str = "█"
    ) -> str:
        """
        生成垂直条形图
        
        Args:
            data: 数据点列表
            title: 图表标题
            show_labels: 是否显示标签
            bar_char: 条形字符
            
        Returns:
            ASCII图表字符串
        """
        if not data:
            return "No data provided."
            
        max_value = max(d.value for d in data)
        num_bars = len(data)
        
        if num_bars == 0:
            return "No data provided."
        
        # 计算每个条形的宽度
        chart_area_width = self.width - 4  # 留出边框
        bar_width = max(1, (chart_area_width // num_bars) - 1)
        spacing = max(1, (chart_area_width - bar_width * num_bars) // (num_bars + 1))
        
        # 构建网格
        grid = [[' ' for _ in range(self.width - 2)] for _ in range(self.height - 2)]
        
        # 填充数据
        for i, point in enumerate(data):
            bar_height = self._calculate_bar_height(
                point.value, max_value, self.height - 4
            )
            
            start_x = spacing + i * (bar_width + spacing)
            start_y = self.height - 4 - bar_height
            
            for y in range(bar_height):
                for x in range(bar_width):
                    if 0 <= start_y + y < self.height - 2 and 0 <= start_x + x < self.width - 2:
                        grid[start_y + y][start_x + x] = bar_char
        
        # 构建输出
        lines = []
        
        if title:
            padding = (self.width - len(title)) // 2
            lines.append(" " * padding + title + "\n")
        
        # 顶部边框
        lines.append("┌" + "─" * (self.width - 2) + "┐")
        
        # 图表区域
        for row in grid:
            line = "│" + "".join(row) + "│"
            if show_labels and len(data) <= self.width - 4:
                # 添加标签
                pass
            lines.append(line)
        
        # X轴
        lines.append("├" + "─" * (self.width - 2) + "┤")
        
        # 标签行
        label_line = "│"
        for i, point in enumerate(data):
            if i > 0:
                label_line += " "
            label = self._truncate_label(point.label, bar_width)
            label_line += label.center(bar_width)
        label_line += "│"
        lines.append(label_line)
        
        # 底部边框
        lines.append("└" + "─" * (self.width - 2) + "┘")
        
        # Y轴刻度
        lines.append(f"Max: {int(max_value)}")
        
        return "\n".join(lines)
    
    def generate_line_chart(
        self,
        data: List[Dict[str, Union[str, float]]],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        show_grid: bool = True
    ) -> str:
        """
        生成折线图
        
        Args:
            data: 数据点列表，每个点包含 'x', 'y', 可选的 'label' 和 'color'
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            show_grid: 是否显示网格
            
        Returns:
            ASCII图表字符串
        """
        if not data:
            return "No data provided."
            
        # 提取坐标
        x_values = [d['x'] for d in data]
        y_values = [d['y'] for d in data]
        
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        
        # 留出边距
        chart_width = self.width - 8
        chart_height = self.height - 6
        
        if chart_width <= 0 or chart_height <= 0:
            return "Chart dimensions too small."
        
        # 初始化网格
        grid = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]
        
        # 绘制网格(如果启用)
        if show_grid:
            for i in range(chart_height):
                grid[i][0] = self.LINE_CHARS['vertical']
            for j in range(chart_width):
                grid[chart_height - 1][j] = self.LINE_CHARS['horizontal']
        
        # 绘制折线
        for i in range(len(data) - 1):
            # 当前点到下一点的映射
            x1 = int((data[i]['x'] - min_x) / (max_x - min_x + 0.001) * (chart_width - 1))
            y1 = chart_height - 1 - int((data[i]['y'] - min_y) / (max_y - min_y + 0.001) * (chart_height - 1))
            x2 = int((data[i + 1]['x'] - min_x) / (max_x - min_x + 0.001) * (chart_width - 1))
            y2 = chart_height - 1 - int((data[i + 1]['y'] - min_y) / (max_y - min_y + 0.001) * (chart_height - 1))
            
            # 简单的Bresenham算法
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            
            while True:
                if 0 <= x1 < chart_width and 0 <= y1 < chart_height:
                    char = '●'
                    if data[i].get('color') and self.use_colors:
                        char = self._get_color(data[i]['color'], char)
                    grid[y1][x1] = char
                    
                if x1 == x2 and y1 == y2:
                    break
                    
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy
        
        # 构建输出
        lines = []
        
        if title:
            padding = (self.width - len(title)) // 2
            lines.append(" " * padding + title + "\n")
        
        # 顶部边框
        lines.append(self.LINE_CHARS['corner_tl'] + 
                     self.LINE_CHARS['line'] * (self.width - 2) + 
                     self.LINE_CHARS['corner_tr'])
        
        # Y轴标签
        if y_label:
            y_label = y_label[:self.height - 4]
            for i, char in enumerate(y_label):
                if i < self.height - 3:
                    line = self.LINE_CHARS['vertical'] + " " * (self.width - 4) + char
                    if i == 0:
                        line = self.LINE_CHARS['vertical'] + " " * (self.width - 4) + char
                    lines.append(line)
        
        # 图表区域
        for row in grid:
            line = self.LINE_CHARS['vertical'] + "".join(row) + self.LINE_CHARS['vertical']
            lines.append(line)
        
        # 底部边框
        lines.append(self.LINE_CHARS['corner_bl'] + 
                     self.LINE_CHARS['horizontal'] * (self.width - 2) + 
                     self.LINE_CHARS['corner_br'])
        
        # X轴标签
        if x_label:
            padding = self.width - len(x_label) - 2
            lines.append(" " * padding + x_label)
        
        return "\n".join(lines)
    
    def generate_stacked_bar_chart(
        self,
        series: List[DataSeries],
        labels: List[str],
        title: str = "",
        show_legend: bool = True
    ) -> str:
        """
        生成堆叠条形图
        
        Args:
            series: 数据系列列表
            labels: 分类标签
            title: 图表标题
            show_legend: 是否显示图例
            
        Returns:
            ASCII图表字符串
        """
        if not series or not labels:
            return "No data provided."
            
        num_categories = len(labels)
        max_total = sum(
            sum(point.value for point in s.data) 
            for s in series
        )
        
        label_width = max(len(l) for l in labels) + 2
        available_width = self.width - label_width - 10
        
        lines = []
        
        if title:
            padding = (self.width - len(title)) // 2
            lines.append(" " * padding + title + "\n")
        
        # 顶部边框
        lines.append("┌" + "─" * (self.width - 2) + "┐")
        
        # 颜色映射
        colors = ColorPalette.RAINBOW.value
        color_map = {s.name: colors[i % len(colors)] for i, s in enumerate(series)}
        
        # 数据行
        for j, label in enumerate(labels):
            truncated_label = self._truncate_label(label, label_width - 2)
            line = f"│ {truncated_label:<{label_width - 1}}│ "
            
            total_width = 0
            for s in series:
                if j < len(s.data):
                    value = s.data[j].value
                    if max_total > 0:
                        width = int(value / max_total * available_width)
                        bar = "█" * width
                        color = s.data[j].color or color_map.get(s.name)
                        if color:
                            bar = self._get_color(color, bar)
                        line += bar
                        total_width += width
            
            lines.append(line)
        
        # 底部边框
        lines.append("└" + "─" * (self.width - 2) + "┘")
        
        # 图例
        if show_legend:
            lines.append("")
            legend_line = "Legend: "
            for i, s in enumerate(series):
                color = colors[i % len(colors)]
                legend_item = f"■ {s.name} "
                if self.use_colors:
                    legend_item = self._get_color(color, legend_item)
                legend_line += legend_item
            lines.append(legend_line)
        
        return "\n".join(lines)
    
    def export_to_file(self, chart: str, filename: str) -> bool:
        """
        将图表导出到文件
        
        Args:
            chart: ASCII图表字符串
            filename: 输出文件名
            
        Returns:
            是否成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(chart)
                f.write('\n')
            return True
        except Exception as e:
            print(f"Error exporting to file: {e}")
            return False


def demo():
    """演示函数"""
    # 创建图表生成器
    generator = ASCIIGraphics(width=70, height=25)
    
    print("=" * 70)
    print("ASCII Chart Generator Demo 📊")
    print("=" * 70)
    print()
    
    # 示例1: 水平条形图 - 编程语言流行度
    print("1️⃣  Horizontal Bar Chart - Programming Language Popularity")
    print("-" * 70)
    
    languages = [
        DataPoint("Python", 92.5, "blue"),
        DataPoint("JavaScript", 88.2, "yellow"),
        DataPoint("Java", 76.3, "red"),
        DataPoint("TypeScript", 72.1, "cyan"),
        DataPoint("C++", 68.5, "green"),
        DataPoint("Go", 65.8, "magenta"),
        DataPoint("Rust", 58.3, "white"),
        DataPoint("Ruby", 45.2, "red"),
    ]
    
    chart = generator.generate_horizontal_bar_chart(
        languages,
        "📈 Programming Language Popularity (2026)",
        bar_char="█"
    )
    print(chart)
    print()
    
    # 示例2: 垂直条形图 - 月度销售额
    print("2️⃣  Vertical Bar Chart - Monthly Sales")
    print("-" * 70)
    
    months = [
        DataPoint("Jan", 45000),
        DataPoint("Feb", 52000),
        DataPoint("Mar", 48000),
        DataPoint("Apr", 61000),
        DataPoint("May", 55000),
        DataPoint("Jun", 67000),
        DataPoint("Jul", 72000),
        DataPoint("Aug", 69000),
        DataPoint("Sep", 75000),
        DataPoint("Oct", 82000),
        DataPoint("Nov", 88000),
        DataPoint("Dec", 95000),
    ]
    
    chart = generator.generate_vertical_bar_chart(
        months,
        "📊 Monthly Sales 2025 (CNY)",
        bar_char="📊"
    )
    print(chart)
    print()
    
    # 示例3: 折线图 - 股票价格走势
    print("3️⃣  Line Chart - Stock Price Trend")
    print("-" * 70)
    
    stock_data = [
        {'x': 1, 'y': 100, 'label': 'Jan'},
        {'x': 2, 'y': 120, 'label': 'Feb'},
        {'x': 3, 'y': 115, 'label': 'Mar'},
        {'x': 4, 'y': 130, 'label': 'Apr'},
        {'x': 5, 'y': 145, 'label': 'May'},
        {'x': 6, 'y': 140, 'label': 'Jun'},
        {'x': 7, 'y': 155, 'label': 'Jul'},
        {'x': 8, 'y': 165, 'label': 'Aug'},
        {'x': 9, 'y': 175, 'label': 'Sep'},
        {'x': 10, 'y': 170, 'label': 'Oct'},
    ]
    
    chart = generator.generate_line_chart(
        stock_data,
        "📈 Stock Price Trend 2025",
        "Month",
        "Price (CNY)"
    )
    print(chart)
    print()
    
    # 示例4: 堆叠条形图 - 各产品季度销售
    print("4️⃣  Stacked Bar Chart - Quarterly Sales by Product")
    print("-" * 70)
    
    product_a = DataSeries("Product A", [
        DataPoint("Q1", 15000),
        DataPoint("Q2", 18000),
        DataPoint("Q3", 22000),
        DataPoint("Q4", 25000),
    ])
    
    product_b = DataSeries("Product B", [
        DataPoint("Q1", 12000),
        DataPoint("Q2", 15000),
        DataPoint("Q3", 17000),
        DataPoint("Q4", 20000),
    ])
    
    product_c = DataSeries("Product C", [
        DataPoint("Q1", 8000),
        DataPoint("Q2", 10000),
        DataPoint("Q3", 12000),
        DataPoint("Q4", 15000),
    ])
    
    chart = generator.generate_stacked_bar_chart(
        [product_a, product_b, product_c],
        ["Q1", "Q2", "Q3", "Q4"],
        "📊 Quarterly Sales by Product",
        show_legend=True
    )
    print(chart)
    print()
    
    # 示例5: 导出到文件
    print("5️⃣  Export to File")
    print("-" * 70)
    
    if generator.export_to_file(chart, "stacked_bar_chart.txt"):
        print("✅ Chart exported to 'stacked_bar_chart.txt'")
    print()


def create_quick_chart():
    """快速创建图表的便捷函数"""
    generator = ASCIIGraphics(width=60, height=20)
    
    # 快速水平条形图
    data = [
        DataPoint("Task A", 85, "green"),
        DataPoint("Task B", 72, "yellow"),
        DataPoint("Task C", 95, "red"),
        DataPoint("Task D", 60, "cyan"),
    ]
    
    return generator.generate_horizontal_bar_chart(
        data,
        "Progress Overview"
    )


if __name__ == "__main__":
    # 检查参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo()
        elif sys.argv[1] == "--help":
            print("""
ASCII Chart Generator - 终端ASCII图表生成器
==============================================

使用方法:
    python ascii_chart_generator.py          # 运行演示
    python ascii_chart_generator.py --demo   # 运行完整演示
    python ascii_chart_generator.py --help   # 显示此帮助

功能:
    • 水平条形图 (Horizontal Bar Chart)
    • 垂直条形图 (Vertical Bar Chart)  
    • 折线图 (Line Chart)
    • 堆叠条形图 (Stacked Bar Chart)
    • 多数据对比
    • 颜色支持 (需安装 termcolor)
    • 导出到文件

示例:
    from ascii_chart_generator import ASCIIGraphics, DataPoint
    
    generator = ASCIIGraphics(width=60, height=20)
    data = [DataPoint("A", 100), DataPoint("B", 80)]
    chart = generator.generate_horizontal_bar_chart(data, "My Chart")
    print(chart)
""")
        else:
            print("Unknown argument. Use --help for usage information.")
    else:
        demo()
