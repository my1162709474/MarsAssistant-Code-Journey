#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII图表生成器 - 终端数据可视化工具
支持条形图、折线图、面积图、饼图等多种图表类型
"""

import math
import sys
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ChartType(Enum):
    """图表类型枚举"""
    BAR = "bar"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    HORIZONTAL_BAR = "hbar"
    SCATTER = "scatter"


class AlignType(Enum):
    """对齐方式枚举"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class DataPoint:
    """数据点"""
    label: str
    value: float
    color: Optional[str] = None


@dataclass
class ChartStyle:
    """图表样式配置"""
    width: int = 60
    height: int = 15
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    bar_char: str = "█"
    line_char: str = "●"
    fill_char: str = "░"
    grid_char: str = "│"
    axis_char: str = "┼"
    corner_char: str = "┼"
    show_values: bool = True
    value_position: str = "top"  # top, inside, none
    colors: bool = False
    show_grid: bool = True
    y_min: Optional[float] = None
    y_max: Optional[float] = None


class ASCIIColor:
    """ANSI颜色码"""
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 亮色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    @classmethod
    def get_color(cls, index: int) -> str:
        """根据索引获取颜色"""
        colors = [
            cls.CYAN, cls.GREEN, cls.YELLOW, cls.MAGENTA,
            cls.RED, cls.BLUE, cls.BRIGHT_CYAN, cls.BRIGHT_GREEN
        ]
        return colors[index % len(colors)]


