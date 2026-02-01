#!/usr/bin/env python3
"""
智能数据验证器 (Day 16)
Intelligent Data Validator

功能：
- 数据类型自动检测与验证
- 邮箱、电话号码、URL、身份证等格式验证
- 自定义验证规则
- 批量数据验证
- 验证报告生成
"""

import re
from typing import Any, Callable, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """验证结果"""
    field: str
    value: Any
    is_valid: bool
    error_message: Optional[str] = None
    validated_at: str = None
    
    def __post_init__(self):
        if self.validated_at is None:
            self.validated_at = datetime.now().isoformat()


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.rules: List[Tuple[str, Callable, str]] = []
        self.validation_history: List[ValidationResult] = []
    
    def add_rule(self, field: str, validator: Callable, error_msg: str = "验证失败"):
        """添加验证规则"""
        self.rules.append((field, validator, error_msg))
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str, region: str = "CN") -> bool:
        """验证电话号码"""
        patterns = {
            "CN": r'^1[3-9]\d{9}$',  # 中国手机号
            "US": r'^\+?1?\d{10,15}$',  # 美国电话
            "HK": r'^(\+?852-?)?[5689]\d{7}$',  # 香港电话
        }
        pattern = patterns.get(region, patterns["CN"])
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, url))
    
    def validate_id_card(self, id_card: str) -> bool:
        """验证身份证号（中国）"""
        if len(id_card) != 18:
            return False
        # 校验码验证
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        checksum = "10X98765432"
        sum_val = sum(int(id_card[i]) * factors[i] for i in range(17))
        return id_card[17] == checksum[sum_val % 11]
    
    def validate_ip(self, ip: str) -> bool:
        """验证IP地址"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        parts = ip.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    
    def validate_credit_card(self, card_number: str) -> bool:
        """验证信用卡号（Luhn算法）"""
        digits = card_number.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) not in [13, 15, 16]:
            return False
        # Luhn算法
        total = 0
        is_second = False
        for digit in reversed(digits):
            d = int(digit)
            if is_second:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
            is_second = not is_second
        return total % 10 == 0
    
    def validate_date(self, date_str: str, format: str = "%Y-%m-%d") -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    def validate_between(self, value: int, min_val: int, max_val: int) -> bool:
        """验证数值范围"""
        return min_val <= value <= max_val
    
    def validate_length(self, text: str, min_len: int, max_len: int) -> bool:
        """验证字符串长度"""
        return min_len <= len(text) <= max_len
    
    def validate_pattern(self, text: str, pattern: str) -> bool:
        """验证正则表达式"""
        return bool(re.match(pattern, text))
    
    def validate(self, data: dict) -> List[ValidationResult]:
        """批量验证数据"""
        results = []
        for field, validator, error_msg in self.rules:
            if field in data:
                value = data[field]
                try:
                    is_valid = validator(value)
                    result = ValidationResult(
                        field=field,
                        value=value,
                        is_valid=is_valid,
                        error_message=None if is_valid else error_msg
                    )
                except Exception as e:
                    result = ValidationResult(
                        field=field,
                        value=value,
                        is_valid=False,
                        error_message=f"验证异常: {str(e)}"
                    )
                results.append(result)
                self.validation_history.append(result)
        return results
    
    def validate_single(self, value: Any, validator: Callable, error_msg: str = "验证失败") -> ValidationResult:
        """单个值验证"""
        try:
            is_valid = validator(value)
            return ValidationResult(
                field="single_value",
                value=value,
                is_valid=is_valid,
                error_message=None if is_valid else error_msg
            )
        except Exception as e:
            return ValidationResult(
                field="single_value",
                value=value,
                is_valid=False,
                error_message=f"验证异常: {str(e)}"
            )
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """生成验证报告"""
        total = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total - passed
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║              📋 数据验证报告                           ║
╠════════════════════════════════════════════════════════════╣
║ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<40}║
║ 总验证数: {total:<43}║
║ ✅ 通过: {passed:<45}║
║ ❌ 失败: {failed:<45}║
╚════════════════════════════════════════════════════════════╝
"""
        if failed > 0:
            report += "\n📌 失败详情:\n"
            for r in results:
                if not r.is_valid:
                    report += f"   • {r.field}: {r.value} → {r.error_message}\n"
        else:
            report += "\n🎉 所有验证全部通过！\n"
        
        return report


def demo():
    """演示"""
    validator = DataValidator()
    
    # 添加验证规则
    validator.add_rule("email", validator.validate_email, "邮箱格式不正确")
    validator.add_rule("phone", lambda x: validator.validate_phone(x, "CN"), "手机号格式不正确")
    validator.add_rule("age", lambda x: validator.validate_between(x, 0, 150), "年龄必须在0-150之间")
    validator.add_rule("url", validator.validate_url, "URL格式不正确")
    
    # 测试数据
    test_data = {
        "email": "test@example.com",
        "phone": "13812345678",
        "age": 25,
        "url": "https://www.example.com"
    }
    
    # 验证
    results = validator.validate(test_data)
    
    # 生成报告
    report = validator.generate_report(results)
    print(report)
    
    # 单独验证示例
    print("🔍 单独验证示例:")
    
    # 身份证验证
    id_card = "110101199001011234"
    result = validator.validate_single(id_card, validator.validate_id_card, "身份证号不正确")
    print(f"   身份证 {id_card}: {'✅ 有效' if result.is_valid else '❌ 无效'}")
    
    # IP验证
    ip = "192.168.1.1"
    result = validator.validate_single(ip, validator.validate_ip, "IP地址不正确")
    print(f"   IP {ip}: {'✅ 有效' if result.is_valid else '❌ 无效'}")
    
    # 信用卡验证
    card = "4532 1234 5678 9012"
    result = validator.validate_single(card, validator.validate_credit_card, "信用卡号不正确")
    print(f"   信用卡 {card}: {'✅ 有效' if result.is_valid else '❌ 无效'}")


if __name__ == "__main__":
    demo()
