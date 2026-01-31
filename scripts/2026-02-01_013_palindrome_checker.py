#!/usr/bin/env python3
"""
回文数检测器 - Day 13
功能：检测字符串或数字是否为回文数

回文数/回文字符串：正着读和反着读都一样
例如：121, 12321, "上海自来水来自海上"
"""

import re


def is_palindrome_number(n: int) -> bool:
    """检测整数是否为回文数"""
    if n < 0:
        return False
    original = n
    reversed_num = 0
    
    while n > 0:
        digit = n % 10
        reversed_num = reversed_num * 10 + digit
        n //= 10
    
    return original == reversed_num


def is_palindrome_string(s: str) -> bool:
    """检测字符串是否为回文数（忽略大小写和非字母数字）"""
    # 只保留字母和数字，转为小写
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    return cleaned == cleaned[::-1]


def is_palindrome_recursive(s: str) -> bool:
    """递归方式检测回文字符串"""
    s = s.lower()
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome_recursive(s[1:-1])


def longest_palindromic_substring(s: str) -> str:
    """
    查找最长回文子串
    动态规划解法 - O(n²)时间复杂度
    """
    n = len(s)
    if n <= 1:
        return s
    
    # dp[i][j] 表示 s[i:j+1] 是否为回文
    dp = [[False] * n for _ in range(n)]
    
    # 所有长度为1的子串都是回文
    for i in range(n):
        dp[i][i] = True
    
    max_len = 1
    start = 0
    
    # 检查长度为2及以上的子串
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            
            # 首尾相同
            if s[i] == s[j]:
                # 长度为2，或者内部是回文
                if length == 2 or dp[i + 1][j - 1]:
                    dp[i][j] = True
                    if length > max_len:
                        max_len = length
                        start = i
    
    return s[start:start + max_len]


def expand_around_center(s: str) -> str:
    """
    中心扩展法查找最长回文子串 - O(n)时间复杂度
    """
    if not s or len(s) < 2:
        return s
    
    start, end = 0, 0
    
    for i in range(len(s)):
        # 奇数长度回文
        len1 = expand(s, i, i)
        # 偶数长度回文
        len2 = expand(s, i, i + 1)
        max_len = max(len1, len2)
        
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    
    return s[start:end + 1]


def expand(s: str, left: int, right: int) -> int:
    """中心扩展辅助函数"""
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return right - left - 1


def count_palindromic_substrings(s: str) -> int:
    """统计字符串中回文子串的数量"""
    count = 0
    for i in range(len(s)):
        # 奇数中心
        count += expand(s, i, i)
        # 偶数中心
        count += expand(s, i, i + 1)
    return count


# ==================== 演示示例 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🔍 回文数检测器 - Day 13")
    print("=" * 50)
    
    # 测试数字
    test_numbers = [121, -121, 10, 12321, 12345]
    print("\n📊 数字回文检测:")
    for num in test_numbers:
        result = "✓ 是回文" if is_palindrome_number(num) else "✗ 不是回文"
        print(f"  {num}: {result}")
    
    # 测试字符串
    test_strings = [
        "上海自来水来自海上",
        "A man a plan a canal Panama",
        "Hello World",
        "12321",
        "racecar",
        "madam"
    ]
    print("\n📊 字符串回文检测:")
    for s in test_strings:
        result = "✓ 是回文" if is_palindrome_string(s) else "✗ 不是回文"
        print(f"  \"{s}\": {result}")
    
    # 测试最长回文子串
    test_cases = [
        "babad",
        "cbbd",
        "上海自来水来自海上abcba",
        "abcdef"
    ]
    print("\n📊 最长回文子串:")
    for s in test_cases:
        result = longest_palindromic_substring(s)
        print(f"  \"{s}\" → \"{result}\"")
    
    # 测试回文子串计数
    print("\n📊 回文子串计数:")
    for s in ["abc", "aaa", "ababa"]:
        count = count_palindromic_substrings(s)
        print(f"  \"{s}\": {count} 个回文子串")
    
    print("\n" + "=" * 50)
    print("✅ 演示完成！")
    print("=" * 50)
