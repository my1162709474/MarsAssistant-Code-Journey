#!/usr/bin/env python3
"""
Binary Search Visualizer - AI辅助学习工具
展示二分查找算法的可视化过程

Day 1: Binary Search Visualizer
"""

from typing import List
import random


class BinarySearchVisualizer:
    """二分查找可视化器 - 帮助理解算法执行过程"""
    
    def __init__(self, data: List[int] = None, size: int = 20):
        self.data = sorted(data) if data else self._generate_random_data(size)
        self.steps = []
        
    def _generate_random_data(self, size: int) -> List[int]:
        """生成随机数据"""
        return random.sample(range(1, 101), size)
    
    def search(self, target: int, visualize: bool = True) -> int:
        """
        二分查找算法（带可视化）
        
        Args:
            target: 目标值
            visualize: 是否记录执行步骤
            
        Returns:
            目标值的索引，未找到返回-1
        """
        left, right = 0, len(self.data) - 1
        self.steps = []
        
        while left <= right:
            mid = (left + right) // 2
            mid_val = self.data[mid]
            
            # 记录步骤
            if visualize:
                self.steps.append({
                    'left': left,
                    'right': right,
                    'mid': mid,
                    'mid_val': mid_val,
                    'target': target,
                    'found': mid_val == target
                })
            
            if mid_val == target:
                return mid
            elif mid_val < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    def print_visualization(self, target: int):
        """打印可视化结果"""
        print(f"\n{'='*60}")
        print(f"🔍 Binary Search Visualizer - 查找目标: {target}")
        print(f"📊 数据: {self.data}")
        print(f"{'='*60}")
        
        if not self.steps:
            print("❌ 未找到目标值")
            return
            
        for i, step in enumerate(self.steps, 1):
            left, right, mid, mid_val = step['left'], step['right'], step['mid'], step['mid_val']
            
            # 构建可视化条
            bar = ""
            for idx in range(len(self.data)):
                if idx == left:
                    bar += "L"
                elif idx == right:
                    bar += "R"
                elif idx == mid:
                    bar += "⬇️" if not step['found'] else "🎯"
                else:
                    bar += "·"
            
            print(f"\n步骤 {i}: {bar}")
            print(f"         {' ' * (mid * 3)}↑")
            print(f"         中间值: {mid_val}")
            print(f"         范围: [{left}, {right}]")
            
            if step['found']:
                print(f"\n✅ 找到目标值 {target} 于索引 {mid}！")
                break
                
        print(f"\n{'='*60}\n")


def demo():
    """演示"""
    visualizer = BinarySearchVisualizer(size=15)
    target = random.choice(visualizer.data)
    
    visualizer.print_visualization(target)
    
    # 测试未找到的情况
    print("\n🔍 测试未找到的情况:")
    visualizer.print_visualization(999)


if __name__ == "__main__":
    demo()
