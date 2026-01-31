def binary_search(arr, target):
    """
    二分查找算法 - 经典算法练习
    时间复杂度: O(log n)
    空间复杂度: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid  # 找到目标，返回索引
        elif arr[mid] < target:
            left = mid + 1  # 目标在右半部分
        else:
            right = mid - 1  # 目标在左半部分
    
    return -1  # 未找到目标


def test_binary_search():
    """测试二分查找"""
    test_cases = [
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, 4),
        ([1, 2, 3, 4, 5], 1, 0),
        ([1, 2, 3, 4, 5], 5, 4),
        ([1, 2, 3, 4, 5], 6, -1),
        ([], 1, -1),
        ([1], 1, 0),
        ([1], 2, -1),
    ]
    
    for arr, target, expected in test_cases:
        result = binary_search(arr, target)
        assert result == expected, f"测试失败: arr={arr}, target={target}, expected={expected}, got={result}"
    
    print("✅ 所有测试通过！")


if __name__ == "__main__":
    test_binary_search()
    
    # 示例使用
    sorted_array = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    target = 23
    
    index = binary_search(sorted_array, target)
    if index != -1:
        print(f"🎯 目标 {target} 在索引 {index} 处找到")
    else:
        print(f"❌ 目标 {target} 未找到")
