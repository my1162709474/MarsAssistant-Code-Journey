#!/usr/bin/env python3
"""
智能数据可视化工具 - Day 52
支持多种图表类型、自动图表选择、数据统计分析

功能特性:
- 📊 自动图表类型推荐
- 📈 多种图表支持: 折线图/柱状图/散点图/饼图/热力图/箱线图
- 🔍 数据统计分析
- 🎨 智能配色方案
- 📁 多格式导出: PNG/SVG/HTML
"""

import json
import base64
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
import tempfile
import os

# 尝试导入可视化库
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # 无GUI后端
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ChartType(Enum):
    """图表类型枚举"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HEATMAP = "heatmap"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"
    AREA = "area"


class DataType(Enum):
    """数据类型枚举"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    MIXED = "mixed"


@dataclass
class DataColumn:
    """数据列信息"""
    name: str
    data_type: DataType
    values: List[Any]
    stats: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        self._calculate_stats()
    
    def _calculate_stats(self):
        """计算统计信息"""
        if self.data_type == DataType.NUMERICAL:
            numerical_values = [v for v in self.values if isinstance(v, (int, float)) and v is not None]
            if numerical_values:
                self.stats = {
                    'mean': np.mean(numerical_values) if NUMPY_AVAILABLE else sum(numerical_values)/len(numerical_values),
                    'std': np.std(numerical_values) if NUMPY_AVAILABLE else 0,
                    'min': min(numerical_values),
                    'max': max(numerical_values),
                    'median': np.median(numerical_values) if NUMPY_AVAILABLE else sorted(numerical_values)[len(numerical_values)//2],
                    'count': len(numerical_values)
                }


@dataclass
class ChartConfig:
    """图表配置"""
    chart_type: ChartType
    title: str = "图表"
    xlabel: str = ""
    ylabel: str = ""
    figsize: Tuple[int, int] = (10, 6)
    color_scheme: str = "default"
    show_grid: bool = True
    rotate_labels: int = 0
    save_path: Optional[str] = None
    export_format: str = "png"


class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, data: Dict[str, List[Any]]):
        self.raw_data = data
        self.columns: List[DataColumn] = []
        self._parse_data()
    
    def _parse_data(self):
        """解析数据"""
        for col_name, values in self.raw_data.items():
            data_type = self._detect_data_type(values)
            self.columns.append(DataColumn(col_name, data_type, values))
    
    def _detect_data_type(self, values: List[Any]) -> DataType:
        """检测数据类型"""
        # 过滤None值
        valid_values = [v for v in values if v is not None]
        if not valid_values:
            return DataType.MIXED
        
        # 检查是否全是数值
        if all(isinstance(v, (int, float)) for v in valid_values):
            return DataType.NUMERICAL
        
        # 检查是否包含日期
        date_patterns = ['-', '/']
        if any(any(p in str(v) for p in date_patterns) for v in valid_values[:10]):
            try:
                for v in valid_values[:10]:
                    from datetime import datetime
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y']:
                        try:
                            datetime.strptime(str(v), fmt)
                            return DataType.TEMPORAL
                        except ValueError:
                            continue
            except:
                pass
        
        # 检查是否是分类数据
        unique_ratio = len(set(valid_values)) / len(valid_values)
        if unique_ratio < 0.5 or len(set(valid_values)) <= 10:
            return DataType.CATEGORICAL
        
        return DataType.MIXED
    
    def get_numerical_columns(self) -> List[DataColumn]:
        """获取数值列"""
        return [col for col in self.columns if col.data_type == DataType.NUMERICAL]
    
    def get_categorical_columns(self) -> List[DataColumn]:
        """获取分类列"""
        return [col for col in self.columns if col.data_type == DataType.CATEGORICAL]
    
    def get_temporal_columns(self) -> List[DataColumn]:
        """获取时间列"""
        return [col for col in self.columns if col.data_type == DataType.TEMPORAL]
    
    def analyze(self) -> Dict[str, Any]:
        """返回分析结果"""
        return {
            'total_columns': len(self.columns),
            'numerical_count': len(self.get_numerical_columns()),
            'categorical_count': len(self.get_categorical_columns()),
            'temporal_count': len(self.get_temporal_columns()),
            'columns': [{
                'name': col.name,
                'type': col.data_type.value,
                'stats': col.stats
            } for col in self.columns]
        }


