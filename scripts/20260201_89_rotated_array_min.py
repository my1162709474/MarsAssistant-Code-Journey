#!/usr/bin/env python3
"""
Day 89: 二分查找变体 - 寻找旋转排序数组中的最小值

算法说明：
- LeetCode 153: Find Minimum in Rotated Sorted Array
- 时间复杂度: O(log n)
- 空间复杂度: O(1)

核心思路：
使用二分查找，比较中间元素与右端点来确定最小值的位置。
"""

from typing import List

def find_min_in_rotated_array(nums: List[int]) -> int:
    """
    在旋转排序数组中找到最小值
    
    Args:
        nums: 旋转排序数组，例如 [4,5,6,7,0,1,2]
    
    Returns:
        最小值
    
    示例:
        >>> find_min_in_rotated_array([4,5,6,7,0,1,2])
        0
        >>> find_min_in_rotated_array([11,13,15,17])
        11
    """
    if not nums:
        raise ValueError("数组不能为空")
    
    left, right = 0, len(nums) - 1
    
    # 如果数组没有旋转，直接返回第一个元素
    if nums[left] <= nums[right]:
        return nums[left]
    
    while left < right:
        mid = (left + right) // 2
        
        # 如果中间元素大于右端点，最小值一定在右侧
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            # 中间元素小于等于右端点，最小值在左侧（包括中间）
            right = mid
    
    return nums[left]


def find_min_with_duplicates(nums: List[int]) -> int:
    """
    允许重复元素的版本
    当 nums[mid] == nums[right] 时，右端点左移一位
    """
    if not nums:
        raise ValueError("数组不能为空")
    
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if nums[mid] > nums[right]:
            left = mid + 1
        elif nums[mid] < nums[right]:
            right = mid
        else:
            # 相等时，右端点左移，缩小搜索范围
            right -= 1
    
    return nums[left]


# 单元测试
if __name__ == "__main__":
    test_cases = [
        ([4, 5, 6, 7, 0, 1, 2], 0),
        ([11, 13, 15, 17], 11),
        ([2, 1], 1),
        ([3, 4, 5, 1, 2], 1),
    ]
    
    print("二分查找变体测试：")
    for nums, expected in test_cases:
        result = find_min_in_rotated_array(nums)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: {nums} → 结果: {result}, 期望: {expected}")
    
    print("\n算法学习笔记：")
    print("1. 二分查找的核心是比较中间值与目标区域端点")
    print("2. 在旋转数组中，相邻区域的边界处就是最小值")
    print("3. 注意处理边界条件和重复元素的情况")
