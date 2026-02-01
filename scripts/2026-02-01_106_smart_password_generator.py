#!/usr/bin/env python3
"""
🔐 智能密码生成器 - Smart Password Generator
============================================

一个功能强大、安全可靠的密码生成工具。

功能特点:
- 🎲 多种密码强度（弱/中等/强/超强）
- 🔢 支持自定义长度
- 💪 包含字符类型：大小写字母、数字、特殊字符
- 📊 密码强度实时评估
- 🎯 可记忆密码模式（基于助记词）
- 📝 历史记录管理
- 🔒 安全随机数生成

作者: MarsAssistant
日期: 2026-02-01
"""

import random
import string
import secrets
import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class PasswordStrength(Enum):
    """密码强度等级"""
    WEAK = "弱"
    MEDIUM = "中等"
    STRONG = "强"
    VERY_STRONG = "超强"


@dataclass
class PasswordResult:
    """密码生成结果"""
    password: str
    strength: PasswordStrength
    entropy: float
    length: int
    char_types: List[str]
    timestamp: str


class SmartPasswordGenerator:
    """智能密码生成器"""
    
    # 字符集
    LOWERCASE = string.ascii_lowercase      # 小写字母
    UPPERCASE = string.ascii_uppercase      # 大写字母
    DIGITS = string.digits                  # 数字
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"  # 特殊字符
    
    # 助记词列表（用于生成可记忆密码）
    MNEMONIC_WORDS = [
        # 动物
        "tiger", "dragon", "phoenix", "eagle", "wolf", "lion", "bear", "hawk",
        "dolphin", "whale", "shark", "owl", "falcon", "raven", "swan", "deer",
        # 自然
        "sun", "moon", "star", "ocean", "river", "mountain", "forest", "cloud",
        "rain", "snow", "wind", "fire", "earth", "sky", "wave", "rock",
        # 颜色
        "blue", "green", "red", "gold", "silver", "purple", "orange", "pink",
        # 动作
        "run", "jump", "fly", "swim", "dance", "sing", "walk", "climb",
        # 物品
        "book", "tree", "flower", "garden", "house", "bridge", "castle", "tower",
        # 情感
        "happy", "bright", "swift", "calm", "brave", "wise", "kind", "gentle"
    ]
    
    def __init__(self, history_file: str = "~/.password_history.json"):
        self.history_file = os.path.expanduser(history_file)
        self.history: List[Dict] = []
        self._load_history()
    
    def _load_history(self) -> None:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
    
    def _save_history(self) -> None:
        """保存历史记录"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-100:], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存历史记录失败: {e}")
    
    def calculate_entropy(self, password: str) -> float:
        """计算密码熵值（比特）"""
        if not password:
            return 0.0
        
        charset_size = 0
        if any(c in self.LOWERCASE for c in password):
            charset_size += 26
        if any(c in self.UPPERCASE for c in password):
            charset_size += 26
        if any(c in self.DIGITS for c in password):
            charset_size += 10
        if any(c in self.SPECIAL_CHARS for c in password):
            charset_size += len(self.SPECIAL_CHARS)
        
        if charset_size == 0:
            return 0.0
        
        return len(password) * math.log2(charset_size)
    
    def evaluate_strength(self, password: str) -> Tuple[PasswordStrength, float]:
        """评估密码强度"""
        entropy = self.calculate_entropy(password)
        length = len(password)
        
        # 字符类型计数
        has_lower = any(c in self.LOWERCASE for c in password)
        has_upper = any(c in self.UPPERCASE for c in password)
        has_digit = any(c in self.DIGITS for c in password)
        has_special = any(c in self.SPECIAL_CHARS for c in password)
        
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        
        # 强度判断
        if length < 8 or char_types < 2 or entropy < 40:
            strength = PasswordStrength.WEAK
        elif length < 12 or char_types < 3 or entropy < 60:
            strength = PasswordStrength.MEDIUM
        elif length < 16 or char_types < 4 or entropy < 80:
            strength = PasswordStrength.STRONG
        else:
            strength = PasswordStrength.VERY_STRONG
        
        return strength, entropy
    
    def get_char_types(self, password: str) -> List[str]:
        """获取密码包含的字符类型"""
        types = []
        if any(c in self.LOWERCASE for c in password):
            types.append("小写字母")
        if any(c in self.UPPERCASE for c in password):
            types.append("大写字母")
        if any(c in self.DIGITS for c in password):
            types.append("数字")
        if any(c in self.SPECIAL_CHARS for c in password):
            types.append("特殊字符")
        return types
    
    def generate_random_password(
        self,
        length: int = 16,
        use_lowercase: bool = True,
        use_uppercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_ambiguous: bool = False
    ) -> str:
        """生成随机密码"""
        charset = ""
        
        if use_lowercase:
            if exclude_ambiguous:
                charset += self.LOWERCASE.replace('l', '').replace('o', '')
            else:
                charset += self.LOWERCASE
        
        if use_uppercase:
            if exclude_ambiguous:
                charset += self.UPPERCASE.replace('I', '').replace('O', '')
            else:
                charset += self.UPPERCASE
        
        if use_digits:
            if exclude_ambiguous:
                charset += self.DIGITS.replace('0', '').replace('1', '')
            else:
                charset += self.DIGITS
        
        if use_special:
            charset += self.SPECIAL_CHARS
        
        if not charset:
            raise ValueError("至少需要选择一种字符类型")
        
        # 使用secrets模块生成密码学安全的随机数
        password = ''.join(secrets.choice(charset) for _ in range(length))
        
        # 确保包含每种选中的字符类型
        if use_lowercase:
            password = password.replace(
                random.choice(password),
                secrets.choice(self.LOWERCASE), 1
            )
        if use_uppercase:
            password = password.replace(
                random.choice(password),
                secrets.choice(self.UPPERCASE), 1
            )
        if use_digits:
            password = password.replace(
                random.choice(password),
                secrets.choice(self.DIGITS), 1
            )
        if use_special:
            password = password.replace(
                random.choice(password),
                secrets.choice(self.SPECIAL_CHARS), 1
            )
        
        return password
    
    def generate_memorable_password(
        self,
        num_words: int = 4,
        separator: str = "-",
        capitalize: bool = True,
        add_number: bool = True,
        add_special: bool = True
    ) -> str:
        """生成可记忆的密码（基于助记词）"""
        if num_words < 2:
            num_words = 2
        if num_words > 8:
            num_words = 8
        
        # 随机选择单词
        words = [secrets.choice(self.MNEMONIC_WORDS) for _ in range(num_words)]
        
        if capitalize:
            words = [word.capitalize() for word in words]
        
        password = separator.join(words)
        
        if add_number:
            password += separator + str(secrets.randbelow(100))
        
        if add_special:
            password = password.replace(separator, secrets.choice(self.SPECIAL_CHARS), 1)
        
        return password
    
    def generate_pin(self, length: int = 6, allow_repeat: bool = True) -> str:
        """生成PIN码"""
        digits = list(self.DIGITS)
        if not allow_repeat:
            if length > len(digits):
                length = len(digits)
            return ''.join(secrets.choice(digits) for _ in range(length))
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    def generate_password(
        self,
        mode: str = "random",
        length: int = 16,
        strength: str = "strong"
    ) -> PasswordResult:
        """生成密码的主方法"""
        if mode == "memorable":
            password = self.generate_memorable_password(num_words=4)
        elif mode == "pin":
            password = self.generate_pin(length=length)
        else:
            # 根据强度设置参数
            if strength == "weak":
                length = max(8, length)
                password = self.generate_random_password(
                    length=length, use_special=False, use_uppercase=False
                )
            elif strength == "medium":
                length = max(12, length)
                password = self.generate_random_password(
                    length=length, use_special=False
                )
            elif strength == "very_strong":
                length = max(20, length)
                password = self.generate_random_password(
                    length=length, exclude_ambiguous=True
                )
            else:  # strong
                password = self.generate_random_password(length=length)
        
        strength_level, entropy = self.evaluate_strength(password)
        char_types = self.get_char_types(password)
        
        result = PasswordResult(
            password=password,
            strength=strength_level,
            entropy=entropy,
            length=len(password),
            char_types=char_types,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存到历史记录
        self.history.append(asdict(result))
        self._save_history()
        
        return result
    
    def get_strength_icon(self, strength: PasswordStrength) -> str:
        """获取强度图标"""
        icons = {
            PasswordStrength.WEAK: "🔴",
            PasswordStrength.MEDIUM: "🟡",
            PasswordStrength.STRONG: "🟢",
            PasswordStrength.VERY_STRONG: "💚"
        }
        return icons.get(strength, "⚪")
    
    def print_result(self, result: PasswordResult) -> None:
        """打印密码结果"""
        print("\n" + "="*50)
        print("🔐 生成密码结果")
        print("="*50)
        print(f"密码: {result.password}")
        print(f"强度: {self.get_strength_icon(result.strength)} {result.strength.value}")
        print(f"熵值: {result.entropy:.1f} bits")
        print(f"长度: {result.length} 字符")
        print(f"类型: {', '.join(result.char_types)}")
        print("="*50 + "\n")
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史记录"""
        return self.history[-limit:]
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history = []
        self._save_history()
        print("✅ 历史记录已清空")


