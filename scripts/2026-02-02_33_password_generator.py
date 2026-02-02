#!/usr/bin/env python3
"""
随机密码生成器 - Day 33
支持多种安全级别和自定义选项
"""

import random
import string
import secrets
import base64
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class PasswordStrength(Enum):
    LOW = "low"      # 简单密码
    MEDIUM = "medium" # 中等密码
    HIGH = "high"    # 高强度密码
    EXTREME = "extreme" # 极高强度


@dataclass
class PasswordConfig:
    """密码配置"""
    length: int = 16
    strength: PasswordStrength = PasswordStrength.HIGH
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = True  # 排除易混淆字符
    exclude_similar: bool = True    # 排除相似字符
    custom_chars: Optional[str] = None


class PasswordGenerator:
    """随机密码生成器"""
    
    AMBIGUOUS = "0O1lI|"  # 易混淆字符
    SIMILAR = "0OD8B6G"   # 相似字符
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()
    
    def _get_character_pool(self) -> str:
        """获取字符池"""
        if self.config.custom_chars:
            return self.config.custom_chars
        
        pool = ""
        
        if self.config.use_uppercase:
            pool += string.ascii_uppercase
        if self.config.use_lowercase:
            pool += string.ascii_lowercase
        if self.config.use_digits:
            pool += string.digits
        if self.config.use_symbols:
            pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # 根据强度调整
        if self.config.strength == PasswordStrength.LOW:
            pool = pool[:random.randint(10, 20)]
        elif self.config.strength == PasswordStrength.MEDIUM:
            pool = pool[:random.randint(20, 30)]
        
        # 排除字符
        if self.config.exclude_ambiguous:
            pool = self._exclude_chars(pool, self.AMBIGUOUS)
        if self.config.exclude_similar:
            pool = self._exclude_chars(pool, self.SIMILAR)
        
        return pool
    
    def _exclude_chars(self, pool: str, exclude: str) -> str:
        """排除指定字符"""
        return ''.join(c for c in pool if c not in exclude)
    
    def _ensure_diversity(self, password: str, pool: str) -> str:
        """确保密码包含多种字符类型"""
        required_types = []
        if self.config.use_uppercase and any(c in string.ascii_uppercase for c in password):
            required_types.append(random.choice([c for c in string.ascii_uppercase if c in pool]))
        if self.config.use_lowercase and any(c in string.ascii_lowercase for c in password):
            required_types.append(random.choice([c for c in string.ascii_lowercase if c in pool]))
        if self.config.use_digits and any(c in string.digits for c in password):
            required_types.append(random.choice([c for c in string.digits if c in pool]))
        if self.config.use_symbols and any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            required_types.append(random.choice([c for c in "!@#$%^&*()_+-=[]{}|;:,.<>?" if c in pool]))
        
        # 替换随机位置的字符
        for i, char in enumerate(required_types):
            if char and i < len(password):
                pos = random.randint(0, len(password) - 1)
                password = password[:pos] + char + password[pos + 1:]
        
        return password
    
    def generate(self) -> str:
        """生成密码"""
        pool = self._get_character_pool()
        
        if not pool:
            raise ValueError("字符池为空，请检查配置")
        
        # 使用secrets生成密码（密码学安全）
        password = ''.join(secrets.choice(pool) for _ in range(self.config.length))
        
        # 确保多样性
        password = self._ensure_diversity(password, pool)
        
        return password
    
    def generate_memorable(self, word_count: int = 4, separator: str = "-") -> str:
        """生成易记密码（口令）"""
        words = [
            "apple", "brave", "cloud", "delta", "eagle", "focus", "gamma", "honor",
            "iron", "jumbo", "kite", "lemon", "magic", "navy", "ocean", "prime",
            "quest", "rapid", "solar", "tiger", "ultra", "vista", "water", "xray",
            "youth", "zebra", "alert", "bright", "clear", "dream", "energy", "frost"
        ]
        
        selected = random.sample(words, min(word_count, len(words)))
        result = separator.join(word.capitalize() for word in selected)
        
        # 添加随机数字和符号
        result += f"{random.randint(10, 99)}{random.choice(['!', '@', '#', '$', '%'])}"
        
        return result
    
    def generate_pin(self, length: int = 6) -> str:
        """生成数字PIN码"""
        return ''.join(str(random.randint(0, 9)) for _ in range(length))
    
    def generate_phrase(self, length: int = 32) -> str:
        """生成随机短语（Base64编码）"""
        raw_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(raw_bytes).decode('utf-8')[:length]
    
    def generate_multiple(self, count: int = 5) -> List[str]:
        """生成多个密码"""
        return [self.generate() for _ in range(count)]