class ChartRecommender:
    """图表推荐器"""
    
    @staticmethod
    def recommend(data: Dict[str, List[Any]]) -> List[ChartType]:
        """推荐合适的图表类型"""
        analyzer = DataAnalyzer(data)
        recommendations = []
        
        numerical_cols = analyzer.get_numerical_columns()
        categorical_cols = analyzer.get_categorical_columns()
        temporal_cols = analyzer.get_temporal_columns()
        
        # 基于数据特征推荐
        if temporal_cols and numerical_cols:
            recommendations.extend([ChartType.LINE, ChartType.AREA])
        
        if categorical_cols and numerical_cols:
            recommendations.extend([ChartType.BAR, ChartType.BOXPLOT])
        
        if len(numerical_cols) >= 2:
            recommendations.append(ChartType.SCATTER)
        
        if len(numerical_cols) >= 1:
            recommendations.append(ChartType.HISTOGRAM)
        
        if categorical_cols and len(numerical_cols) == 1:
            recommendations.append(ChartType.PIE)
        
        if len(numerical_cols) >= 2:
            recommendations.append(ChartType.HEATMAP)
        
        # 去重保持顺序
        seen = set()
        unique_recs = []
        for chart in recommendations:
            if chart not in seen:
                seen.add(chart)
                unique_recs.append(chart)
        
        return unique_recs if unique_recs else [ChartType.LINE]