# 导入math模块（在calculate_entropy中使用）
import math


def demo():
    """演示密码生成器的使用"""
    generator = SmartPasswordGenerator()
    
    print("🎯 智能密码生成器演示")
    print("="*50)
    
    # 1. 生成强密码
    print("\n1️⃣ 生成强随机密码:")
    result = generator.generate_password(mode="random", strength="strong")
    generator.print_result(result)
    
    # 2. 生成可记忆密码
    print("2️⃣ 生成可记忆密码:")
    result = generator.generate_password(mode="memorable")
    generator.print_result(result)
    
    # 3. 生成PIN码
    print("3️⃣ 生成6位PIN码:")
    result = generator.generate_password(mode="pin", length=6)
    generator.print_result(result)
    
    # 4. 生成超强密码
    print("4️⃣ 生成超强密码（20位，无歧义字符）:")
    result = generator.generate_password(mode="random", strength="very_strong", length=20)
    generator.print_result(result)
    
    # 5. 生成弱密码（仅演示）
    print("5️⃣ 生成弱密码（仅字母，仅演示）:")
    weak_password = generator.generate_random_password(
        length=8, use_digits=False, use_special=False
    )
    print(f"密码: {weak_password}")
    
    # 显示历史记录
    print("\n📜 最近生成记录:")
    for item in generator.get_history(5):
        print(f"  • {item['password'][:20]}... | {item['strength']}")


