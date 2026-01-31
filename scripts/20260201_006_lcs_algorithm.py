#!/usr/bin/env python3
"""
最长公共子序列 (Longest Common Subsequence) 算法实现
============================================

LCS是经典的动态规划问题，用于找出两个序列中最长的共同子序列。
在生物信息学（DNA序列比对）、版本控制（diff算法）等领域有广泛应用。

时间复杂度: O(m*n)
空间复杂度: O(m*n) 或 O(min(m,n)) 优化版本
"""

def lcs_dp(s1: str, s2: str) -> str:
    """
    传统动态规划解法
    """
    m, n = len(s1), len(s2)
    # 创建DP表
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # 填充DP表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # 回溯找出LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs))


def lcs_memory_optimized(s1: str, s2: str) -> str:
    """
    空间优化版本：只用两行
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    previous = [0] * (len(s2) + 1)
    current = [0] * (len(s2) + 1)
    
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous, current = current, [0] * (len(s2) + 1)
    
    return previous[len(s2)]


def lcs_length_only(s1: str, s2: str) -> int:
    """
    只返回LCS长度，不返回具体序列
    最优空间复杂度: O(min(m,n))
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    previous = [0] * (len(s2) + 1)
    
    for i in range(1, len(s1) + 1):
        current = [0] * (len(s2) + 1)
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current
    
    return previous[-1]


# ========== 测试 ==========
if __name__ == "__main__":
    test_cases = [
        ("ABCDGH", "AEDFHR"),      # LCS: "ADH" (长度3)
        ("AGGTAB", "GXTXAYB"),     # LCS: "GTAB" (长度4)
        ("XMJYAUZ", "MZJAWXU"),    # LCS: "MJAU" (长度4)
        ("stone", "longest"),      # LCS: "one" (长度3)
        ("今天天气真好", "今天真是个好天气"),  # 中文测试
    ]
    
    print("=" * 50)
    print("最长公共子序列 (LCS) 算法演示")
    print("=" * 50)
    
    for s1, s2 in test_cases:
        print(f"\n输入1: {s1}")
        print(f"输入2: {s2}")
        
        lcs_result = lcs_dp(s1, s2)
        length = lcs_length_only(s1, s2)
        
        print(f"LCS序列: {lcs_result}")
        print(f"LCS长度: {length}")
        print("-" * 30)

print("\n✅ 算法完成！动态规划是解决序列问题的利器。")
