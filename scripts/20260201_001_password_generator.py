#!/usr/bin/env python3
"""
智能密码生成器
Smart Password Generator

AI Code Journey - Day 1
"""

import random
import string
from typing import List

class PasswordGenerator:
    """安全密码生成器类"""
    
    def __init__(self):
        self.char_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
    
    def generate(self, length: int = 16, use_upper: bool = True,
                 use_digits: bool = True, use_symbols: bool = True) -> str:
        """
        生成安全密码
        
        Args:
            length: 密码长度 (默认16)
            use_upper: 包含大写字母
            use_digits: 包含数字
            use_symbols: 包含特殊符号
        
        Returns:
            生成的密码字符串
        """
        chars = string.ascii_lowercase
        
        if use_upper:
            chars += self.char_sets['uppercase']
        if use_digits:
            chars += self.char_sets['digits']
        if use_symbols:
            chars += self.char_sets['symbols']
        
        # 确保至少包含每种要求的字符类型
        password_chars = []
        if use_upper:
            password_chars.append(random.choice(self.char_sets['uppercase']))
        if use_digits:
            password_chars.append(random.choice(self.char_sets['digits']))
        if use_symbols:
            password_chars.append(random.choice(self.char_sets['symbols']))
        
        # 填充剩余长度
        for _ in range(length - len(password_chars)):
            password_chars.append(random.choice(chars))
        
        # 打乱顺序
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def generate_memorable(self, words: List[str] = None, separator: str = '-') -> str:
        """
        生成易记密码 (如: Apple-Coffee-2024!)
        """
        if words is None:
            words = ['apple', 'brave', 'cloud', 'delta', 'eagle', 'focus', 
                     'green', 'house', 'igloo', 'jolly', 'kite', 'lemon']
        
        word1 = random.choice(words).capitalize()
        word2 = random.choice([w for w in words if w != words[words.index(word1)-1]]).capitalize()
        number = random.randint(1000, 9999)
        symbol = random.choice('!@#$%')
        
        return f"{word1}{separator}{word2}{number}{symbol}"

def main():
    """演示密码生成器"""
    generator = PasswordGenerator()
    
    print('=== AI Code Journey: 智能密码生成器 ===
')
    
    # 生成标准密码
    password = generator.generate(length=20)
    print(f'标准密码: {password}')
    print(f'长度: {len(password)}')
    
    # 生成易记密码
    memorable = generator.generate_memorable()
    print(f'
易记密码: {memorable}')
    
    print('
✅ 密码生成完成!')

if __name__ == '__main__':
    main()