class SmartVisualizer:
    """智能可视化主类"""
    
    COLOR_SCHEMES = {
        'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'pastel': ['#ffb3ba', '#ffdfba', '#ffffba', '#baffc9', '#bae1ff'],
        'dark': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'],
        'nature': ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2'],
        'ocean': ['#0077b6', '#00b4d8', '#90e0ef', '#caf0f8', '#03045e']
    }
    
    def __init__(self, data: Dict[str, List[Any]]):
        self.data = data
        self.analyzer = DataAnalyzer(data)
        self.fig = None
        self.ax = None
    
    def _get_colors(self, scheme: str, n: int) -> List[str]:
        """获取配色"""
        colors = self.COLOR_SCHEMES.get(scheme, self.COLOR_SCHEMES['default'])
        return colors[:min(n, len(colors))]
    
    def create_chart(self, config: ChartConfig) -> Optional[str]:
        """创建图表"""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.fig, self.ax = plt.subplots(figsize=config figsize)
        
        chart_type = config.chart_type
        x_col = self.analyzer.columns[0] if self.analyzer.columns else None
        y_cols = self.analyzer.columns[1:] if len(self.analyzer.columns) > 1 else self.analyzer.columns
        
        try:
            if chart_type == ChartType.LINE:
                self._draw_line_chart(x_col, y_cols, config)
            elif chart_type == ChartType.BAR:
                self._draw_bar_chart(x_col, y_cols, config)
            elif chart_type == ChartType.SCATTER:
                self._draw_scatter_chart(x_col, y_cols, config)
            elif chart_type == ChartType.PIE:
                self._draw_pie_chart(x_col, y_cols, config)
            elif chart_type == ChartType.HEATMAP:
                self._draw_heatmap_chart(y_cols, config)
            elif chart_type == ChartType.BOXPLOT:
                self._draw_boxplot_chart(y_cols, config)
            elif chart_type == ChartType.HISTOGRAM:
                self._draw_histogram_chart(y_cols, config)
            elif chart_type == ChartType.AREA:
                self._draw_area_chart(x_col, y_cols, config)
            
            self._finalize_plot(config)
            
            # 保存图表
            if config.save_path:
                plt.savefig(config.save_path, format=config.export_format, dpi=150, bbox_inches='tight')
            
            # 返回base64编码
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode()
            
        except Exception as e:
            print(f"绘图错误: {e}")
            return None
        finally:
            plt.close(self.fig)
    
    def _draw_line_chart(self, x_col, y_cols, config):
        """绘制折线图"""
        x_data = x_col.values if x_col else range(len(y_cols[0].values))
        colors = self._get_colors(config.color_scheme, len(y_cols))
        
        for i, y_col in enumerate(y_cols):
            self.ax.plot(x_data, y_col.values, marker='o', 
                        color=colors[i % len(colors)], 
                        label=y_col.name, linewidth=2)
    
    def _draw_bar_chart(self, x_col, y_cols, config):
        """绘制柱状图"""
        x_data = x_col.values if x_col else range(len(y_cols[0].values))
        colors = self._get_colors(config.color_scheme, len(y_cols))
        
        x = np.arange(len(x_data)) if not x_col else x_data
        width = 0.8 / len(y_cols) if len(y_cols) > 1 else 0.6
        
        for i, y_col in enumerate(y_cols):
            offset = (i - len(y_cols)/2 + 0.5) * width
            self.ax.bar([xi + offset for xi in (range(len(x_data)) if not x_col else x)], 
                       y_col.values, width, 
                       color=colors[i % len(colors)], 
                       label=y_col.name)
    
    def _draw_scatter_chart(self, x_col, y_cols, config):
        """绘制散点图"""
        if len(y_cols) >= 2:
            colors = self._get_colors(config.color_scheme, 1)
            self.ax.scatter(x_col.values if x_col else range(len(y_cols[0].values)),
                          y_cols[0].values,
                          c=colors[0], alpha=0.6, s=50)
    
    def _draw_pie_chart(self, x_col, y_cols, config):
        """绘制饼图"""
        if y_cols:
            values = [v for v in y_cols[0].values if v is not None]
            labels = [str(v) for v in x_col.values[:len(values)]] if x_col else [f'Item {i+1}' for i in range(len(values))]
            colors = self._get_colors(config.color_scheme, len(values))
            
            self.ax.pie(values, labels=labels, colors=colors, 
                       autopct='%1.1f%%', startangle=90)
            self.ax.axis('equal')
    
    def _draw_heatmap_chart(self, y_cols, config):
        """绘制热力图"""
        if len(y_cols) >= 2:
            data_matrix = []
            for y_col in y_cols:
                data_matrix.append([v if isinstance(v, (int, float)) else 0 for v in y_col.values])
            
            if NUMPY_AVAILABLE:
                data_matrix = np.array(data_matrix)
                im = self.ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto')
                plt.colorbar(im, ax=self.ax)
                
                self.ax.set_yticks(range(len(y_cols)))
                self.ax.set_yticklabels([col.name for col in y_cols])
                self.ax.set_xticks(range(min(len(y_cols[0].values), 20)))
            else:
                # 简易热力图
                for i, row in enumerate(data_matrix):
                    for j, val in enumerate(row[:20]):
                        color_val = min(val / max(max(row) if row else 1, 1), 1)
                        self.ax.add_patch(plt.Rectangle((j, i), 1, 1, 
                                                       facecolor=plt.cm.YlOrRd(color_val)))
                self.ax.set_xlim(0, min(len(data_matrix[0]), 20))
                self.ax.set_ylim(len(data_matrix), 0)
    
    def _draw_boxplot_chart(self, y_cols, config):
        """绘制箱线图"""
        if y_cols:
            data = [[v for v in y_col.values if isinstance(v, (int, float))] for y_col in y_cols]
            self.ax.boxplot(data, labels=[col.name for col in y_cols])
    
    def _draw_histogram_chart(self, y_cols, config):
        """绘制直方图"""
        if y_cols:
            values = [v for v in y_cols[0].values if isinstance(v, (int, float))]
            colors = self._get_colors(config.color_scheme, 1)
            self.ax.hist(values, bins=20, color=colors[0], edgecolor='white', alpha=0.7)
    
    def _draw_area_chart(self, x_col, y_cols, config):
        """绘制面积图"""
        x_data = x_col.values if x_col else range(len(y_cols[0].values))
        colors = self._get_colors(config.color_scheme, len(y_cols))
        
        for i, y_col in enumerate(y_cols):
            self.ax.fill_between(x_data, y_col.values, alpha=0.3, 
                                color=colors[i % len(colors)], label=y_col.name)
            self.ax.plot(x_data, y_col.values, color=colors[i % len(colors)], linewidth=2)
    
    def _finalize_plot(self, config):
        """完成图表设置"""
        self.ax.set_title(config.title, fontsize=14, fontweight='bold')
        
        if config.xlabel:
            self.ax.set_xlabel(config.xlabel)
        if config.ylabel:
            self.ax.set_ylabel(config.ylabel)
        
        if config.show_grid:
            self.ax.grid(True, linestyle='--', alpha=0.7)
        
        if self.analyzer.columns and len(self.analyzer.columns) > 1:
            self.ax.legend(loc='best')
        
        if config.rotate_labels:
            plt.xticks(rotation=config.rotate_labels)
        
        plt.tight_layout()
    
    def auto_create(self, chart_type: Optional[ChartType] = None) -> Dict[str, Any]:
        """自动创建图表"""
        if not chart_type:
            recommended = ChartRecommender.recommend(self.data)
            chart_type = recommended[0] if recommended else ChartType.LINE
        
        config = ChartConfig(
            chart_type=chart_type,
            title=f"自动生成 - {chart_type.value}图",
            color_scheme='default'
        )
        
        image_base64 = self.create_chart(config)
        
        return {
            'chart_type': chart_type.value,
            'image_base64': image_base64,
            'recommended_types': [ct.value for ct in ChartRecommender.recommend(self.data)],
            'data_analysis': self.analyzer.analyze()
        }