class ASCIITerminalChart:
    """ASCII终端图表生成器"""
    
    # 饼图字符（从12点钟方向开始，顺时针）
    PIE_CHARS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    
    def __init__(self, style: Optional[ChartStyle] = None):
        self.style = style or ChartStyle()
    
    def _calculate_y_range(self, data: List[DataPoint]) -> tuple:
        """计算Y轴范围"""
        values = [d.value for d in data]
        y_min = self.style.y_min if self.style.y_min is not None else min(values)
        y_max = self.style.y_max if self.style.y_max is not None else max(values)
        
        # 添加一些边距
        range_val = y_max - y_min
        if range_val == 0:
            y_max = y_min + 1
        else:
            y_max += range_val * 0.1
            y_min -= range_val * 0.05
            y_min = max(0, y_min)
        
        return y_min, y_max
    
    def _normalize_value(self, value: float, y_min: float, y_max: float) -> float:
        """归一化值到[0, 1]"""
        if y_max == y_min:
            return 0.5
        return (value - y_min) / (y_max - y_min)
    
    def _get_bar_chars(self, height: int) -> List[str]:
        """获取条形图字符序列（从下到上）"""
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        return chars[:height] if height <= len(chars) else chars
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """自动换行文本"""
        if len(text) <= width:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text[:width]]
    
    def _format_value(self, value: float) -> str:
        """格式化数值"""
        if abs(value) >= 1e9:
            return f"{value/1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.1f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.1f}K"
        elif abs(value) >= 1:
            return f"{value:.1f}"
        else:
            return f"{value:.2f}"
    
    def generate_bar_chart(self, data: List[DataPoint]) -> str:
        """生成条形图"""
        if not data:
            return "No data provided"
        
        y_min, y_max = self._calculate_y_range(data)
        chart_width = self.style.width - 12  # 留出标签空间
        chart_height = self.style.height
        
        # 计算每个数据点的条形宽度
        num_bars = len(data)
        if num_bars == 0:
            return "No data"
        
        bar_width = max(1, chart_width // num_bars - 1)
        spacing = max(0, chart_width - num_bars * (bar_width + 1))
        
        lines = []
        
        # 标题
        if self.style.title:
            title_lines = self._wrap_text(self.style.title, self.style.width)
            for line in title_lines:
                lines.append(line.center(self.style.width))
            lines.append("")
        
        # Y轴标签
        y_label = self.style.y_label
        if y_label:
            for i, char in enumerate(y_label):
                if i < chart_height:
                    lines.append(f"  {char}{' ' * 9}")
        
        # 生成图表
        for row in range(chart_height, 0, -1):
            line = ""
            row_normalized = (row - 0.5) / chart_height
            
            for i, point in enumerate(data):
                point_normalized = self._normalize_value(point.value, y_min, y_max)
                bar_chars = self._get_bar_chars(8)
                char_index = min(int(point_normalized * len(bar_chars)), len(bar_chars) - 1)
                
                if point_normalized >= row_normalized:
                    if self.style.colors:
                        color = point.color or ASCIIColor.get_color(i)
                        line += f"{color}{bar_chars[char_index] * bar_width}{ASCIIColor.RESET}"
                    else:
                        line += bar_chars[char_index] * bar_width
                else:
                    line += " " * bar_width
                
                if i < num_bars - 1:
                    line += " "
            
            # Y轴刻度
            y_value = y_min + (y_max - y_min) * (row - 1) / (chart_height - 1)
            y_tick = f"{self._format_value(y_value):>8} "
            lines.append(y_tick + line)
        
        # X轴
        x_axis = " " * 9 + " " + "─" * (chart_width + num_bars - 1)
        lines.append(x_axis)
        
        # X轴标签（每两个显示一个避免拥挤）
        x_labels = ""
        for i, point in enumerate(data):
            label = point.label[:bar_width-1]
            if i % 2 == 0:
                x_labels += f" {label:<{bar_width}}"
            else:
                x_labels += f" {' ' * (bar_width)}"
        lines.append(" " * 9 + " " + x_labels)
        
        return "\n".join(lines)
    
    def generate_line_chart(self, data: List[DataPoint]) -> str:
        """生成折线图"""
        if len(data) < 2:
            return self.generate_bar_chart(data)
        
        y_min, y_max = self._calculate_y_range(data)
        chart_width = self.style.width - 12
        chart_height = self.style.height
        
        lines = []
        
        # 标题
        if self.style.title:
            title_lines = self._wrap_text(self.style.title, self.style.width)
            for line in title_lines:
                lines.append(line.center(self.style.width))
            lines.append("")
        
        # Y轴标签
        y_label = self.style.y_label
        if y_label:
            for i, char in enumerate(y_label):
                if i < chart_height:
                    lines.append(f"  {char}{' ' * 9}")
        
        # 初始化网格
        grid = [[" " for _ in range(chart_width)] for _ in range(chart_height)]
        
        # 计算数据点位置并绘制连线
        for i in range(len(data) - 1):
            x1 = int(i * (chart_width - 1) / (len(data) - 1))
            x2 = int((i + 1) * (chart_width - 1) / (len(data) - 1))
            y1 = int(self._normalize_value(data[i].value, y_min, y_max) * (chart_height - 1))
            y2 = int(self._normalize_value(data[i + 1].value, y_min, y_max) * (chart_height - 1))
            y1 = chart_height - 1 - y1
            y2 = chart_height - 1 - y2
            
            # 绘制线段
            if x1 == x2:
                grid[min(y1, y2)][x1] = "│"
            elif y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    grid[y1][x] = "─"
            else:
                steps = max(abs(x2 - x1), abs(y2 - y1))
                for step in range(steps + 1):
                    x = x1 + (x2 - x1) * step // steps
                    y = y1 + (y2 - y1) * step // steps
                    if 0 <= x < chart_width and 0 <= y < chart_height:
                        grid[y][x] = "●"
        
        # 绘制数据点
        for i, point in enumerate(data):
            x = int(i * (chart_width - 1) / (len(data) - 1))
            y = int(self._normalize_value(point.value, y_min, y_max) * (chart_height - 1))
            y = chart_height - 1 - y
            if 0 <= y < chart_height and 0 <= x < chart_width:
                if self.style.colors:
                    color = point.color or ASCIIColor.CYAN
                    grid[y][x] = f"{color}●{ASCIIColor.RESET}"
                else:
                    grid[y][x] = "●"
        
        # 生成图表行
        for row in range(chart_height):
            y_value = y_min + (y_max - y_min) * (chart_height - 1 - row) / (chart_height - 1)
            y_tick = f"{self._format_value(y_value):>8} "
            line = y_tick + "│" + "".join(grid[row])
            lines.append(line)
        
        # X轴
        x_axis = " " * 9 + "└" + "─" * chart_width + "┘"
        lines.append(x_axis)
        
        # X轴标签
        x_labels = ""
        step = max(1, len(data) // 5)
        for i in range(0, len(data), step):
            label = data[i].label[:8]
            x = int(i * (chart_width - 1) / max(1, len(data) - 1))
            x_labels += f"{' ' * x}{label:^8}"
        lines.append(" " * 10 + x_labels)
        
        return "\n".join(lines)
    
    def generate_area_chart(self, data: List[DataPoint]) -> str:
        """生成面积图"""
        if len(data) < 2:
            return self.generate_bar_chart(data)
        
        y_min, y_max = self._calculate_y_range(data)
        chart_width = self.style.width - 12
        chart_height = self.style.height
        
        lines = []
        
        # 标题
        if self.style.title:
            title_lines = self._wrap_text(self.style.title, self.style.width)
            for line in title_lines:
                lines.append(line.center(self.style.width))
            lines.append("")
        
        # 初始化网格
        grid = [[" " for _ in range(chart_width)] for _ in range(chart_height)]
        
        # 填充面积
        for i, point in enumerate(data):
            x = int(i * (chart_width - 1) / (len(data) - 1))
            y = int(self._normalize_value(point.value, y_min, y_max) * (chart_height - 1))
            y = chart_height - 1 - y
            
            for row in range(y, chart_height):
                fill_char = "▒" if row < chart_height - 1 else "─"
                if self.style.colors:
                    color = point.color or ASCIIColor.get_color(i)
                    grid[row][x] = f"{color}{fill_char}{ASCIIColor.RESET}"
                else:
                    grid[row][x] = fill_char
        
        # 绘制顶部线
        for i in range(len(data) - 1):
            x1 = int(i * (chart_width - 1) / (len(data) - 1))
            x2 = int((i + 1) * (chart_width - 1) / (len(data) - 1))
            y1 = int(self._normalize_value(data[i].value, y_min, y_max) * (chart_height - 1))
            y1 = chart_height - 1 - y1
            y2 = int(self._normalize_value(data[i + 1].value, y_min, y_max) * (chart_height - 1))
            y2 = chart_height - 1 - y2
            
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < chart_width:
                    grid[min(y1, y2)][x] = "●"
        
        # 生成图表行
        for row in range(chart_height):
            y_value = y_min + (y_max - y_min) * (chart_height - 1 - row) / (chart_height - 1)
            y_tick = f"{self._format_value(y_value):>8} "
            line = y_tick + "│" + "".join(grid[row])
            lines.append(line)
        
        # X轴
        x_axis = " " * 9 + "└" + "─" * chart_width + "┘"
        lines.append(x_axis)
        
        return "\n".join(lines)
    
    def generate_pie_chart(self, data: List[DataPoint]) -> str:
        """生成饼图（ASCII艺术风格）"""
        if not data:
            return "No data provided"
        
        total = sum(d.value for d in data)
        if total == 0:
            return "Total value is zero"
        
        lines = []
        
        # 标题
        if self.style.title:
            title_lines = self._wrap_text(self.style.title, self.style.width)
            for line in title_lines:
                lines.append(line.center(self.style.width))
            lines.append("")
        
        # 计算每个扇区
        sectors = []
        for i, point in enumerate(data):
            percentage = point.value / total
            sectors.append({
                "label": point.label,
                "value": point.value,
                "percentage": percentage,
                "color": point.color or ASCIIColor.get_color(i)
            })
        
        # 绘制饼图（使用字符表示）
        radius = min(10, self.style.width // 4)
        
        for row in range(radius * 2 + 1):
            line = ""
            for col in range(radius * 2 + 1):
                dx = col - radius
                dy = row - radius
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= radius:
                    angle = math.atan2(dy, dx)  # -π 到 π
                    if angle < 0:
                        angle += 2 * math.pi  # 0 到 2π
                    
                    # 计算当前角度对应的扇区
                    accumulated = 0
                    char = " "
                    for sector in sectors:
                        accumulated += sector["percentage"]
                        if angle < accumulated * 2 * math.pi:
                            if self.style.colors:
                                char = f"{sector['color']}●{ASCIIColor.RESET}"
                            else:
                                char = "●"
                            break
                    
                    line += char if distance <= radius else " "
                else:
                    line += " "
            
            lines.append(line.center(self.style.width))
        
        lines.append("")
        
        # 图例
        legend_width = self.style.width - 4
        lines.append("─" * min(legend_width, len(sectors) * 20))
        
        for i, sector in enumerate(sectors):
            color_code = sector['color'] if self.style.colors else ""
            reset = ASCIIColor.RESET if self.style.colors else ""
            percentage = sector['percentage'] * 100
            label = sector['label'][:12]
            value = self._format_value(sector['value'])
            legend_line = f"  {color_code}■{reset} {label:<12} {value:>8} ({percentage:5.1f}%)"
            lines.append(legend_line)
        
        lines.append("─" * min(legend_width, len(sectors) * 20))
        
        return "\n".join(lines)
    
    def generate_horizontal_bar(self, data: List[DataPoint]) -> str:
        """生成水平条形图"""
        if not data:
            return "No data provided"
        
        y_min, y_max = self._calculate_y_range(data)
        
        lines = []
        
        # 标题
        if self.style.title:
            title_lines = self._wrap_text(self.style.title, self.style.width)
            for line in title_lines:
                lines.append(line.center(self.style.width))
            lines.append("")
        
        # 找出最长标签
        max_label_len = max(len(d.label) for d in data)
        max_label_len = min(max_label_len, 15)
        
        chart_width = self.style.width - max_label_len - 15
        
        for point in data:
            normalized = self._normalize_value(point.value, y_max, y_min)
            bar_len = int(normalized * chart_width)
            percentage = (point.value / y_max) * 100 if y_max != 0 else 0
            
            if self.style.colors:
                color = point.color or ASCIIColor.get_color(data.index(point))
                bar = f"{color}{'█' * bar_len}{ASCIIColor.RESET}"
            else:
                bar = "█" * bar_len
            
            label = point.label[:max_label_len].ljust(max_label_len)
            value = self._format_value(point.value)
            
            line = f"{label} │{bar} {value} ({percentage:5.1f}%)"
            lines.append(line)
        
        return "\n".(lines)
    
    def generate(self, data: List[DataPoint], chart_type: Optional[ChartType] = None) -> str:
        """生成图表的通用方法"""
        chart_type = chart_type or ChartType.BAR
        
        generators = {
            ChartType.BAR: self.generate_bar_chart,
            ChartType.LINE: self.generate_line_chart,
            ChartType.AREA: self.generate_area_chart,
            ChartType.PIE: self.generate_pie_chart,
            ChartType.HORIZONTAL_BAR: self.generate_horizontal_bar,
        }
        
        generator = generators.get(chart_type, self.generate_bar_chart)
        return generator(data)
    
    def demo(self):
        """展示各种图表"""
        print("=" * self.style.width)
        print("ASCII 图表生成器演示")
        print("=" * self.style.width)
        print()
        
        # 示例数据
        sales_data = [
            DataPoint("Jan", 12000),
            DataPoint("Feb", 15000),
            DataPoint("Mar", 11000),
            DataPoint("Apr", 18000),
            DataPoint("May", 22000),
            DataPoint("Jun", 19000),
        ]
        
        # 带颜色的数据
        colored_data = [
            DataPoint("A", 85, ASCIIColor.RED),
            DataPoint("B", 42, ASCIIColor.GREEN),
            DataPoint("C", 67, ASCIIColor.YELLOW),
            DataPoint("D", 95, ASCIIColor.CYAN),
            DataPoint("E", 53, ASCIIColor.MAGENTA),
        ]
        
        # 饼图数据
        market_data = [
            DataPoint("Product A", 35),
            DataPoint("Product B", 25),
            DataPoint("Product C", 20),
            DataPoint("Product D", 12),
            DataPoint("Other", 8),
        ]
        
        print("📊 垂直条形图（销售数据）:")
        print("-" * self.style.width)
        chart = ASCIITerminalChart(ChartStyle(title="Monthly Sales 2024"))
        print(chart.generate(sales_data, ChartType.BAR))
        print()
        
        print("📈 折线图（带颜色）:")
        print("-" * self.style.width)
        chart = ASCIITerminalChart(ChartStyle(title="Multi-Color Data", colors=True))
        print(chart.generate(colored_data, ChartType.LINE))
        print()
        
        print("🎂 饼图（市场份额）:")
        print("-" * self.style.width)
        chart = ASCIITerminalChart(ChartStyle(title="Market Share"))
        print(chart.generate(market_data, ChartType.PIE))
        print()
        
        print("📊 面积图:")
        print("-" * self.style.width)
        chart = ASCIITerminalChart(ChartStyle(title="Area Chart Demo"))
        print(chart.generate(sales_data, ChartType.AREA))
        print()
        
        print("📊 水平条形图:")
        print("-" * self.style.width)
        chart = ASCIITerminalChart(ChartStyle(title="Horizontal Bar Chart", width=50))
        print(chart.generate(colored_data, ChartType.HORIZONTAL_BAR))
        print()


def main():
    """主函数 - 演示图表生成器"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ASCII图表生成器 - 终端数据可视化工具"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["bar", "line", "area", "pie", "hbar"],
        default="bar",
        help="图表类型 (默认: bar)"
    )
    parser.add_argument(
        "--title", "-T",
        default="My Chart",
        help="图表标题"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=60,
        help="图表宽度 (默认: 60)"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        default=15,
        help="图表高度 (默认: 15)"
    )
    parser.add_argument(
        "--colors", "-c",
        action="store_true",
        help="启用颜色"
    )
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="运行演示"
    )
    parser.add_argument(
        "--data",
        nargs="+",
        help="数据点，格式: label:value"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        chart = ASCIITerminalChart()
        chart.demo()
        return
    
    if args.data:
        data_points = []
        for item in args.data:
            if ":" in item:
                label, value = item.rsplit(":", 1)
                try:
                    value = float(value)
                    data_points.append(DataPoint(label, value))
                except ValueError:
                    print(f"错误: 无效的数据格式 '{item}'，请使用 label:value 格式")
                    sys.exit(1)
        
        if not data_points:
            print("错误: 没有有效的数据点")
            sys.exit(1)
        
        style = ChartStyle(
            title=args.title,
            width=args.width,
            height=args.height,
            colors=args.colors
        )
        
        chart_type_map = {
            "bar": ChartType.BAR,
            "line": ChartType.LINE,
            "area": ChartType.AREA,
            "pie": ChartType.PIE,
            "hbar": ChartType.HORIZONTAL_BAR,
        }
        
        chart = ASCIITerminalChart(style)
        result = chart.generate(data_points, chart_type_map[args.type])
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
