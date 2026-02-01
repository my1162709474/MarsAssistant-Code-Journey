#!/usr/bin/env python3
"""
Day 022: Greedy Algorithm Examples - 贪心算法示例

This script demonstrates the core concepts and applications of greedy algorithms.
学习贪心算法的核心思想和典型应用场景。

Topics Covered:
1. Activity Selection Problem (活动选择问题)
2. Fractional Knapsack (分数背包问题)
3. Huffman Coding (哈夫曼编码)
4. Minimum Spanning Tree - Prim's Algorithm (Prim最小生成树)
"""

from typing import List, Tuple
import heapq
from collections import defaultdict


# ============== 1. Activity Selection Problem ==============
def activity_selection(activities: List[Tuple[int, int]]) -> List[int]:
    """
    活动选择问题 - 选择最多不冲突的活动
    
    Args:
        activities: List of (start_time, end_time) tuples
    
    Returns:
        Indices of selected activities
    """
    # 按结束时间排序
    sorted_activities = sorted(enumerate(activities), key=lambda x: x[1][1])
    
    selected = []
    last_end_time = -1
    
    for idx, (start, end) in sorted_activities:
        if start >= last_end_time:
            selected.append(idx)
            last_end_time = end
    
    return selected


# ============== 2. Fractional Knapsack ==============
def fractional_knapsack(values: List[float], weights: List[float], capacity: float) -> Tuple[float, List[float]]:
    """
    分数背包问题 - 可以取部分物品
    
    Args:
        values: List of item values
        weights: List of item weights
        capacity: Maximum carrying capacity
    
    Returns:
        (maximum value, list of fractions taken)
    """
    n = len(values)
    ratios = [(values[i] / weights[i], i) for i in range(n)]
    ratios.sort(reverse=True)  # 按单位价值排序
    
    total_value = 0.0
    fractions = [0.0] * n
    
    for ratio, i in ratios:
        if weights[i] <= capacity:
            fractions[i] = 1.0
            total_value += values[i]
            capacity -= weights[i]
        else:
            fractions[i] = capacity / weights[i]
            total_value += values[i] * fractions[i]
            break
    
    return total_value, fractions


# ============== 3. Huffman Coding ==============
class HuffmanCoding:
    def __init__(self):
        self.codes = {}
    
    def build_huffman_tree(self, text: str) -> dict:
        """
        Build Huffman coding for given text
        
        Time Complexity: O(n log n)
        """
        if not text:
            return {}
        
        # Count frequency
        freq = defaultdict(int)
        for char in text:
            freq[char] += 1
        
        # Build priority queue
        heap = [(count, char) for char, count in freq.items()]
        heapq.heapify(heap)
        
        # Merge nodes
        while len(heap) > 1:
            left_count, left_char = heapq.heappop(heap)
            right_count, right_char = heapq.heappop(heap)
            heapq.heappush(heap, (left_count + right_count, (left_char, right_char)))
        
        # Generate codes
        if heap:
            root = heap[0][1]
            self._generate_codes(root, '')
        
        return self.codes
    
    def _generate_codes(self, node: Tuple, prefix: str):
        if isinstance(node, str):
            if node:
                self.codes[node] = prefix if prefix else '0'
        else:
            left, right = node
            self._generate_codes(left, prefix + '0')
            self._generate_codes(right, prefix + '1')
    
    def encode(self, text: str) -> str:
        """Encode text using Huffman coding"""
        codes = self.build_huffman_tree(text)
        return ''.join(codes.get(char, '') for char in text)
    
    def decode(self, encoded: str) -> str:
        """Decode Huffman encoded string"""
        if not encoded or not self.codes:
            return ''
        
        # Build reverse mapping
        reverse_codes = {code: char for char, code in self.codes.items()}
        
        result = []
        current = ''
        for bit in encoded:
            current += bit
            if current in reverse_codes:
                result.append(reverse_codes[current])
                current = ''
        
        return ''.join(result)


