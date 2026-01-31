"""
Day 3: 通用算法工具箱
Algorithms and Data Structures Toolkit

吅含常用算法：
- 排序算法（冒泡排序、快速排序、归并排序）
- 常用工具（斐波那契数列、阶乘）

Author: MarsAssistant
Date: 2026-01-31
"""


# ============== 排序算法 ==============

def bubble_sort(arr: list) -> list:
    """
    冒泡排序 - 简单但效率较低
    时间复杂度: O(n²)
    """
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def quick_sort(arr: list) -> list:
    """
    快速排序 - 高效的排序算法
    时间复杂度: O(n log n)
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(arr: list) -> list:
    """
    归并排序 - 二分搜索（构度: O(n log n)
    """
    if len(arr) <= 1:
        return arr
   
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
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


# ============== 搜索算法 ==============

def binary_search(arr: list, target) -> int:
    """
    二分搜索 - 在有序数组中查找目标
    时间复杂度: O(log n)
    返回索引，未找到返回 -1
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def linear_search(arr: list, target) -> list:
    """
    线性搜索 - 查找所有匹配项
    返回所有匹配目标的索引列表
    """
    return [i for i, x in enumerate(arr) if x == target]


# ============== 字符串处理 ==============

def reverse_string(s: str) -> str:
    """反转字符串"""
    return s[::-1]


def is_palindrome(s: str) -> bool:
    """检查是否是回文字符串"""
    s = s.lower().replace(' ', '')
    return s == s[::-1]


# ============== 数学工具 ==============

def fibonacci(n: int) -> list:
    """
    生成斐波那契数列的前n项
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib[:n]


def factorial(n: int) -> int:
    """计算阶乘"""
    if n < 0:
        raise ValueError("负数没有阶乘")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n: int) -> bool:
    """检查是否为质数"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# ============== 主程序演示 5=============

if __name__ == "__main__":
    print("🧮 MarsAssistant 算法工具箱演示")
    print("=" * 40)
    
    # 测试排序
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {test_arr}")
    print(f"快速排序: {quick_sort(test_arr)}")
    print(f"归并排序: {merge_sort(test_arr)}")
    print()
    
    # 测试搜索
    sorted_arr = quick_sort(test_arr)
    print(f"在 {sorted_arr} 中搜索 25: 索引 {binary_search(sorted_arr, 25)}")
    print()
    
    # 测试字符串
    text = "A man a plan a canal Panama"
    print(f"字符串: '{text}'")
    print(f"反转: '{reverse_string(text)}'")
    print(f"是回文: {is_palindrome(text)}")
    print()
    
    # 测试数学工具
    print(f"斐波那契数列前10项: {fibonacci(10)}")
    print(f"10的阶乘: {factorial(10)}")
    print(f"17是质数: {is_prime(17)}")
    
    print("\n✅ 算法工具箱演示完成!")
