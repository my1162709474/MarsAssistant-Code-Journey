"""
密码生成器 - Secure Password Generator
支持多种密码类型和强度选项
"""

import random
import string
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import math


class PasswordStrength(Enum):
    """密码强度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class PasswordConfig:
    """密码配置"""
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_special: bool = True
    exclude_ambiguous: bool = False
    exclude_similar: bool = False


class PasswordGenerator:
    """密码生成器类"""
    
    # 模糊字符 (容易混淆)
    AMBIGUOUS_CHARS = '0O1lI|'
    
    # 相似字符
    SIMILAR_PAIRS = {'1': 'l', '0': 'O', '5': 'S', '8': 'B'}
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()
    
    def generate(self) -> str:
        """生成单个密码"""
        alphabet = self._build_alphabet()
        
        if len(alphabet) < self.config.length:
            raise ValueError("密码长度超过可用字符集大小")
        
        # 使用secrets模块确保密码学安全
        password_chars = []
        mandatory_chars = self._get_mandatory_chars()
        
        # 确保包含必需字符
        for char_list in mandatory_chars:
            if char_list:
                password_chars.append(secrets.choice(char_list))
        
        # 填充剩余字符
        remaining = self.config.length - len(password_chars)
        if remaining > 0:
            password_chars.extend(secrets.choice(alphabet) for _ in range(remaining))
        
        # 打乱字符顺序
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def generate_multiple(self, count: int = 10) -> List[str]:
        """批量生成多个密码"""
        return [self.generate() for _ in range(count)]
    
    def generate_memorable(self, word_count: int = 4, separator: str = '-') -> str:
        """生成易记密码 (单词组合形式)"""
        words = self._get_common_words()
        selected = random.sample(words, min(word_count, len(words)))
        
        # 首字母大写
        selected = [word.capitalize() for word in selected]
        
        # 添加数字
        selected[-1] = selected[-1] + str(random.randint(10, 99))
        
        return separator.join(selected)
    
    def calculate_entropy(self, password: str) -> float:
        """计算密码熵值"""
        pool_size = 0
        
        if any(c.isupper() for c in password):
            pool_size += 26
        if any(c.islower() for c in password):
            pool_size += 26
        if any(c.isdigit() for c in password):
            pool_size += 10
        if any(not c.isalnum() for c in password):
            pool_size += 32
        
        if pool_size == 0:
            return 0.0
        
        entropy = len(password) * math.log2(pool_size)
        return entropy
    
    def evaluate_strength(self, password: str) -> tuple[PasswordStrength, str]:
        """评估密码强度"""
        entropy = self.calculate_entropy(password)
        
        if entropy < 40:
            return PasswordStrength.LOW, "非常弱 - 容易破解"
        elif entropy < 60:
            return PasswordStrength.MEDIUM, "中等 - 建议增强"
        elif entropy < 80:
            return PasswordStrength.HIGH, "强 - 安全性好"
        else:
            return PasswordStrength.EXTREME, "极强 - 安全性极佳"
    
    def _build_alphabet(self) -> str:
        """构建字符集"""
        chars = []
        
        if self.config.use_uppercase:
            chars.extend(string.ascii_uppercase)
        if self.config.use_lowercase:
            chars.extend(string.ascii_lowercase)
        if self.config.use_digits:
            chars.extend(string.digits)
        if self.config.use_special:
            chars.extend('!@#$%^&*()_+-=[]{}|;:,.<>?')
        
        # 排除模糊字符
        if self.config.exclude_ambiguous:
            chars = [c for c in chars if c not in self.AMBIGUOUS_CHARS]
        
        # 排除相似字符
        if self.config.exclude_similar:
            all_similar = set()
            for pair in self.SIMILAR_PAIRS.values():
                all_similar.update(pair)
            chars = [c for c in chars if c not in all_similar]
        
        return ''.join(chars)
    
    def _get_mandatory_chars(self) -> List[str]:
        """获取必须包含的字符列表"""
        mandatory = []
        
        if self.config.use_uppercase:
            uppercase = string.ascii_uppercase
            if self.config.exclude_ambiguous:
                uppercase = ''.join(c for c in uppercase if c not in self.AMBIGUOUS_CHARS)
            mandatory.append(uppercase)
        
        if self.config.use_lowercase:
            lowercase = string.ascii_lowercase
            if self.config.exclude_ambiguous:
                lowercase = ''.join(c for c in lowercase if c not in self.AMBIGUOUS_CHARS)
            mandatory.append(lowercase)
        
        if self.config.use_digits:
            digits = string.digits
            if self.config.exclude_ambiguous:
                digits = ''.join(c for c in digits if c not in self.AMBIGUOUS_CHARS)
            mandatory.append(digits)
        
        if self.config.use_special:
            mandatory.append('!@#$%^&*()_+-=[]{}|;:,.<>?')
        
        return mandatory
    
    def _get_common_words(self) -> List[str]:
        """获取常用单词列表"""
        return [
            'apple', 'brave', 'cloud', 'delta', 'eagle', 'focus', 'grace',
            'honor', 'input', 'jump', 'karma', 'lemon', 'magic', 'nexus',
            'ocean', 'power', 'quest', 'river', 'solar', 'tiger', 'ultra',
            'vision', 'water', 'xray', 'youth', 'zebra', 'amber', 'blaze',
            'coral', 'drift', 'ember', 'flame', 'grove', 'haven', 'index',
            'jade', 'knight', 'light', 'mount', 'noble', 'orbit', 'prism',
            'quick', 'realm', 'swift', 'unity', 'vivid', 'waltz', 'xenon'
        ]


def demo():
    """演示密码生成器功能"""
    print("🔐 Password Generator - 密码生成器")
    print("=" * 50)
    
    # 创建生成器
    generator = PasswordGenerator()
    
    # 1. 生成强密码
    print("\n1. 随机强密码:")
    password = generator.generate()
    strength, desc = generator.evaluate_strength(password)
    print(f"   {password}")
    print(f"   强度: {strength.value} - {desc}")
    
    # 2. 自定义配置
    print("\n2. 自定义配置 (20位, 不含模糊字符):")
    config = PasswordConfig(
        length=20,
        exclude_ambiguous=True,
        exclude_similar=True
    )
    custom_gen = PasswordGenerator(config)
    print(f"   {custom_gen.generate()}")
    
    # 3. 易记密码
    print("\n3. 易记密码 (单词组合):")
    print(f"   {generator.generate_memorable()}")
    
    # 4. 批量生成
    print("\n4. 批量生成 (5个密码):")
    passwords = generator.generate_multiple(5)
    for pwd in passwords:
        print(f"   {pwd}")
    
    # 5. 不同强度
    print("\n5. 不同长度密码对比:")
    for length in [8, 12, 16, 24]:
        config = PasswordConfig(length=length)
        gen = PasswordGenerator(config)
        pwd = gen.generate()
        strength, _ = gen.evaluate_strength(pwd)
        print(f"   {length}位: {pwd} [{strength.value}]")


if __name__ == "__main__":
    demo()