def evaluate_password_strength(password: str) -> dict:
    """评估密码强度"""
    score = 0
    feedback = []
    
    length = len(password)
    
    # 长度评分
    if length >= 16:
        score += 25
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    else:
        feedback.append("密码太短，建议至少8位")
    
    # 字符类型评分
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    types_count = sum([has_upper, has_lower, has_digit, has_symbol])
    score += types_count * 15
    
    if not has_upper:
        feedback.append("缺少大写字母")
    if not has_lower:
        feedback.append("缺少小写字母")
    if not has_digit:
        feedback.append("缺少数字")
    if not has_symbol:
        feedback.append("缺少特殊字符")
    
    # 唯一性评分
    unique_ratio = len(set(password)) / length if length > 0 else 0
    if unique_ratio > 0.7:
        score += 10
    
    # 总体评级
    if score >= 85:
        rating = "极强"
    elif score >= 70:
        rating = "强"
    elif score >= 55:
        rating = "中等"
    elif score >= 40:
        rating = "弱"
    else:
        rating = "极弱"
    
    return {
        "password": password,
        "score": min(score, 100),
        "rating": rating,
        "feedback": feedback if feedback else ["密码结构良好"],
        "length": length,
        "entropy": round(secrets.entropy_hint(password) if hasattr(secrets, 'entropy_hint') else 0, 2)
    }


def interactive_mode():
    """交互模式"""
    print("🔐 随机密码生成器 - Day 33")
    print("=" * 40)
    
    generator = PasswordGenerator()
    
    while True:
        print("\n选择生成类型:")
        print("1. 高强度随机密码")
        print("2. 易记口令（word-phrase）")
        print("3. 数字PIN码")
        print("4. 随机短语（Base64）")
        print("5. 评估密码强度")
        print("q. 退出")
        
        choice = input("\n请选择 (1-5/q): ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            config = PasswordConfig(
                length=16,
                strength=PasswordStrength.HIGH
            )
            generator = PasswordGenerator(config)
            pwd = generator.generate()
            result = evaluate_password_strength(pwd)
            print(f"\n生成的密码: {pwd}")
            print(f"强度评级: {result['rating']} ({result['score']}分)")
        elif choice == '2':
            pwd = generator.generate_memorable()
            result = evaluate_password_strength(pwd)
            print(f"\n生成的易记密码: {pwd}")
            print(f"强度评级: {result['rating']} ({result['score']}分)")
        elif choice == '3':
            pwd = generator.generate_pin()
            print(f"\n生成的PIN码: {pwd}")
        elif choice == '4':
            pwd = generator.generate_phrase()
            print(f"\n生成的短语: {pwd}")
        elif choice == '5':
            pwd = input("输入要评估的密码: ")
            result = evaluate_password_strength(pwd)
            print(f"\n强度评级: {result['rating']} ({result['score']}分)")
            for tip in result['feedback']:
                print(f"  • {tip}")
        else:
            print("无效选择，请重试")


def demo():
    """演示函数"""
    print("🔐 随机密码生成器演示 - Day 33")
    print("=" * 50)
    
    generator = PasswordGenerator()
    
    print("\n1. 高强度密码:")
    pwd = generator.generate()
    result = evaluate_password_strength(pwd)
    print(f"   {pwd}")
    print(f"   强度: {result['rating']}")
    
    print("\n2. 易记口令:")
    pwd = generator.generate_memorable()
    result = evaluate_password_strength(pwd)
    print(f"   {pwd}")
    print(f"   强度: {result['rating']}")
    
    print("\n3. PIN码:")
    print(f"   {generator.generate_pin(6)}")
    
    print("\n4. 批量生成5个密码:")
    passwords = generator.generate_multiple(5)
    for i, p in enumerate(passwords, 1):
        result = evaluate_password_strength(p)
        print(f"   {i}. {p} ({result['rating']})")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print(__doc__)
            print("\n使用方法:")
            print("  python password_generator.py        # 交互模式")
            print("  python password_generator.py demo  # 运行演示")
            print("  python password_generator.py -g    # 生成一个密码")
            print("  python password_generator.py -p    # 生成PIN码")
        elif sys.argv[1] == 'demo':
            demo()
        elif sys.argv[1] == '-g':
            generator = PasswordGenerator()
            print(generator.generate())
        elif sys.argv[1] == '-p':
            print(generator.generate_pin())
        else:
            print("未知参数，使用 -h 查看帮助")
    else:
        interactive_mode()
