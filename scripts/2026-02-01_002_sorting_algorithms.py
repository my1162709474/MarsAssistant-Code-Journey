"""
排序算法合集 - Sorting Algorithms Collection
Day 14: 经典排序算法实现与性能比较

包含：
- 快速排序 (Quick Sort)
- 归并排序 (Merge Sort)
- 堆排序 (Heap Sort)
- 桶排序 (Bucket Sort)
- 性能对比测试
"""

import random
import time
from typing import List, Callable
import matplotlib.pyplot as plt


class SortingAlgorithms:
    """排序算法集合类"""
    
    @staticmethod
    def quick_sort(arr: List[int]) -> List[int]:
        """快速排序 - 平均O(n log n)，最坏O(n²)"""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return SortingAlgorithms.quick_sort(left) + middle + SortingAlgorithms.quick_sort(right)
    
    @staticmethod
    def merge_sort(arr: List[int]) -> List[int]:
        """归并排序 - 稳定O(n log n)"""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = SortingAlgorithms.merge_sort(arr[:mid])
        right = SortingAlgorithms.merge_sort(arr[mid:])
        
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def heap_sort(arr: List[int]) -> List[int]:
        """堆排序 - O(n log n)"""
        n = len(arr)
        
        # 构建最大堆
        for i in range(n // 2 - 1, -1, -1):
            SortingAlgorithms._heapify(arr, n, i)
        
        # 提取元素
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            SortingAlgorithms._heapify(arr, i, 0)
        
        return arr
    
    @staticmethod
    def _heapify(arr: List[int], n: int, i: int):
        """堆化辅助函数"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            SortingAlgorithms._heapify(arr, n, largest)
    
    @staticmethod
    def bucket_sort(arr: List[int]) -> List[int]:
        """桶排序 - O(n+k)，适合分布均匀的数据"""
        if len(arr) == 0:
            return arr
        
        min_val, max_val = min(arr), max(arr)
        bucket_count = len(arr)
        buckets = [[] for _ in range(bucket_count)]
        
        for num in arr:
            bucket_index = (num - min_val) * (bucket_count - 1) // (max_val - min_val + 1)
            buckets[bucket_index].append(num)
        
        result = []
        for bucket in buckets:
            SortingAlgorithms._insertion_sort(bucket)
            result.extend(bucket)
        
        return result
    
    @staticmethod
    def _insertion_sort(arr: List[int]):
        """插入排序 - 用于桶内排序"""
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
    
    @staticmethod
    def bubble_sort(arr: List[int]) -> List[int]:
        """冒泡排序 - O(n²)，教学用"""
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.algorithms = {
            'Quick Sort': SortingAlgorithms.quick_sort,
            'Merge Sort': SortingAlgorithms.merge_sort,
            'Heap Sort': SortingAlgorithms.heap_sort,
            'Bucket Sort': SortingAlgorithms.bucket_sort,
            'Bubble Sort': SortingAlgorithms.bubble_sort,
        }
    
    def test_performance(self, data: List[int], verbose: bool = True) -> dict:
        """测试所有算法的性能"""
        results = {}
        
        for name, algo in self.algorithms.items():
            test_data = data.copy()
            start = time.time()
            sorted_data = algo(test_data)
            elapsed = time.time() - start
            
            results[name] = {
                'time': elapsed,
                'sorted': sorted_data[:10],  # 只保存前10个元素
                'is_correct': sorted_data == sorted(data)
            }
            
            if verbose:
                status = "✓" if results[name]['is_correct'] else "✗"
                print(f"{status} {name}: {elapsed:.4f}s")
        
        return results
    
    def benchmark(self, sizes: List[int] = [100, 500, 1000, 5000]) -> dict:
        """基准测试 - 不同数据规模"""
        print("\n" + "="*60)
        print("性能基准测试")
        print("="*60)
        
        all_results = {}
        
        for size in sizes:
            print(f"\n数据规模: {size}")
            data = [random.randint(1, 10000) for _ in range(size)]
            results = self.test_performance(data)
            all_results[size] = results
        
        return all_results
    
    def plot_results(self, results: dict, save_path: str = None):
        """绘制性能对比图"""
        algorithms = list(self.algorithms.keys())
        sizes = list(results.keys())
        
        times = {algo: [] for algo in algorithms}
        
        for size in sizes:
            for algo in algorithms:
                times[algo].append(results[size][algo]['time'])
        
        plt.figure(figsize=(12, 8))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, algo in enumerate(algorithms):
            plt.plot(sizes, times[algo], marker='o', label=algo, 
                    color=colors[i % len(colors)], linewidth=2)
        
        plt.xlabel('数据规模 (n)', fontsize=12)
        plt.ylabel('执行时间 (秒)', fontsize=12)
        plt.title('排序算法性能对比', fontsize=14, fontweight='bold')
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.yscale('log')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"\n图表已保存至: {save_path}")
        
        return plt


def demo():
    """演示函数"""
    print("🚀 排序算法合集演示")
    print("="*60)
    
    # 小规模测试
    test_data = [64, 34, 25, 12, 22, 11, 90]
    print(f"\n原始数据: {test_data}")
    
    tester = PerformanceTester()
    results = tester.test_performance(test_data)
    
    print("\n排序后数据 (Quick Sort):")
    sorted_data = SortingAlgorithms.quick_sort(test_data.copy())
    print(f"  {sorted_data}")
    
    # 基准测试
    benchmark_results = tester.benchmark([100, 500, 1000])
    
    # 绘制图表
    tester.plot_results(benchmark_results, 'sorting_benchmark.png')
    
    return results


if __name__ == "__main__":
    demo()
