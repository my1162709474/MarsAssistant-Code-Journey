#!/usr/bin/env python3
"""
密码强度检测器 (Day 17)
=======================
一个实用的密码安全分析工具，帮助用户创建更安全的密码。

功能：
- 多维度密码强度评估
- 实时熵值计算
- 智能改进建议
- 常见密码检测
"""

import math
import re
import random
from typing import Dict, Tuple

# 常见弱密码列表
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", "12345", "123456789",
    "football", "iloveyou", "admin", "welcome", "dragon", "monkey",
    "baseball", "letmein", "master", "sunshine", "princess", "password123"
}


def calculate_entropy(password: str) -> float:
    """
    计算密码的熵值（信息熵）
    熵越高，密码越难被猜测
    
    公式: H = L × log2(R)
    L = 密码长度
    R = 字符集大小
    """
    charset_size = 0
    
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        charset_size += 32
    
    if charset_size == 0:
        return 0
    
    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)


def check_common_password(password: str) -> bool:
    """检查是否是常见密码"""
    return password.lower() in COMMON_PASSWORDS


def analyze_password(password: str) -> Dict:
    """
    全面分析密码强度
    返回详细的分析结果
    """
    result = {
        "password": password,
        "length": len(password),
        "has_lowercase": False,
        "has_uppercase": False,
        "has_digit": False,
        "has_special": False,
        "special_chars": set(),
        "consecutive_chars": 0,
        "repeated_chars": 0,
        "is_common": False,
        "entropy": 0,
        "strength_score": 0,
        "strength_level": "",
        "suggestions": []
    }
    
    # 字符类型检测
    result["has_lowercase"] = bool(re.search(r'[a-z]', password))
    result["has_uppercase"] = bool(re.search(r'[A-Z]', password))
    result["has_digit"] = bool(re.search(r'\d', password))
    result["has_special"] = bool(re.search(r'[!@#$%^&*()_+-=[]{}|;:,.<>?/]', password))
    
    # 收集特殊字符
    result["special_chars"] = set(re.findall(r'[!@#$%^&*()_+-=[]{}|;:,.<>?/]', password))
    
    # 检测连续字符（如 "123", "abc"）
    consecutive = 1
    for i in range(1, len(password)):
        if password[i].isdigit() and password[i-1].isdigit():
            if int(password[i]) - int(password[i-1]) == 1:
                consecutive += 1
        elif password[i].isalpha() and password[i-1].isalpha():
            if ord(password[i].lower()) - ord(password[i-1].lower()) == 1:
                consecutive += 1
    result["consecutive_chars"] = consecutive
    
    # 检测重复字符（如 "aaa"）
    repeated = 1
    for i in range(1, len(password)):
        if password[i] == password[i-1]:
            repeated += 1
    result["repeated_chars"] = repeated
    
    # 检查常见密码
    result["is_common"] = check_common_password(password)
    
    # 计算熵值
    result["entropy"] = calculate_entropy(password)
    
    # 计算强度分数 (0-100)
    score = 0
    
    # 长度评分 (最多40分)
    if len(password) >= 16:
        score += 40
    elif len(password) >= 12:
        score += 30
    elif len(password) >= 8:
        score += 20
    elif len(password) >= 6:
        score += 10
    
    # 字符类型评分 (每种类型+15分)
    if result["has_lowercase"]:
        score += 15
    if result["has_uppercase"]:
        score += 15
    if result["has_digit"]:
        score += 15
    if result["has_special"]:
        score += 15
    
    # 惩罚
    if result["is_common"]:
        score = min(score, 10)
    if result["consecutive_chars"] >= 4:
        score -= 10
    if result["repeated_chars"] >= 3:
        score -= 10
    
    result["strength_score"] = max(0, min(100, score))
    
    # 强度等级
    if score >= 81:
        result["strength_level"] = "很强 🛡️"
    elif score >= 61:
        result["strength_level"] = "强 💪"
    elif score >= 41:
        result["strength_level"] = "中等 📊"
    elif score >= 21:
        result["strength_level"] = "弱 ⚠️"
    else:
        result["strength_level"] = "很弱 ❌"
    
    # 生成改进建议
    if len(password) < 12:
        result["suggestions"].append("• 增加密码长度到12个字符以上")
    if not result["has_uppercase"]:
        result["suggestions"].append("• 添加大写字母 (A-Z)")
    if not result["has_lowercase"]:
        result["suggestions"].append("• 添加小写字母 (a-z)")
    if not result["has_digit"]:
        result["suggestions"].append("• 添加数字 (0-9)")
    if not result["has_special"]:
        result["suggestions"].append("• 添加特殊字符 (!@#$%等)")
    if result["consecutive_chars"] >= 4:
        result["suggestions"].append("• 避免连续字符序列")
    if result["repeated_chars"] >= 3:
        result["suggestions"].append("• 避免重复字符")
    if result["is_common"]:
        result["suggestions"].append("• 请勿使用常见密码")
    
    if not result["suggestions"]:
        result["suggestions"].append("✅ 密码设计得很好！")
    
    return result


def generate_strong_password(length: int = 16) -> str:
    """
    生成一个强密码
    """
    if length < 8:
        length = 8
    
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    all_chars = lowercase + uppercase + digits + special
    
    # 确保每种类型至少有一个
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # 填充剩余长度
    for _ in range(length - 4):
        password.append(random.choice(all_chars))
    
    # 打乱顺序
    random.shuffle(password)
    
    return "".join(password)


def print_report(result: Dict):
    """打印详细的密码分析报告"""
    print("\n" + "=" * 50)
    print("🔐 密码强度分析报告")
    print("=" * 50)
    print(f"\n📝 密码示例: {result['password'][:10]}...")
    print(f"📏 密码长度: {result['length']} 个字符")
    print(f"\n📊 强度评分: {result['strength_score']}/100")
    print(f"🏷️  强度等级: {result['strength_level']}")
    print(f"🧮 信息熵: {result['entropy']} bits")
    
    print("\n✅ 字符组成:")
    print(f"   - 小写字母: {'是' if result['has_lowercase'] else '否'}")
    print(f"   - 大写字母: {'是' if result['has_uppercase'] else '否'}")
    print(f"   - 数字: {'是' if result['has_digit'] else '否'}")
    print(f"   - 特殊字符: {'是' if result['has_special'] else '否'}")
    
    if result['special_chars']:
        print(f"   - 特殊字符集: {''.join(result['special_chars'])}")
    
    print("\n⚠️  风险检测:")
    print(f"   - 连续字符序列: {result['consecutive_chars']} 个连续")
    print(f"   - 重复字符: {result['repeated_chars']} 个重复")
    print(f"   - 常见密码: {'是 ⚠️' if result['is_common'] else '否'}")
    
    print("\n💡 改进建议:")
    for suggestion in result['suggestions']:
        print(f"   {suggestion}")
    
    print("\n" + "=" * 50)


def main():
    """主函数"""
    print("🔐 密码强度检测器 (Day 17)")
    print("=" * 40)
    print("输入 'g' 生成强密码")
    print("输入 'q' 退出")
    print("=" * 40)
    
    while True:
        choice = input("\n👉 请输入密码进行检测: ").strip()
        
        if choice.lower() == 'q':
            print("👋 再见！")
            break
        
        if choice.lower() == 'g':
            new_password = generate_strong_password()
            print(f"\n🎉 生成的强密码: {new_password}")
            result = analyze_password(new_password)
            print_report(result)
            continue
        
        if not choice:
            print("⚠️ 请输入密码！")
            continue
        
        result = analyze_password(choice)
        print_report(result)


if __name__ == "__main__":
    main()
