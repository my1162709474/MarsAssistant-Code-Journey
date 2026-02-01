import json

# 二分搜索算法合集
# ===========================================
# 包含多种二分搜索变体和应用场景
# ===========================================

def binary_search(arr, target):
    """
    标准二分搜索
    找到返回索引，否则返回-1
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


def binary_search_left_bound(arr, target):
    """
    查找左侧边界：第一个大于等于target的位置
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left


def binary_search_right_bound(arr, target):
    """
    查找右侧边界：最后一个小于等于target的位置
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] > target:
            right = mid - 1
        else:
            left = mid + 1
    return right


def first_greater_than_target(arr, target):
    """
    查找第一个严格大于target的元素
    """
    left, right = 0, len(arr) - 1
    ans = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] > target:
            ans = mid
            right = mid - 1
        else:
            left = mid + 1
    return ans


def last_less_than_target(arr, target):
    """
    查找最后一个小于target的元素
    """
    left, right = 0, len(arr) - 1
    ans = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < target:
            ans = mid
            left = mid + 1
        else:
            right = mid - 1
    return ans


def search_rotated_array(arr, target):
    """
    搜索旋转排序数组（无重复）
    LeetCode 33
    """
    if not arr:
        return -1
    
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        
        # 判断哪边有序
        if arr[left] <= arr[mid]:  # 左边有序
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # 右边有序
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def search_rotated_with_duplicates(arr, target):
    """
    搜索旋转排序数组（有重复）
    LeetCode 81
    """
    if not arr:
        return False
    
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return True
        
        # 处理重复元素
        if arr[left] == arr[mid] == arr[right]:
            left += 1
            right -= 1
        elif arr[left] <= arr[mid]:  # 左边有序
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # 右边有序
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    return False


def find_min_in_rotated(arr):
    """
    寻找旋转数组中的最小值
    LeetCode 153
    """
    if not arr:
        return None
    
    left, right = 0, len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[right]:
            left = mid + 1
        else:
            right = mid
    return arr[left]


def find_peak_element(arr):
    """
    寻找峰值元素（比邻居大的元素）
    LeetCode 162
    """
    left, right = 0, len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[mid + 1]:
            right = mid
        else:
            left = mid + 1
    return left


def find_kth_smallest(arr1, arr2, k):
    """
    在两个有序数组中找到第k小的元素
    LeetCode 4
    """
    def find_kth(a1, a2, k, a1_start, a2_start):
        if k > len(a1) + len(a2):
            return None
        
        # 边界情况
        if a1_start >= len(a1):
            return a2[a2_start + k - 1]
        if a2_start >= len(a2):
            return a1[a1_start + k - 1]
        if k == 1:
            return min(a1[a1_start], a2[a2_start])
        
        a1_mid = a1_start + k // 2 - 1
        a2_mid = a2_start + k // 2 - 1
        
        a1_val = a1[a1_mid] if a1_mid < len(a1) else float(inf)
        a2_val = a2[a2_mid] if a2_mid < len(a2) else float(inf)
        
        if a1_val < a2_val:
            return find_kth(a1, a2, k - k // 2, a1_mid + 1, a2_start)
        else:
            return find_kth(a1, a2, k - k // 2, a1_start, a2_mid + 1)
    
    return find_kth(arr1, arr2, k, 0, 0)


def square_root(x):
    """
    计算平方根（整数）
    LeetCode 69
    """
    if x < 2:
        return x
    
    left, right = 1, x // 2
    while left <= right:
        mid = (left + right) // 2
        sq = mid * mid
        if sq == x:
            return mid
        elif sq < x:
            left = mid + 1
        else:
            right = mid - 1
    return right


def search_range(arr, target):
    """
    搜索目标值的第一个和最后一个位置
    LeetCode 34
    """
    left = binary_search_left_bound(arr, target)
    right = binary_search_right_bound(arr, target)
    
    if left < len(arr) and arr[left] == target:
        return [left, right]
    return [-1, -1]


# ===========================================
# 测试函数
# ===========================================

def test_binary_search():
    arr = [1, 3, 5, 7, 9, 11, 13, 15]
    
    print("标准二分搜索:")
    for target in [1, 7, 13, 0, 16]:
        result = binary_search(arr, target)
        print(f"  搜索 {target}: {result}")
    
    print("
左侧边界:")
    arr = [1, 2, 2, 2, 3, 4, 4, 5]
    for target in [2, 4, 6]:
        idx = binary_search_left_bound(arr, target)
        print(f"  第一个>={target}: 索引 {idx}")
    
    print("
右侧边界:")
    for target in [2, 4, 6]:
        idx = binary_search_right_bound(arr, target)
        print(f"  最后一个小于={target}: 索引 {idx}")


def test_rotated_search():
    print("
旋转数组搜索:")
    arr = [4, 5, 6, 7, 0, 1, 2, 3]
    for target in [0, 3, 5]:
        result = search_rotated_array(arr, target)
        print(f"  搜索 {target} 在 {arr[:4]}... 中: {result}")
    
    print(f"  最小值: {find_min_in_rotated(arr)}")


def test_special_cases():
    print("
特殊场景:")
    # 峰值查找
    arr = [1, 2, 3, 1]
    peak = find_peek_element(arr)
    print(f"  峰值元素索引: {peak}, 值: {arr[peak]}")
    
    # 第k小元素
    arr1, arr2 = [1, 3, 5, 7], [2, 4, 6, 8]
    for k in range(1, 9):
        result = find_kth_smallest(arr1, arr2, k)
        print(f"  第{k}小元素: {result}")
    
    # 平方根
    for x in [0, 1, 4, 8, 16, 27]:
        print(f"  sqrt({x}) = {square_root(x)}")


def main():
    print("二分搜索算法合雄 - 测试")
    print("=" * 40)
    
    test_binary_search()
    test_rotated_search()
    test_special_cases()
    
    print("
" + "=" * 40)
    print("测试完成！")


if __name__ == "__main__":
    main()

