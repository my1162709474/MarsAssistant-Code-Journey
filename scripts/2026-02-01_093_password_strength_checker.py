#!/usr/bin/env python3
"""
🔐 密码强度检测器
检查密码强度并提供改进建议
"""

import re
import hashlib
import os
from datetime import datetime

class PasswordStrengthChecker:
    """密码强度检测器类"""
    
    def __init__(self):
        self.common_passwords = [
            "password", "123456", "12345678", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
    
    def check_length(self, password: str) -> dict:
        """检查密码长度"""
        length = len(password)
        score = min(length * 2, 20)  # 最多20分
        status = "weak"
        
        if length >= 16:
            status = "excellent"
            score = 20
        elif length >= 12:
            status = "strong"
        elif length >= 8:
            status = "medium"
        
        return {
            "score": score,
            "status": status,
            "message": f"长度 {length} 字符",
            "tips": "密码越长越安全，建议至少12位" if length < 12 else ""
        }
    
    def check_complexity(self, password: str) -> dict:
        """检查密码复杂度"""
        score = 0
        checks = []
        
        # 大写字母
        if re.search(r'[A-Z]', password):
            score += 10
            checks.append("✓ 包含大写字母")
        else:
            checks.append("✗ 缺少大写字母")
        
        # 小写字母
        if re.search(r'[a-z]', password):
            score += 10
            checks.append("✓ 包含小写字母")
        else:
            checks.append("✗ 缺少小写字母")
        
        # 数字
        if re.search(r'\d', password):
            score += 10
            checks.append("✓ 包含数字")
        else:
            checks.append("✗ 缺少数字")
        
        # 特殊字符
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
            checks.append("✓ 包含特殊字符")
        else:
            checks.append("✗ 缺少特殊字符")
        
        return {
            "score": score,
            "checks": checks,
            "status": "excellent" if score >= 45 else "good" if score >= 30 else "weak"
        }
    
    def check_patterns(self, password: str) -> dict:
        """检查常见模式"""
        score = 25
        issues = []
        
        # 连续数字
        if re.search(r'(?:012|123|234|345|456|567|678|789|890)', password):
            score -= 10
            issues.append("⚠ 包含连续数字序列")
        
        # 连续字母
        if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mnop|nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)', password.lower()):
            score -= 10
            issues.append("⚠ 包含连续字母序列")
        
        # 重复字符
        if re.search(r'(.)\1{2,}', password):
            score -= 15
            issues.append("⚠ 包含重复字符")
        
        # 键盘模式
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', '123qwe']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                score -= 15
                issues.append(f"⚠ 包含键盘模式: {pattern}")
        
        return {
            "score": max(0, score),
            "issues": issues,
            "status": "excellent" if score >= 20 else "good" if score >= 10 else "weak"
        }
    
    def check_breached(self, password: str) -> bool:
        """检查密码是否在泄露库中 (模拟检查)"""
        # 实际应该使用 haveibeenpwned API
        # 这里使用常见密码列表模拟
        return password.lower() in self.common_passwords
    
    def calculate_entropy(self, password: str) -> float:
        """计算密码熵值"""
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
        
        if charset_size == 0:
            return 0
        
        entropy = len(password) * math.log2(charset_size)
        return round(entropy, 2)
    
    def generate_suggestion(self, password: str) -> str:
        """生成改进建议"""
        suggestions = []
        
        if len(password) < 12:
            suggestions.append("• 增加密码长度到12位以上")
        
        if not re.search(r'[A-Z]', password):
            suggestions.append("• 添加大写字母")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("• 添加特殊字符")
        
        if not suggestions:
            suggestions.append("• 您的密码已经很好了！")
        
        return "\n".join(suggestions)
    
    def analyze(self, password: str) -> dict:
        """综合分析密码强度"""
        length_result = self.check_length(password)
        complexity_result = self.check_complexity(password)
        patterns_result = self.check_patterns(password)
        
        # 计算总分
        total_score = (
            length_result["score"] * 0.3 +
            complexity_result["score"] * 0.4 +
            patterns_result["score"] * 0.3
        )
        
        is_breached = self.check_breached(password)
        entropy = self.calculate_entropy(password)
        
        # 确定总体评级
        if is_breached:
            overall = "danger"
            rating = "🔴 危险"
        elif total_score >= 80:
            overall = "excellent"
            rating = "🟢 优秀"
        elif total_score >= 60:
            overall = "good"
            rating = "🔵 良好"
        elif total_score >= 40:
            overall = "medium"
            rating = "🟡 一般"
        else:
            overall = "weak"
            rating = "🟠 较弱"
        
        return {
            "rating": rating,
            "overall_score": round(total_score, 1),
            "length": length_result,
            "complexity": complexity_result,
            "patterns": patterns_result,
            "is_breached": is_breached,
            "entropy": entropy,
            "suggestions": self.generate_suggestion(password)
        }
    
    def print_report(self, password: str):
        """打印详细报告"""
        result = self.analyze(password)
        
        print("\n" + "=" * 50)
        print("🔐 密码强度分析报告")
        print("=" * 50)
        print(f"\n📊 总体评级: {result['rating']}")
        print(f"📈 综合得分: {result['overall_score']}/100")
        print(f"🎲 信息熵: {result['entropy']} bits")
        
        if result['is_breached']:
            print("\n⚠️  警告: 此密码在常见泄露列表中！")
            print("   请立即更换密码！")
        
        print(f"\n📏 长度检查: {result['length']['status']} ({result['length']['message']})")
        if result['length']['tips']:
            print(f"   💡 {result['length']['tips']}")
        
        print(f"\n🔧 复杂度检查: {result['complexity']['status']}")
        for check in result['complexity']['checks']:
            print(f"   {check}")
        
        if result['patterns']['issues']:
            print(f"\n⚡ 模式检查发现问题:")
            for issue in result['patterns']['issues']:
                print(f"   {issue}")
        
        print(f"\n💡 改进建议:")
        print(result['suggestions'])
        print("\n" + "=" * 50 + "\n")


def main():
    """主函数"""
    checker = PasswordStrengthChecker()
    
    print("🔐 密码强度检测器")
    print("输入 'quit' 退出\n")
    
    while True:
        password = input("请输入要检查的密码: ")
        
        if password.lower() == 'quit':
            print("再见！安全第一！🔒")
            break
        
        if not password:
            print("请输入密码！\n")
            continue
        
        # 显示强度条
        result = checker.analyze(password)
        bar_length = int(result['overall_score'] // 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        print(f"\n强度: [{bar}] {result['overall_score']:.1f}%")
        checker.print_report(password)


if __name__ == "__main__":
    import math
    main()