def interactive_mode():
    """交互模式"""
    generator = SmartPasswordGenerator()
    
    while True:
        print("\n🔐 智能密码生成器")
        print("1. 生成随机密码")
        print("2. 生成可记忆密码")
        print("3. 生成PIN码")
        print("4. 查看历史记录")
        print("5. 清空历史记录")
        print("q. 退出")
        
        choice = input("\n请选择: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            strength = input("选择强度 (weak/medium/strong/very_strong): ").strip()
            result = generator.generate_password(mode="random", strength=strength)
            generator.print_result(result)
        elif choice == '2':
            result = generator.generate_password(mode="memorable")
            generator.print_result(result)
        elif choice == '3':
            length = input("PIN长度 (默认6): ").strip()
            length = int(length) if length else 6
            result = generator.generate_password(mode="pin", length=length)
            generator.print_result(result)
        elif choice == '4':
            print("\n📜 历史记录:")
            for item in generator.get_history():
                print(f"  • {item['password']}")
        elif choice == '5':
            generator.clear_history()
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式
        generator = SmartPasswordGenerator()
        
        if sys.argv[1] in ['-h', '--help']:
            print(__doc__)
            print("\n用法:")
            print("  python smart_password_generator.py          # 交互模式")
            print("  python smart_password_generator.py random   # 生成随机强密码")
            print("  python smart_password_generator.py memorable # 生成可记忆密码")
            print("  python smart_password_generator.py pin      # 生成PIN码")
        elif sys.argv[1] == 'random':
            result = generator.generate_password(mode="random")
            generator.print_result(result)
        elif sys.argv[1] == 'memorable':
            result = generator.generate_password(mode="memorable")
            generator.print_result(result)
        elif sys.argv[1] == 'pin':
            length = int(sys.argv[2]) if len(sys.argv) > 2 else 6
            result = generator.generate_password(mode="pin", length=length)
            generator.print_result(result)
        else:
            print("❌ 未知参数，使用 -h 查看帮助")
    else:
        # 演示模式或交互模式
        demo()
        # interactive_mode()
