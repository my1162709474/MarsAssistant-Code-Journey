#!/usr/bin/env python3
"""
LZ77 简单压缩/解压缩工具
演示经典的数据压缩算法

原理：查找重复的字符串，用(距离,长度)引用替代
"""

import json
import base64


def lz77_compress(data: str, window_size: int = 256, min_match: int = 3) -> str:
    """LZ77 压缩"""
    result = []
    i = 0
    n = len(data)
    
    while i < n:
        best_dist = 0
        best_len = 0
        
        # 在滑动窗口中查找最长的匹配
        start = max(0, i - window_size)
        for j in range(start, i):
            length = 0
            while i + length < n and data[j + length] == data[i + length] and length < 255:
                length += 1
            
            if length > best_len and length >= min_match:
                best_dist = i - j
                best_len = length
        
        if best_len > 0:
            # 找到重复，用引用表示
            result.append((best_dist, best_len, data[i + best_len] if i + best_len < n else None))
            i += best_len + (1 if i + best_len < n else 0)
        else:
            # 没有匹配，直接输出字符
            result.append(data[i])
            i += 1
    
    return json.dumps(result)


def lz77_decompress(compressed: str) -> str:
    """LZ77 解压缩"""
    data = json.loads(compressed)
    result = []
    
    for item in data:
        if isinstance(item, str) and len(item) == 1:
            result.append(item)
        elif isinstance(item, list) and len(item) >= 2:
            dist, length = item[0], item[1]
            start = len(result) - dist
            for i in range(length):
                result.append(result[start + i])
            # 添加后续字符（如果有）
            if len(item) > 2 and item[2]:
                result.append(item[2])
    
    return ''.join(result)


def lz77_binary_compress(data: bytes, window_size: int = 4096, min_match: int = 4) -> bytes:
    """二进制版本的LZ77压缩（更实用）"""
    result = bytearray()
    i = 0
    
    while i < len(data):
        best_dist = 0
        best_len = 0
        
        # 滑动窗口搜索
        start = max(0, i - window_size)
        for j in range(start, i):
            length = 0
            while (i + length < len(data) and 
                   j + length < i and 
                   data[j + length] == data[i + length] and 
                   length < 255):
                length += 1
            
            if length > best_len and length >= min_match:
                best_dist = i - j
                best_len = length
        
        if best_len > 0:
            # 标记为引用：使用特殊字节(255)开头
            result.extend([0xFF, (best_dist >> 8) & 0xFF, best_dist & 0xFF, best_len])
            i += best_len
        else:
            result.append(data[i])
            i += 1
    
    return bytes(result)


def lz77_binary_decompress(compressed: bytes) -> bytes:
    """二进制版本解压缩"""
    result = bytearray()
    i = 0
    
    while i < len(compressed):
        if compressed[i] == 0xFF and i + 4 <= len(compressed):
            dist = (compressed[i+1] << 8) | compressed[i+2]
            length = compressed[i+3]
            start = len(result) - dist
            for j in range(length):
                result.append(result[start + j])
            i += 4
        else:
            result.append(compressed[i])
            i += 1
    
    return bytes(result)


# 演示
if __name__ == "__main__":
    print("=== LZ77 压缩算法演示 ===\n")
    
    # 测试文本
    test_text = "ABABABABCDABABABABABA"
    print(f"原文: {test_text}")
    
    compressed = lz77_compress(test_text)
    print(f"压缩后: {compressed}")
    
    decompressed = lz77_decompress(compressed)
    print(f"解压后: {decompressed}")
    print(f"压缩率: {len(compressed)}/{len(test_text)} = {len(compressed)/len(test_text):.2%}\n")
    
    # 实际文件压缩示例
    sample_data = b"Hello World! " * 100
    print(f"二进制数据大小: {len(sample_data)} bytes")
    
    binary_compressed = lz77_binary_compress(sample_data)
    print(f"压缩后大小: {len(binary_compressed)} bytes")
    print(f"压缩率: {len(binary_compressed)/len(sample_data):.2%}")
    
    binary_decompressed = lz77_binary_decompress(binary_compressed)
    assert binary_decompressed == sample_data
    print("✓ 解压验证通过")
