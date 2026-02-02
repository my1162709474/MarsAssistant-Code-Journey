#!/usr/bin/env python3
"""
智能数据可视化工具 - Day 50
支持多种图表类型：折线图、柱状图、饼图、散点图、热力图、雷达图
"""

import json
import base64
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import numpy as np

class SmartChart:
    """智能图表生成器"""
    
    CHARTS = {
        'line': '折线图',
        'bar': '柱状图', 
        'pie': '饼图',
        'scatter': '散点图',
        'heatmap': '热力图',
        'radar': '雷达图',
        'histogram': '直方图',
        'box': '箱线图'
    }
    
    COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
        '#BB8FCE', '#85C1E9', '#F8B500', '#00CED1'
    ]
    
    def __init__(self, title="图表", figsize=(10, 6)):
        self.title = title
        self.figsize = figsize
        self.colors = self.COLORS
    
    def _setup_plot(self):
        """设置图表基础样式"""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
    
    def line(self, data, labels=None, xlabel="X", ylabel="Y"):
        """绘制折线图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize)
        
        x = list(range(len(data))) if labels is None else labels
        
        for i, (series, name) in enumerate(data):
            color = self.colors[i % len(self.colors)]
            ax.plot(x if labels else range(len(series)), series, 
                   marker='o', markersize=4, linewidth=2, 
                   label=name, color=color)
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return self._save(fig)
    
    def bar(self, data, labels=None, xlabel="类别", ylabel="数值"):
        """绘制柱状图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize)
        
        categories = [d[0] for d in data]
        values = [d[1] for d in data]
        
        bars = ax.bar(categories, values, color=self.colors[:len(categories)])
        
        # 添加数值标签
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=10)
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        return self._save(fig)
    
    def pie(self, data, labels=None):
        """绘制饼图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize)
        
        categories = [d[0] for d in data]
        values = [d[1] for d in data]
        
        wedges, texts, autotexts = ax.pie(values, labels=categories, 
                                         autopct='%1.1f%%',
                                         colors=self.colors[:len(categories)],
                                         explode=[0.02]*len(categories),
                                         shadow=True)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        
        return self._save(fig)
    
    def scatter(self, data, labels=None, xlabel="X", ylabel="Y"):
        """绘制散点图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize)
        
        for i, (x_vals, y_vals, name) in enumerate(data):
            ax.scatter(x_vals, y_vals, c=self.colors[i % len(self.colors)],
                      s=100, alpha=0.7, label=name, edgecolors='white')
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return self._save(fig)
    
    def heatmap(self, data, labels=None, title="热力图"):
        """绘制热力图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize)
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('数值', fontsize=12)
        
        # 添加数值标签
        for i in range(len(data)):
            for j in range(len(data[0])):
                text = ax.text(j, i, f'{data[i][j]:.1f}',
                              ha='center', va='center', 
                              color='white' if data[i][j] > np.mean(data) else 'black')
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        
        return self._save(fig)
    
    def radar(self, data, labels=None):
        """绘制雷达图"""
        self._setup_plot()
        fig, ax = plt.subplots(figsize=self.figsize, subplot_kw=dict(projection='polar'))
        
        categories = [d[0] for d in data]
        values = [d[1] for d in data]
        N = len(categories)
        
        # 计算角度
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color=self.colors[0])
        ax.fill(angles, values, alpha=0.25, color=self.colors[0])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        ax.set_title(self.title, fontsize=14, fontweight='bold', y=1.08)
        
        return self._save(fig)
    
    def _save(self, fig):
        """保存图表到base64"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return img_base64


class DataVisualizer:
    """数据可视化主类"""
    
    SUPPORTED_FORMATS = ['png', 'json', 'html']
    
    def __init__(self):
        self.chart = SmartChart()
        self.charts = self.chart.CHARTS
    
    def show_supported_charts(self):
        """显示支持的图表类型"""
        print("\n📊 支持的图表类型:")
        print("-" * 30)
        for chart_type, desc in self.charts.items():
            print(f"  • {chart_type:12} - {desc}")
        print("-" * 30)
    
    def demo(self):
        """演示所有图表类型"""
        print("\n🎨 智能数据可视化工具演示")
        print("=" * 50)
        
        # 1. 折线图
        print("\n📈 1. 折线图示例")
        line_data = [
            ([1,2,3,4,5,6], [2, 4, 3, 5, 4, 6], "销售额"),
            ([1,2,3,4,5,6], [3, 3, 5, 4, 6, 5], "利润")
        ]
        self.chart.title = "季度销售趋势"
        img = self.chart.line(line_data, labels=[f"Q{i}" for i in range(1,7)])
        print(f"   生成的图像base64长度: {len(img)}")
        
        # 2. 柱状图
        print("\n📊 2. 柱状图示例")
        bar_data = [("北京", 85), ("上海", 92), ("深圳", 78), ("杭州", 88)]
        self.chart.title = "城市GDP排名"
        img = self.chart.bar(bar_data)
        print(f"   生成的图像base64长度: {len(img)}")
        
        # 3. 饼图
        print("\n🥧 3. 饼图示例")
        pie_data = [("电子产品", 35), ("服装", 25), ("食品", 20), ("图书", 12), ("其他", 8)]
        self.chart.title = "电商平台品类占比"
        img = self.chart.pie(pie_data)
        print(f"   生成的图像base64长度: {len(img)}")
        
        # 4. 散点图
        print("\n⚫ 4. 散点图示例")
        scatter_data = [
            (np.random.rand(50)*100, np.random.rand(50)*100, "用户群A"),
            (np.random.rand(50)*100, np.random.rand(50)*100, "用户群B")
        ]
        self.chart.title = "用户行为分析"
        img = self.chart.scatter(scatter_data, xlabel="访问频率", ylabel="购买金额")
        print(f"   生成的图像base64长度: {len(img)}")
        
        # 5. 热力图
        print("\n🔥 5. 热力图示例")
        heatmap_data = np.random.rand(8, 8) * 100
        self.chart.title = "业务指标相关性矩阵"
        img = self.chart.heatmap(heatmap_data)
        print(f"   生成的图像base64长度: {len(img)}")
        
        # 6. 雷达图
        print("\n📡 6. 雷达图示例")
        radar_data = [("速度", 85), ("耐力", 72), ("力量", 90), ("智力", 88), ("敏捷", 78)]
        self.chart.title = "角色属性面板"
        img = self.chart.radar(radar_data)
        print(f"   生成的图像base64长度: {len(img)}")
        
        print("\n" + "=" * 50)
        print("✅ 演示完成！所有图表生成成功。")
        print("\n💡 使用方法:")
        print("   from smart_chart import SmartChart")
        print("   chart = SmartChart('我的图表')")
        print("   img_base64 = chart.bar([('A', 10), ('B', 20)])")


if __name__ == "__main__":
    visualizer = DataVisualizer()
    visualizer.demo()