class DataVisualizerCLI:
    """命令行接口"""
    
    def __init__(self):
        self.visualizer = None
    
    def load_sample_data(self) -> Dict[str, List[Any]]:
        """加载示例数据"""
        return {
            '月份': ['1月', '2月', '3月', '4月', '5月', '6月'],
            '销售额': [12000, 15000, 13500, 18000, 21000, 19500],
            '利润': [3000, 4200, 3800, 5200, 6500, 5800],
            '客户数': [150, 180, 165, 210, 245, 230]
        }
    
    def interactive_mode(self):
        """交互模式"""
        print("""
╔══════════════════════════════════════════════════════╗
║           智能数据可视化工具 v1.0                    ║
║══════════════════════════════════════════════════════║
║  支持: 折线图/柱状图/散点图/饼图/热力图/箱线图       ║
╚══════════════════════════════════════════════════════╝
        """)
        
        while True:
            print("\n📊 选项:")
            print("1. 加载示例数据")
            print("2. 输入自定义数据")
            print("3. 查看推荐图表类型")
            print("4. 生成图表")
            print("5. 退出")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == '1':
                self.data = self.load_sample_data()
                print("✅ 示例数据已加载")
                self._show_data_info()
            
            elif choice == '2':
                self.data = self._input_custom_data()
                print("✅ 自定义数据已加载")
            
            elif choice == '3':
                if self.data:
                    self.visualizer = SmartVisualizer(self.data)
                    result = self.visualizer.auto_create()
                    print(f"\n📈 推荐图表类型: {', '.join(result['recommended_types'])}")
            
            elif choice == '4':
                if not self.data:
                    print("❌ 请先加载数据")
                    continue
                
                print("\n可用图表类型:")
                for i, ct in enumerate(ChartType, 1):
                    print(f"  {i}. {ct.value}")
                
                chart_choice = input("选择图表类型 (1-8): ").strip()
                try:
                    chart_type = list(ChartType)[int(chart_choice) - 1]
                except (ValueError, IndexError):
                    chart_type = ChartType.LINE
                
                self.visualizer = SmartVisualizer(self.data)
                result = self.visualizer.auto_create(chart_type)
                
                print(f"\n✅ {result['chart_type']} 图已生成")
                print(f"推荐类型: {', '.join(result['recommended_types'])}")
            
            elif choice == '5':
                print("👋 再见!")
                break
    
    def _show_data_info(self):
        """显示数据信息"""
        self.visualizer = SmartVisualizer(self.data)
        analysis = self.visualizer.analyzer.analyze()
        print(f"\n📊 数据分析:")
        print(f"  - 列数: {analysis['total_columns']}")
        print(f"  - 数值列: {analysis['numerical_count']}")
        print(f"  - 分类列: {analysis['categorical_count']}")
        print(f"  - 时间列: {analysis['temporal_count']}")
    
    def _input_custom_data(self) -> Dict[str, List[Any]]:
        """输入自定义数据"""
        data = {}
        print("\n输入数据 (每行: 列名=值1,值2,...)")
        print("示例: 成绩=85,92,78,90,88")
        print("输入 'done' 完成")
        
        while True:
            line = input("> ").strip()
            if line.lower() == 'done':
                break
            if '=' in line:
                col_name, values_str = line.split('=', 1)
                try:
                    values = [float(v.strip()) if v.strip().replace('.','').isdigit() else v.strip() 
                             for v in values_str.split(',')]
                    data[col_name.strip()] = values
                except ValueError:
                    values = [v.strip() for v in values_str.split(',')]
                    data[col_name.strip()] = values
        
        return data


