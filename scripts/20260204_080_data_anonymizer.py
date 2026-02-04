#!/usr/bin/env python3
"""
智能数据脱敏工具 - Smart Data Anonymizer
======================================
自动检测和脱敏敏感数据，保护隐私安全。

功能:
- 邮箱地址脱敏
- 手机号码脱敏
- 身份证号脱敏
- 银行卡号脱敏
- IP地址脱敏
- 自定义规则支持

作者: MarsAssistant
日期: 2026-02-04
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class AnonymizationStrategy(Enum):
    """脱敏策略"""
    MASK = "mask"           # 替换为*号
    HASH = "hash"           # 哈希处理
    PARTIAL = "partial"     # 部分保留
    REMOVE = "remove"       # 完全移除
    FAKE = "fake"           # 替换为假数据


@dataclass
class Rule:
    """脱敏规则"""
    name: str
    pattern: re.Pattern
    strategy: AnonymizationStrategy
    replacement: Optional[str] = None
    preserve_length: bool = False


class DataAnonymizer:
    """智能数据脱敏器"""
    
    # 默认脱敏规则
    DEFAULT_RULES = [
        # 邮箱地址: test@example.com -> t***@example.com
        Rule(
            name="email",
            pattern=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            strategy=AnonymizationStrategy.PARTIAL,
            preserve_length=False
        ),
        # 手机号码: 13812345678 -> 138****5678
        Rule(
            name="phone",
            pattern=re.compile(r'\b(1[3-9]\d{9})\b'),
            strategy=AnonymizationStrategy.PARTIAL,
            preserve_length=True
        ),
        # 身份证号: 110101199001011234 -> 1101***********1234
        Rule(
            name="id_card",
            pattern=re.compile(r'\b(\d{17}[\dXx])\b'),
            strategy=AnonymizationStrategy.PARTIAL,
            preserve_length=True
        ),
        # 银行卡号: 6222021234567890 -> 6222**********7890
        Rule(
            name="bank_card",
            pattern=re.compile(r'\b(\d{16,19})\b'),
            strategy=AnonymizationStrategy.PARTIAL,
            preserve_length=True
        ),
        # IP地址: 192.168.1.100 -> 192.***.1.100
        Rule(
            name="ip_address",
            pattern=re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            strategy=AnonymizationStrategy.PARTIAL,
            preserve_length=True
        ),
        # 信用卡CVV: 123 -> ***
        Rule(
            name="cvv",
            pattern=re.compile(r'\b(\d{3,4})\b'),
            strategy=AnonymizationStrategy.MASK,
            preserve_length=True
        ),
    ]
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.custom_fakers: Dict[str, Callable] = {}
        self._add_default_rules()
    
    def _add_default_rules(self):
        """添加默认规则"""
        self.rules.extend(self.DEFAULT_RULES)
    
    def add_rule(self, rule: Rule):
        """添加自定义规则"""
        self.rules.append(rule)
    
    def register_faker(self, name: str, faker_func: Callable[[], str]):
        """注册假数据生成器"""
        self.custom_fakers[name] = faker_func
    
    def _mask_email(self, match: re.Match) -> str:
        """脱敏邮箱"""
        email = match.group(0)
        local, domain = email.rsplit('@', 1)
        if len(local) <= 2:
            return f"*@{domain}"
        return f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"
    
    def _mask_phone(self, match: re.Match) -> str:
        """脱敏手机号"""
        phone = match.group(0)
        return f"{phone[:3]}****{phone[-4:]}"
    
    def _mask_id_card(self, match: re.Match) -> str:
        """脱敏身份证号"""
        id_card = match.group(0)
        return f"{id_card[:4]}{'*' * (len(id_card) - 8)}{id_card[-4:]}"
    
    def _mask_bank_card(self, match: re.Match) -> str:
        """脱敏银行卡号"""
        card = match.group(0)
        return f"{card[:4]}{'*' * (len(card) - 8)}{card[-4:]}"
    
    def _mask_ip(self, match: re.Match) -> str:
        """脱敏IP地址"""
        ip = match.group(0)
        parts = ip.split('.')
        return f"{parts[0]}.***.{parts[2]}.{parts[3]}"
    
    def _generic_mask(self, match: re.Match, preserve: int = 2) -> str:
        """通用脱敏"""
        text = match.group(0)
        if len(text) <= preserve:
            return '*' * len(text)
        return f"{text[:preserve]}{'*' * (len(text) - preserve * 2)}{text[-preserve:]}"
    
    def _hash_value(self, value: str) -> str:
        """哈希处理"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def _apply_strategy(self, match: re.Match, rule: Rule) -> str:
        """应用脱敏策略"""
        value = match.group(0)
        
        if rule.name == "email":
            return self._mask_email(match)
        elif rule.name == "phone":
            return self._mask_phone(match)
        elif rule.name == "id_card":
            return self._mask_id_card(match)
        elif rule.name == "bank_card":
            return self._mask_bank_card(match)
        elif rule.name == "ip_address":
            return self._mask_ip(match)
        
        # 通用处理
        if rule.strategy == AnonymizationStrategy.MASK:
            return self._generic_mask(match)
        elif rule.strategy == AnonymizationStrategy.HASH:
            return self._hash_value(value)
        elif rule.strategy == AnonymizationStrategy.PARTIAL:
            return self._generic_mask(match, preserve=2)
        elif rule.strategy == AnonymizationStrategy.REMOVE:
            return '[REMOVED]'
        elif rule.strategy == AnonymizationStrategy.FAKE:
            if rule.name in self.custom_fakers:
                return self.custom_fakers[rule.name]()
            return '[REDACTED]'
        
        return value
    
    def anonymize(self, text: str) -> str:
        """对文本进行脱敏处理"""
        result = text
        
        for rule in self.rules:
            result = rule.pattern.sub(
                lambda m: self._apply_strategy(m, rule),
                result
            )
        
        return result
    
    def anonymize_json(self, json_data: str or dict, 
                       sensitive_keys: List[str] = None) -> str:
        """对JSON数据进行脱敏"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if sensitive_keys is None:
            sensitive_keys = [
                'password', 'secret', 'token', 'key', 'credential',
                'ssn', 'credit_card', 'cvv', 'pin'
            ]
        
        def process(obj):
            if isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    key_lower = k.lower()
                    if any(sk in key_lower for sk in sensitive_keys):
                        result[k] = '[SENSITIVE]'
                    elif isinstance(v, (dict, list)):
                        result[k] = process(v)
                    else:
                        result[k] = v
                return result
            elif isinstance(obj, list):
                return [process(item) for item in obj]
            return obj
        
        processed = process(data)
        return json.dumps(processed, ensure_ascii=False, indent=2)
    
    def anonymize_file(self, input_path: str, output_path: str = None,
                       format: str = 'auto'):
        """对文件进行脱敏处理"""
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if format == 'auto':
            if input_path.endswith('.json'):
                format = 'json'
            elif input_path.endswith('.csv'):
                format = 'csv'
            else:
                format = 'text'
        
        if format == 'json':
            result = self.anonymize_json(content)
        else:
            result = self.anonymize(content)
        
        if output_path is None:
            output_path = input_path.replace('.', '_anonymized.')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return output_path
    
    def get_detection_report(self, text: str) -> Dict:
        """获取敏感数据检测报告"""
        report = {
            'total_matches': 0,
            'by_type': {},
            'matches': []
        }
        
        for rule in self.rules:
            matches = rule.pattern.findall(text)
            if matches:
                count = len(matches) if isinstance(matches[0], str) else len(matches)
                report['by_type'][rule.name] = count
                report['total_matches'] += count
                for m in matches[:5]:  # 只记录前5个示例
                    if isinstance(m, str):
                        report['matches'].append({
                            'type': rule.name,
                            'value': m[:20] + '...' if len(m) > 20 else m
                        })
        
        return report


def demo():
    """演示"""
    anonymizer = DataAnonymizer()
    
    # 注册自定义假数据生成器
    anonymizer.register_faker('name', lambda: '张三')
    anonymizer.register_faker('address', lambda: '北京市朝阳区')
    
    # 测试文本
    test_text = """
    用户信息登记表
    姓名: 张三
    邮箱: zhangsan@example.com
    手机: 13812345678
    身份证: 110101199001011234
    银行卡: 6222021234567890
    IP地址: 192.168.1.100
    密码: MyP@ssw0rd123
    """
    
    print("=" * 60)
    print("智能数据脱敏工具 - 演示")
    print("=" * 60)
    
    print("\n【原始数据】")
    print(test_text)
    
    print("\n【脱敏后数据】")
    anonymized = anonymizer.anonymize(test_text)
    print(anonymized)
    
    print("\n【检测报告】")
    report = anonymizer.get_detection_report(test_text)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # JSON脱敏演示
    print("\n【JSON脱敏演示】")
    json_data = {
        "user": "zhangsan",
        "email": "zhangsan@example.com",
        "phone": "13812345678",
        "password": "secret123",
        "api_token": "ghp_xxxxxxxxxxxx",
        "nested": {
            "credit_card": "6222021234567890",
            "ssn": "110101199001011234"
        }
    }
    
    print("\n原始JSON:")
    print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    anonymized_json = anonymizer.anonymize_json(json_data)
    print("\n脱敏后JSON:")
    print(anonymized_json)


if __name__ == "__main__":
    demo()
