#!/usr/bin/env python3
"""
密码强度分析器 - Day 024
一个智能检测密码强度的工具，包含多种安全检测规则
"""

import re
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class PasswordStrength(Enum):
    VERY_WEAK = 1
    WEAK = 2
    FAIR = 3
    GOOD = 4
    STRONG = 5
    EXCELLENT = 6


@dataclass
class AnalysisResult:
    strength: PasswordStrength
    score: int  # 0-100
    feedback: List[str]
    suggestions: List[str]
    crack_time_estimate: str


class PasswordAnalyzer:
    """密码强度分析器"""
    
    def __init__(self):
        self.common_passwords = {
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'login', 'passw0rd', 'hello'
        }
        
        self.patterns = {
            'sequential': r'(?:012|123|234|345|456|567|678|789|890)',
            'repeated': r'(.)\1{2,}',
            'keyboard': r'(?:qwer|asdf|zxcv|1234|poiuy|lkjh|mnbvc)',
            'year': r'(?:19[5-9]\d|20[0-2]\d)',
            'date': r'(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])'
        }
    
    def analyze(self, password: str) -> AnalysisResult:
        """分析密码强度"""
        if not password:
            return self._empty_result()
        
        score = 0
        feedback = []
        suggestions = []
        
        # 基础分数
        length = len(password)
        score += min(length * 4, 40)  # 最多40分
        
        # 字符类型得分
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./>?]', password))
        
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        score += char_types * 10  # 最多40分
        
        # 检测问题
        issues = []
        
        # 检查常见密码
        if password.lower() in self.common_passwords:
            score -= 50
            issues.append('使用了常见密码')
        
        # 检查顺序数字
        if re.search(self.patterns['sequential'], password):
            score -= 10
            issues.append('包含顺序数字')
        
        # 检查重复字符
        if re.search(self.patterns['repeated'], password):
            score -= 10
            issues.append('包含重复字符')
        
        # 检查键盘模式
        if re.search(self.patterns['keyboard'], password.lower()):
            score -= 15
            issues.append('包含键盘排列模式')
        
        # 检查年份
        if re.search(self.patterns['year'], password):
            score -= 5
            issues.append('可能包含出生年份')
        
        # 检查日期
        if re.search(self.patterns['date'], password):
            score -= 5
            issues.append('可能包含日期')
        
        # 长度建议
        if length < 8:
            suggestions.append('密码至少需要8个字符')
        elif length < 12:
            suggestions.append('建议使用12个字符以上的密码')
        
        # 字符类型建议
        if not has_special:
            suggestions.append('添加特殊字符提高安全性')
        if not has_upper:
            suggestions.append('添加大写字母')
        if not has_digit:
            suggestions.append('添加数字')
        if length > 16 and not has_special:
            suggestions.append('长密码没有特殊字符，安全性没有充分利用')
        
        # 计算最终分数
        score = max(0, min(100, score))
        
        # 估算破解时间（简化版）
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32
        if charset_size == 0:
            charset_size = 26
        
        combinations = charset_size ** length
        crack_time = self._estimate_crack_time(combinations)
        
        # 确定强度等级
        if score >= 90:
            strength = PasswordStrength.EXCELLENT
        elif score >= 75:
            strength = PasswordStrength.STRONG
        elif score >= 60:
            strength = PasswordStrength.GOOD
        elif score >= 40:
            strength = PasswordStrength.FAIR
        elif score >= 20:
            strength = PasswordStrength.WEAK
        else:
            strength = PasswordStrength.VERY_WEAK
        
        return AnalysisResult(
            strength=strength,
            score=score,
            feedback=issues,
            suggestions=suggestions,
            crack_time_estimate=crack_time
        )
    
    def _empty_result(self) -> AnalysisResult:
        return AnalysisResult(
            strength=PasswordStrength.VERY_WEAK,
            score=0,
            feedback=['密码为空'],
            suggestions=['请输入密码'],
            crack_time_estimate='N/A'
        )
    
    def _estimate_crack_time(self, combinations: int) -> str:
        """估算破解时间（假设每秒100亿次尝试）"""
        guesses_per_second = 10_000_000_000
        seconds = combinations / guesses_per_second
        
        if seconds < 1:
            return '瞬间'
        elif seconds < 60:
            return f'{int(seconds)}秒'
        elif seconds < 3600:
            return f'{int(seconds/60)}分钟'
        elif seconds < 86400:
            return f'{int(seconds/3600)}小时'
        elif seconds < 31536000:
            return f'{int(seconds/86400)}天'
        elif seconds < 31536000 * 100:
            return f'{int(seconds/31536000)}年'
        elif seconds < 31536000 * 1000000:
            return f'{int(seconds/31536000/1000)}千年'
        else:
            return '宇宙年龄级'
    
    def check_breached(self, password: str) -> bool:
        """检查密码是否在泄露库中（模拟）"""
        # 实际应该使用 haveibeenpwned.com 的 API
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        
        # 这里模拟返回（实际应调用API）
        return False


def main():
    """主函数 - 交互式密码分析"""
    analyzer = PasswordAnalyzer()
    
    print("🔐 密码强度分析器 - Day 024")
    print("=" * 40)
    
    while True:
        password = input("\n请输入密码（输入q退出）: ")
        
        if password.lower() == 'q':
            break
        
        result = analyzer.analyze(password)
        
        print(f"\n📊 分析结果:")
        print(f"强度: {result.strength.name}")
        print(f"分数: {result.score}/100")
        print(f"估算破解时间: {result.crack_time_estimate}")
        
        if result.feedback:
            print(f"\n⚠️  问题:")
            for f in result.feedback:
                print(f"  - {f}")
        
        if result.suggestions:
            print(f"\n💡 建议:")
            for s in result.suggestions:
                print(f"  - {s}")
        
        # 强度可视化
        bars = '█' * (result.score // 10) + '░' * (10 - result.score // 10)
        print(f"\n[{bars}] {result.score}%")


if __name__ == '__main__':
    main()