def demo():
    """演示函数"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║        智能数据可视化工具 - Demo Mode                ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    
    # 示例数据
    sample_data = {
        '产品': ['A', 'B', 'C', 'D', 'E'],
        '销量': [120, 200, 150, 180, 220],
        '利润率': [0.15, 0.22, 0.18, 0.25, 0.20],
        '客户评分': [4.2, 4.8, 3.9, 4.5, 4.6]
    }
    
    print("📊 使用示例数据...")
    visualizer = SmartVisualizer(sample_data)
    
    print("\n📈 数据分析:")
    analysis = visualizer.analyzer.analyze()
    for col_info in analysis['columns']:
        print(f"  - {col_info['name']}: {col_info['type']}")
    
    print("\n🎯 推荐图表:")
    recommendations = ChartRecommender.recommend(sample_data)
    for chart in recommendations:
        print(f"  - {chart.value}")
    
    print("\n📊 自动生成图表...")
    result = visualizer.auto_create()
    print(f"生成图表类型: {result['chart_type']}")
    print(f"图片大小: {len(result['image_base64']) if result['image_base64'] else 0} bytes (base64)")
    
    print("\n✅ 演示完成!")
    print("\n💡 使用方法:")
    print("  python smart_data_visualizer.py          # 交互模式")
    print("  python smart_data_visualizer.py --demo   # 运行演示")
    print("  python smart_data_visualizer.py --api    # API模式演示")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            demo()
        elif sys.argv[1] == '--api':
            # API模式演示
            data = {
                'x': list(range(1, 11)),
                'y1': [i**2 for i in range(1, 11)],
                'y2': [i*10 for i in range(1, 11)]
            }
            viz = SmartVisualizer(data)
            result = viz.auto_create(ChartType.LINE)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python smart_data_visualizer.py [--demo|--api]")
    else:
        cli = DataVisualizerCLI()
        cli.interactive_mode()