# ============== 4. Prim's Algorithm for MST ==============
def prim_mst(graph: dict) -> List[Tuple[int, int, float]]:
    """
    Prim算法 - 求最小生成树
    
    Args:
        graph: Adjacency list, {node: [(neighbor, weight), ...]}
    
    Returns:
        List of edges in MST: [(u, v, weight), ...]
    """
    if not graph:
        return []
    
    visited = set()
    mst = []
    heap = []  # (weight, u, v)
    
    # Start from first node
    start_node = next(iter(graph))
    visited.add(start_node)
    
    for neighbor, weight in graph[start_node]:
        heapq.heappush(heap, (weight, start_node, neighbor))
    
    while heap and len(visited) < len(graph):
        weight, u, v = heapq.heappop(heap)
        
        if v in visited:
            continue
        
        visited.add(v)
        mst.append((u, v, weight))
        
        for neighbor, w in graph[v]:
            if neighbor not in visited:
                heapq.heappush(heap, (w, v, neighbor))
    
    return mst


# ============== Demo Functions ==============
def demo_activity_selection():
    print("=" * 50)
    print("1. Activity Selection Problem")
    print("=" * 50)
    
    activities = [
        (1, 4),   # Activity 0
        (3, 5),   # Activity 1
        (0, 6),   # Activity 2
        (5, 7),   # Activity 3
        (3, 8),   # Activity 4
        (5, 9),   # Activity 5
        (6, 10),  # Activity 6
        (8, 11),  # Activity 7
        (8, 12),  # Activity 8
        (2, 13),  # Activity 9
        (12, 14), # Activity 10
    ]
    
    selected = activity_selection(activities)
    print(f"Activities: {activities}")
    print(f"Selected indices: {selected}")
    print(f"Selected activities: {[activities[i] for i in selected]}")


def demo_fractional_knapsack():
    print("\n" + "=" * 50)
    print("2. Fractional Knapsack")
    print("=" * 50)
    
    values = [60, 100, 120]
    weights = [10, 20, 30]
    capacity = 50
    
    max_value, fractions = fractional_knapsack(values, weights, capacity)
    print(f"Values: {values}")
    print(f"Weights: {weights}")
    print(f"Capacity: {capacity}")
    print(f"Maximum value: {max_value:.2f}")
    print(f"Fractions taken: {fractions}")


def demo_huffman_coding():
    print("\n" + "=" * 50)
    print("3. Huffman Coding")
    print("=" * 50)
    
    text = "hello world"
    huffman = HuffmanCoding()
    encoded = huffman.encode(text)
    
    print(f"Original text: '{text}'")
    print(f"Encoded: {encoded}")
    print(f"Codes: {huffman.codes}")
    
    decoded = huffman.decode(encoded)
    print(f"Decoded: '{decoded}'")


def demo_prim_mst():
    print("\n" + "=" * 50)
    print("4. Prim's Algorithm - Minimum Spanning Tree")
    print("=" * 50)
    
    graph = {
        0: [(1, 2), (3, 6)],
        1: [(0, 2), (2, 3), (3, 8), (4, 5)],
        2: [(1, 3), (4, 7)],
        3: [(0, 6), (1, 8), (4, 9)],
        4: [(1, 5), (2, 7), (3, 9)]
    }
    
    mst = prim_mst(graph)
    print("Graph edges (u, v, weight):")
    for u, v, w in mst:
        print(f" {u} -- {v} (weight: {w})")
    
    total_weight = sum(w for _, _, w in mst)
    print(f"Total MST weight: {total_weight}")


if __name__ == "__main__":
    print("Greedy Algorithm Examples - 贪巃箷法示侈�")
    print("=" * 50)
    
    demo_activity_selection()
    demo_fractional_knapsack()
    demo_huffman_coding()
    demo_prim_mst()
    
    print("\n" + "=" * 50)
    print("All demos completed!")
    print("Key Insight: Greedy algorithms make locally optimal choices")
    print("at each step, hoping to find a global optimum.")
    print("=" * 50)
