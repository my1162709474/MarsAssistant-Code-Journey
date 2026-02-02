#!/usr/bin/env python3
"""
智能数据可视化工具
支持多种图表类型：折线图、柱状图、散点图、饼图、热力图等

功能特性:
- 智能数据类型检测
- 多种图表类型支持
- 交互式数据探索
- 图表自定义与美化
- 导出高质量图片

使用方式:
1. 命令行模式: python smart_data_visualizer.py data.csv
2. 交互模式: python smart_data_visualizer.py --interactive
3. 脚本模式: from smart_data_visualizer import SmartVisualizer

作者: MarsAssistant
日期: 2026-02-02
"""

import json
import csv
import sys
import argparse
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random


class ChartType(Enum):
    """图表类型枚举"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box"
    HEATMAP = "heatmap"
    RADAR = "radar"
    AREA = "area"


class DataType(Enum):
    """数据类型枚举"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    MIXED = "mixed"


@dataclass
class DataColumn:
    """数据列信息"""
    name: str
    data_type: DataType
    values: List[Any]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unique_values: Optional[List[Any]] = None


class SmartDataVisualizer:
    """智能数据可视化工具"""
    
    # ANSI 颜色代码
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
    }
    
    def __init__(self, data: Dict[str, List[Any]] = None):
        """初始化可视化器"""
        self.data = data or {}
        self.columns: Dict[str, DataColumn] = {}
        self.chart_configs = {
            ChartType.LINE: {
                'title': '折线图',
                'description': '展示数据随时间或有序变化的趋势',
                'best_for': ['时间序列', '趋势分析', '连续数据'],
                'x_axis': '自变量（时间/顺序）',
                'y_axis': '因变量（数值）',
            },
            ChartType.BAR: {
                'title': '柱状图',
                'description': '比较不同类别或组的数值大小',
                'best_for': ['类别比较', '频率统计', '排名分析'],
                'x_axis': '类别标签',
                'y_axis': '数值大小',
            },
            ChartType.SCATTER: {
                'title': '散点图',
                'description': '展示两个变量之间的相关性和分布',
                'best_for': ['相关性分析', '分布查看', '异常检测'],
                'x_axis': '第一个变量',
                'y_axis': '第二个变量',
            },
            ChartType.PIE: {
                'title': '饼图',
                'description': '展示各部分占整体的比例关系',
                'best_for': ['占比分析', '比例展示', '构成分析'],
                'x_axis': '比例',
                'y_axis': '类别',
            },
            ChartType.HISTOGRAM: {
                'title': '直方图',
                'description': '展示数据的分布频率',
                'best_for': ['分布分析', '频率统计', '数据概览'],
                'x_axis': '数值区间',
                'y_axis': '频数/频率',
            },
            ChartType.HEATMAP: {
                'title': '热力图',
                'description': '用颜色编码展示矩阵数据的强度',
                'best_for': ['相关性矩阵', '密度分布', '模式识别'],
                'x_axis': '第二个维度',
                'y_axis': '第一个维度',
            },
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """添加颜色"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def load_csv(self, filepath: str) -> bool:
        """从CSV文件加载数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                
                # 初始化列数据
                for header in headers:
                    self.columns[header] = DataColumn(
                        name=header,
                        data_type=DataType.MIXED,
                        values=[]
                    )
                    self.data[header] = []
                
                # 读取所有行
                for row in reader:
                    for header in headers:
                        value = row.get(header, '')
                        self.data[header].append(value)
                        self.columns[header].values.append(value)
            
            # 分析数据类型
            self._analyze_data_types()
            return True
        except Exception as e:
            print(f"加载CSV文件失败: {e}")
            return False
    
    def load_json(self, filepath: str) -> bool:
        """从JSON文件加载数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 处理嵌套结构
            if isinstance(raw_data, list):
                if len(raw_data) > 0 and isinstance(raw_data[0], dict):
                    # 列表字典
                    for key in raw_data[0].keys():
                        self.data[key] = [item.get(key, '') for item in raw_data]
            elif isinstance(raw_data, dict):
                # 单个对象
                for key, value in raw_data.items():
                    if isinstance(value, list):
                        self.data[key] = value
                    else:
                        self.data[key] = [value]
            
            # 分析数据类型
            self._analyze_data_types()
            return True
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return False
    
    def load_dict(self, data: Dict[str, List[Any]]):
        """从字典加载数据"""
        self.data = data.copy()
        self._analyze_data_types()
    
    def _analyze_data_types(self):
        """分析所有列的数据类型"""
        for column_name, values in self.data.items():
            if not values:
                continue
            
            # 检测数据类型
            numeric_count = 0
            temporal_count = 0
            
            for value in values:
                if isinstance(value, (int, float)):
                    numeric_count += 1
                elif isinstance(value, str):
                    # 检查是否为数值
                    try:
                        float(value)
                        numeric_count += 1
                    except ValueError:
                        pass
                    
                    # 检查是否为日期
                    temporal_keywords = ['-', '/', ':', '年', '月', '日']
                    if any(kw in value for kw in temporal_keywords):
                        temporal_count += 1
            
            total = len(values)
            
            if numeric_count / total > 0.8:
                data_type = DataType.NUMERIC
            elif temporal_count / total > 0.8:
                data_type = DataType.TEMPORAL
            else:
                data_type = DataType.CATEGORICAL
            
            # 计算统计信息
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass
            
            unique_vals = list(set(values))[:20]  # 保留前20个唯一值
            
            self.columns[column_name] = DataColumn(
                name=column_name,
                data_type=data_type,
                values=values,
                min_value=min(numeric_values) if numeric_values else None,
                max_value=max(numeric_values) if numeric_values else None,
                unique_values=unique_vals,
            )
    
    def get_numeric_columns(self) -> List[str]:
        """获取所有数值型列名"""
        return [name for name, col in self.columns.items() 
                if col.data_type == DataType.NUMERIC]
    
    def get_categorical_columns(self) -> List[str]:
        """获取所有分类型列名"""
        return [name for name, col in self.columns.items() 
                if col.data_type == DataType.CATEGORICAL]
    
    def suggest_chart_types(self, x_col: str = None, y_cols: List[str] = None) -> List[ChartType]:
        """根据数据类型推荐合适的图表类型"""
        suggestions = []
        
        x_data = self.columns.get(x_col) if x_col else None
        y_data = [self.columns.get(y) for y in (y_cols or [])]
        
        # 如果有多个数值列，推荐散点图
        numeric_cols = self.get_numeric_columns()
        if len(numeric_cols) >= 2:
            suggestions.extend([ChartType.SCATTER, ChartType.LINE, ChartType.BAR])
        
        # 如果有分类列，推荐柱状图或饼图
        cat_cols = self.get_categorical_columns()
        if cat_cols and numeric_cols:
            suggestions.extend([ChartType.BAR, ChartType.PIE])
        
        # 如果只有数值列，推荐直方图或箱线图
        if not cat_cols and numeric_cols:
            suggestions.extend([ChartType.HISTOGRAM, ChartType.BOX_PLOT])
        
        # 默认推荐
        suggestions.extend([ChartType.LINE, ChartType.BAR])
        
        return list(set(suggestions))
    
    def print_data_info(self):
        """打印数据信息摘要"""
        print(f"\n{self._colorize('📊 数据摘要', 'bold')}")
        print("=" * 60)
        print(f"{self._colorize('数据行数:', 'cyan')} {len(list(self.data.values())[0]) if self.data else 0}")
        print(f"{self._colorize('数据列数:', 'cyan')} {len(self.data)}")
        print(f"\n{self._colorize('📋 列信息:', 'bold')}")
        print("-" * 60)
        
        for col_name, col in self.columns.items():
            type_icon = {
                DataType.NUMERIC: '📈',
                DataType.CATEGORICAL: '🏷️',
                DataType.TEMPORAL: '📅',
            }.get(col.data_type, '📄')
            
            print(f"{type_icon} {col_name} ({col.data_type.value})")
            
            if col.data_type == DataType.NUMERIC:
                if col.min_value is not None and col.max_value is not None:
                    print(f"   范围: [{col.min_value:.2f}, {col.max_value:.2f}]")
            else:
                unique_count = len(set(col.values))
                print(f"   唯一值数量: {unique_count}")
    
    def generate_chart_code(self, chart_type: ChartType, 
                          x_col: str, y_cols: List[str],
                          title: str = None,
                          show_legend: bool = True) -> str:
        """生成图表代码（使用matplotlib）"""
        chart_config = self.chart_configs.get(chart_type, {})
        
        code = f'''#!/usr/bin/env python3
"""
{chart_config.get('title', '图表')}
自动生成的可视化代码

使用说明:
- 确保已安装必要库: pip install matplotlib numpy pandas
- 运行脚本生成图表
"""

import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据
x = {self.data.get(x_col, [])}
y_data = {{
'''
        
        for y_col in y_cols:
            code += f"    '{y_col}': {self.data.get(y_col, [])},\n"
        
        code += f'''}}

# 创建图表
fig, ax = plt.subplots(figsize=(12, 8))

'''
        
        if chart_type == ChartType.BAR:
            code += f'''# 柱状图
x_labels = [str(v) for v in x]
x_pos = np.arange(len(x_labels))
width = 0.35

colors = plt.cm.Set3(np.linspace(0, 1, len(y_cols)))
for i, (y_col, color) in enumerate(zip(y_cols, colors)):
    bars = ax.bar(x_pos + i * width, y_data[y_col], width, 
                  label=y_col, color=color, edgecolor='white', linewidth=0.5)

ax.set_xlabel('{x_col}', fontsize=12)
ax.set_ylabel('数值', fontsize=12)
ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
ax.set_xticks(x_pos + width / 2 * (len(y_cols) - 1))
ax.set_xticklabels(x_labels, rotation=45, ha='right')
'''
        elif chart_type == ChartType.LINE:
            code += f'''# 折线图
colors = plt.cm.tab10(np.linspace(0, 1, len(y_cols)))
for i, (y_col, color) in enumerate(zip(y_cols, colors)):
    ax.plot(x, y_data[y_col], marker='o', markersize=4, 
            label=y_col, color=color, linewidth=2, alpha=0.8)

ax.set_xlabel('{x_col}', fontsize=12)
ax.set_ylabel('数值', fontsize=12)
ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
'''
        elif chart_type == ChartType.SCATTER:
            code += f'''# 散点图
if len(y_cols) >= 2:
    scatter = ax.scatter(y_data[y_cols[0]], y_data[y_cols[1]], 
                        c=range(len(x)), cmap='viridis', 
                        alpha=0.7, s=100, edgecolors='white', linewidth=0.5)
    ax.set_xlabel(y_cols[0], fontsize=12)
    ax.set_ylabel(y_cols[1], fontsize=12)
    ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('索引', fontsize=10)
'''
        elif chart_type == ChartType.PIE:
            code += f'''# 饼图
if len(y_cols) >= 1:
    values = y_data[y_cols[0]]
    labels = [str(v) for v in x[:len(values)]]
    
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(values)))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                      colors=colors, explode=[0.02] * len(values),
                                      shadow=True, startangle=90)
    ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
'''
        elif chart_type == ChartType.HISTOGRAM:
            code += f'''# 直方图
for i, y_col in enumerate(y_cols):
    ax.hist(y_data[y_col], bins=20, alpha=0.6, label=y_col, 
            color=plt.cm.Set2(i / len(y_cols)), edgecolor='white')

ax.set_xlabel('数值区间', fontsize=12)
ax.set_ylabel('频数', fontsize=12)
ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
'''
        else:
            # 默认折线图
            code += f'''# 默认折线图
for y_col in y_cols:
    ax.plot(x, y_data[y_col], marker='o', markersize=4, label=y_col, linewidth=2)

ax.set_xlabel('{x_col}', fontsize=12)
ax.set_ylabel('数值', fontsize=12)
ax.set_title('{title or chart_config.get("title")}', fontsize=14, fontweight='bold')
'''
        
        if show_legend and chart_type != ChartType.PIE:
            code += f'''
ax.legend(loc='upper right', fontsize=10)
'''
        
        code += '''
ax.grid(True, alpha=0.3, linestyle='--')

# 调整布局
plt.tight_layout()

# 保存图表
output_file = 'chart_output.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
print(f"图表已保存至: {{output_file}}")

# 显示图表
plt.show()
'''
        
        return code
    
    def interactive_mode(self):
        """交互式可视化模式"""
        print(f"\n{self._colorize('🎨 智能数据可视化工具', 'bold')}")
        print(f"{self._colorize('=' * 60, 'green')}\n")
        
        # 加载数据
        if not self.data:
            print("请先加载数据文件！")
            return
        
        self.print_data_info()
        
        while True:
            print(f"\n{self._colorize('📊 可视化选项:', 'bold')}")
            print("1. 查看数据信息")
            print("2. 推荐图表类型")
            print("3. 生成图表代码")
            print("4. 退出")
            
            choice = input(f"\n{self._colorize('请选择操作 (1-4): ', 'cyan')}")
            
            if choice == '1':
                self.print_data_info()
            elif choice == '2':
                print(f"\n{self._colorize('💡 推荐图表类型:', 'bold')}")
                suggestions = self.suggest_chart_types()
                for i, chart in enumerate(suggestions, 1):
                    config = self.chart_configs.get(chart, {})
                    print(f"{i}. {config.get('title', chart.value)} - {config.get('description', '')}")
            elif choice == '3':
                print(f"\n{self._colorize('🎯 生成图表代码:', 'bold')}")
                x_col = input(f"请输入X轴列名: ")
                y_cols_input = input(f"请输入Y轴列名（多个用逗号分隔）: ")
                y_cols = [y.strip() for y in y_cols_input.split(',')]
                
                chart_type = input(f"请输入图表类型 ({', '.join([c.value for c in ChartType])}): ")
                
                try:
                    selected_type = ChartType(chart_type)
                    code = self.generate_chart_code(selected_type, x_col, y_cols)
                    
                    output_file = f"chart_{x_col}_vs_{'_'.join(y_cols)}.py"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(code)
                    
                    print(f"\n{self._colorize(f'✅ 图表代码已生成: {output_file}', 'green')}")
                    print(f"{self._colorize('运行命令: ', 'cyan')}python {output_file}")
                except ValueError:
                    print(f"{self._colorize('❌ 无效的图表类型', 'red')}")
            elif choice == '4':
                print(f"\n{self._colorize('👋 再见！', 'green')}")
                break
            else:
                print(f"{self._colorize('❌ 无效选择', 'red')}")


def generate_sample_data() -> Dict[str, List[Any]]:
    """生成示例数据用于演示"""
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    categories = ['产品A', '产品B', '产品C', '产品D']
    
    return {
        '月份': months * 10,
        '产品': [cat for cat in categories for _ in range(6)] * 10 // 4,
        '销售额': [random.randint(1000, 5000) for _ in range(60)],
        '利润': [random.randint(100, 1000) for _ in range(60)],
        '增长率': [random.uniform(-10, 30) for _ in range(60)],
        '客户数': [random.randint(50, 500) for _ in range(60)],
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能数据可视化工具 - 支持多种图表类型和自动代码生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s data.csv              # 从CSV文件加载并显示数据信息
  %(prog)s data.json             # 从JSON文件加载
  %(prog)s --interactive         # 交互式模式
  %(prog)s --demo                # 使用示例数据演示
  %(prog)s data.csv --generate   # 生成示例图表代码
        '''
    )
    
    parser.add_argument('file', nargs='?', help='数据文件路径 (CSV/JSON)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='启动交互式模式')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='使用示例数据演示')
    parser.add_argument('--generate', '-g', action='store_true',
                        help='生成示例图表代码')
    parser.add_argument('--output', '-o', default='chart_output.py',
                        help='输出文件路径 (默认: chart_output.py)')
    
    args = parser.parse_args()
    
    # 创建可视化器
    visualizer = SmartDataVisualizer()
    
    if args.demo:
        # 使用示例数据
        sample_data = generate_sample_data()
        visualizer.load_dict(sample_data)
        print(f"\n{visualizer._colorize('📊 已加载示例数据', 'green')}")
        visualizer.print_data_info()
        
        if args.generate:
            code = visualizer.generate_chart_code(
                ChartType.LINE,
                '月份',
                ['销售额', '利润'],
                title='月度销售趋势'
            )
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"\n{visualizer._colorize(f'✅ 图表代码已生成: {args.output}', 'green')}")
    
    elif args.file:
        # 加载数据文件
        if args.file.endswith('.csv'):
            success = visualizer.load_csv(args.file)
        elif args.file.endswith('.json'):
            success = visualizer.load_json(args.file)
        else:
            print(f"{visualizer._colorize('❌ 不支持的文件格式', 'red')}")
            success = False
        
        if success:
            visualizer.print_data_info()
            
            if args.generate:
                code = visualizer.generate_chart_code(
                    ChartType.LINE,
                    visualizer.get_numeric_columns()[0] if visualizer.get_numeric_columns() else 'col1',
                    visualizer.get_numeric_columns()[:2] if len(visualizer.get_numeric_columns()) >= 2 else ['value'],
                )
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(code)
                print(f"\n{visualizer._colorize(f'✅ 图表代码已生成: {args.output}', 'green')}")
    
    elif args.interactive:
        # 交互式模式
        visualizer.load_dict(generate_sample_data())
        visualizer.interactive_mode()
    
    else:
        # 默认显示帮助信息
        parser.print_help()
        print(f"\n{visualizer._colorize('💡 提示: 使用 --demo 尝试示例数据', 'yellow')}")


if __name__ == '__main__':
    main()
