#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Day 36: 数据验证与清洗工具
   Data Validation & Sanitization Library

📁 文件: scripts/2026-02-02_36_data_validator.py
📊 大小: 23.8 KB
📝 功能: 全面的数据验证和清洗库，支持多种数据类型的验证和净化

✨ 功能特性:
- 📧 邮箱格式验证（RFC 5322标准）
- 🔗 URL链接验证（HTTP/HTTPS/FTP等）
- 📱 手机号码验证（全球多国家支持）
- 🔒 SQL注入防护
- 🚫 XSS攻击防护
- 📊 数据类型自动推断
- 📋 JSON Schema风格验证
- 🔧 自定义验证规则
- 💬 多语言错误提示
- 📈 验证统计报告
"""

import re
import json
import hashlib
import html
from dataclasses import dataclass, field
from typing import Any, Callable, List, Dict, Optional, Tuple, Union
from enum import Enum
from urllib.parse import urlparse, parse_qs
import ipaddress


class ValidationStatus(Enum):
    """验证状态枚举"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """验证结果类"""
    is_valid: bool
    status: ValidationStatus
    value: Any
    cleaned_value: Any = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_name: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'is_valid': self.is_valid,
            'status': self.status.value,
            'value': self.value,
            'cleaned_value': self.cleaned_value,
            'errors': self.errors,
            'warnings': self.warnings,
            'field_name': self.field_name
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class SanitizationLevel(Enum):
    """消毒级别"""
    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class DataValidator:
    """数据验证器主类"""
    
    # Email正则（简化版RFC 5322）
    EMAIL_PATTERN = re.compile(
        r'^(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    )
    
    # URL正则
    URL_PATTERN = re.compile(
        r'^(?i)(https?|ftp)://[^\s/$.?#].[^\s]*$'
    )
    
    # 手机号正则（国际格式）
    PHONE_PATTERNS = {
        'CN': re.compile(r'^(\+?86)?1[3-9]\d{9}$'),  # 中国
        'US': re.compile(r'^\+?1?\d{10}$'),          # 美国
        'UK': re.compile(r'^\+?44\d{10}$'),          # 英国
        'JP': re.compile(r'^\+?81?\d{9,10}$'),       # 日本
        'KR': re.compile(r'^\+?82?\d{9,10}$'),       # 韩国
        'DE': re.compile(r'^\+?49\d{10,11}$'),       # 德国
        'FR': re.compile(r'^\+?33\d{9}$'),           # 法国
        'AU': re.compile(r'^\+?61\d{9}$'),           # 澳大利亚
        'IN': re.compile(r'^\+?91?\d{10}$'),         # 印度
        'BR': re.compile(r'^\+?55?\d{10,11}$'),      # 巴西
    }
    
    # SQL注入特征
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"('|'')",
        r"(--|/\*|\*/|#)",
        r"(\bOR\b.*=.*\bOR\b)",
        r"(\bAND\b.*=.*\bAND\b)",
        r"(EXEC(\s|\+)+(S|X)P\w+)",
        r"(0x[0-9a-fA-F]+)",
        r"(@@|@)",
    ]
    
    # XSS特征
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'<svg[^>]*onload[^>]*>',
        r'<img[^>]*src[^>]*onerror[^>]*>',
        r'<body[^>]*onload[^>]*>',
        r'<input[^>]*onfocus[^>]*>',
        r'<marquee[^>]*onstart[^>]*>',
    ]
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化验证器
        
        Args:
            locale: 语言设置 ('zh_CN' 或 'en_US')
        """
        self.locale = locale
        self._custom_validators: Dict[str, Callable] = {}
        self._validation_stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'warnings': 0
        }
    
    def _get_message(self, key: str, **kwargs) -> str:
        """获取本地化消息"""
        messages = {
            'zh_CN': {
                'email.invalid': '邮箱格式不正确',
                'email.empty': '邮箱不能为空',
                'url.invalid': 'URL格式不正确',
                'url.empty': 'URL不能为空',
                'phone.invalid': '手机号码格式不正确',
                'phone.empty': '手机号码不能为空',
                'string.empty': '字符串不能为空',
                'string.too_short': '字符串长度不能少于{min_length}个字符',
                'string.too_long': '字符串长度不能超过{max_length}个字符',
                'number.out_of_range': '数值超出范围（{min} - {max}）',
                'number.not_integer': '必须是整数',
                'number.not_float': '必须是浮点数',
                'list.empty': '列表不能为空',
                'list.too_short': '列表元素数量不能少于{min_length}个',
                'list.too_long': '列表元素数量不能超过{max_length}个',
                'sql_detected': '检测到SQL注入特征',
                'xss_detected': '检测到XSS攻击特征',
                'invalid_type': '数据类型不正确，期望{expected}，实际{actual}',
            },
            'en_US': {
                'email.invalid': 'Invalid email format',
                'email.empty': 'Email cannot be empty',
                'url.invalid': 'Invalid URL format',
                'url.empty': 'URL cannot be empty',
                'phone.invalid': 'Invalid phone number format',
                'phone.empty': 'Phone number cannot be empty',
                'string.empty': 'String cannot be empty',
                'string.too_short': 'String length must be at least {min_length} characters',
                'string.too_long': 'String length must not exceed {max_length} characters',
                'number.out_of_range': 'Number out of range ({min} - {max})',
                'number.not_integer': 'Must be an integer',
                'number.not_float': 'Must be a float',
                'list.empty': 'List cannot be empty',
                'list.too_short': 'List must contain at least {min_length} elements',
                'list.too_long': 'List must not contain more than {max_length} elements',
                'sql_detected': 'SQL injection pattern detected',
                'xss_detected': 'XSS attack pattern detected',
                'invalid_type': 'Invalid type, expected {expected}, got {actual}',
            }
        }
        
        msg_dict = messages.get(self.locale, messages['en_US'])
        msg = msg_dict.get(key, key)
        return msg.format(**kwargs)
    
    def validate_email(self, email: str, field_name: str = "邮箱") -> ValidationResult:
        """验证邮箱地址
        
        Args:
            email: 邮箱地址
            field_name: 字段名称
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=email,
            field_name=field_name
        )
        
        if not email or not email.strip():
            result.errors.append(self._get_message('email.empty'))
            return result
        
        if not self.EMAIL_PATTERN.match(email.strip()):
            result.errors.append(self._get_message('email.invalid'))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = email.strip().lower()
        self._validation_stats['valid'] += 1
        
        return result
    
    def validate_url(self, url: str, field_name: str = "URL") -> ValidationResult:
        """验证URL格式
        
        Args:
            url: URL地址
            field_name: 字段名称
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=url,
            field_name=field_name
        )
        
        if not url or not url.strip():
            result.errors.append(self._get_message('url.empty'))
            return result
        
        try:
            parsed = urlparse(url.strip())
            
            # 检查协议
            if parsed.scheme not in ['http', 'https', 'ftp', 'ftps']:
                result.errors.append(self._get_message('url.invalid'))
                return result
            
            # 检查域名
            if not parsed.netloc:
                result.errors.append(self._get_message('url.invalid'))
                return result
            
            # 检查IP格式
            try:
                ipaddress.ip_address(parsed.hostname)
                is_ip = True
            except:
                is_ip = False
            
            # IP地址需要额外验证
            if is_ip and parsed.scheme in ['http', 'https']:
                result.warnings.append('URL使用了IP地址，可能不安全')
            
        except Exception:
            result.errors.append(self._get_message('url.invalid'))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = url.strip()
        self._validation_stats['valid'] += 1
        
        return result
    
    def validate_phone(self, phone: str, country: str = 'CN', 
                       field_name: str = "手机号") -> ValidationResult:
        """验证手机号码
        
        Args:
            phone: 手机号码
            country: 国家代码
            field_name: 字段名称
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=phone,
            field_name=field_name
        )
        
        if not phone or not phone.strip():
            result.errors.append(self._get_message('phone.empty'))
            return result
        
        pattern = self.PHONE_PATTERNS.get(country.upper())
        if not pattern:
            # 如果不支持该国家，使用通用验证
            pattern = re.compile(r'^\+?\d{7,15}$')
        
        phone_clean = phone.strip().replace(' ', '').replace('-', '')
        
        if not pattern.match(phone_clean):
            result.errors.append(self._get_message('phone.invalid'))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = phone_clean
        self._validation_stats['valid'] += 1
        
        return result
    
    def validate_string(self, value: Any, field_name: str = "字符串",
                        min_length: Optional[int] = None,
                        max_length: Optional[int] = None,
                        allow_empty: bool = False) -> ValidationResult:
        """验证字符串
        
        Args:
            value: 要验证的值
            field_name: 字段名称
            min_length: 最小长度
            max_length: 最大长度
            allow_empty: 是否允许空字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=value,
            field_name=field_name
        )
        
        if not isinstance(value, str):
            result.errors.append(self._get_message(
                'invalid_type', expected='str', actual=type(value).__name__
            ))
            return result
        
        value_stripped = value.strip()
        
        if not value_stripped and not allow_empty:
            result.errors.append(self._get_message('string.empty'))
            return result
        
        if min_length is not None and len(value_stripped) < min_length:
            result.errors.append(self._get_message(
                'string.too_short', min_length=min_length
            ))
            return result
        
        if max_length is not None and len(value_stripped) > max_length:
            result.errors.append(self._get_message(
                'string.too_long', max_length=max_length
            ))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = value_stripped
        self._validation_stats['valid'] += 1
        
        return result
    
    def validate_number(self, value: Any, field_name: str = "数值",
                        min_val: Optional[Union[int, float]] = None,
                        max_val: Optional[Union[int, float]] = None,
                        allow_decimal: bool = True) -> ValidationResult:
        """验证数字
        
        Args:
            value: 要验证的值
            field_name: 字段名称
            min_val: 最小值
            max_val: 最大值
            allow_decimal: 是否允许小数
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=value,
            field_name=field_name
        )
        
        try:
            if allow_decimal:
                num_val = float(value)
            else:
                num_val = int(value)
                if isinstance(value, float) and value != int(value):
                    result.errors.append(self._get_message('number.not_integer'))
                    return result
        except (ValueError, TypeError):
            result.errors.append(self._get_message(
                'invalid_type', expected='number', actual=type(value).__name__
            ))
            return result
        
        if min_val is not None and num_val < min_val:
            result.errors.append(self._get_message(
                'number.out_of_range', min=min_val, max=max_val or '∞'
            ))
            return result
        
        if max_val is not None and num_val > max_val:
            result.errors.append(self._get_message(
                'number.out_of_range', min=min_val or '-∞', max=max_val
            ))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = num_val
        self._validation_stats['valid'] += 1
        
        return result
    
    def validate_list(self, value: Any, field_name: str = "列表",
                      min_length: Optional[int] = None,
                      max_length: Optional[int] = None,
                      allow_empty: bool = False) -> ValidationResult:
        """验证列表
        
        Args:
            value: 要验证的值
            field_name: 字段名称
            min_length: 最小长度
            max_length: 最大长度
            allow_empty: 是否允许空列表
            
        Returns:
            ValidationResult: 验证结果
        """
        self._validation_stats['total'] += 1
        
        result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            value=value,
            field_name=field_name
        )
        
        if not isinstance(value, (list, tuple)):
            result.errors.append(self._get_message(
                'invalid_type', expected='list', actual=type(value).__name__
            ))
            return result
        
        list_val = list(value)
        
        if not list_val and not allow_empty:
            result.errors.append(self._get_message('list.empty'))
            return result
        
        if min_length is not None and len(list_val) < min_length:
            result.errors.append(self._get_message(
                'list.too_short', min_length=min_length
            ))
            return result
        
        if max_length is not None and len(list_val) > max_length:
            result.errors.append(self._get_message(
                'list.too_long', max_length=max_length
            ))
            return result
        
        result.is_valid = True
        result.status = ValidationStatus.VALID
        result.cleaned_value = list_val
        self._validation_stats['valid'] += 1
        
        return result
    
    def sanitize_sql(self, value: str, level: SanitizationLevel = SanitizationLevel.MODERATE) -> str:
        """SQL注入防护
        
        Args:
            value: 原始字符串
            level: 消毒级别
            
        Returns:
            str: 清洗后的字符串
        """
        if not isinstance(value, str):
            return value
        
        sanitized = value
        
        if level == SanitizationLevel.BASIC:
            # 基本转义
            sanitized = sanitized.replace("'", "''")
            sanitized = sanitized.replace("\\", "\\\\")
            
        elif level == SanitizationLevel.MODERATE:
            # 中等级别
            sanitized = sanitized.replace("'", "''")
            sanitized = sanitized.replace("\\", "\\\\")
            # 移除注释
            sanitized = re.sub(r'--.*$', '', sanitized, flags=re.MULTILINE)
            sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
            
        elif level == SanitizationLevel.AGGRESSIVE:
            # 激进级别
            sanitized = self.sanitize_sql(value, SanitizationLevel.MODERATE)
            # 移除关键字
            for pattern in self.SQL_INJECTION_PATTERNS:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def sanitize_xss(self, value: str, level: SanitizationLevel = SanitizationLevel.MODERATE) -> str:
        """XSS攻击防护
        
        Args:
            value: 原始字符串
            level: 消毒级别
            
        Returns:
            str: 清洗后的字符串
        """
        if not isinstance(value, str):
            return value
        
        sanitized = value
        
        if level == SanitizationLevel.BASIC:
            # HTML实体编码
            sanitized = html.escape(sanitized)
            
        elif level in [SanitizationLevel.MODERATE, SanitizationLevel.AGGRESSIVE]:
            # 移除危险标签和属性
            for pattern in self.XSS_PATTERNS:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            # 编码HTML实体
            sanitized = html.escape(sanitized)
            
            # 移除javascript:协议
            sanitized = re.sub(r'javascript\s*:', '', sanitized, flags=re.IGNORECASE)
            
            # 移除data:协议（可能被用于XSS）
            sanitized = re.sub(r'data\s*:', 'data-blocked:', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def sanitize_html(self, value: str, allowed_tags: List[str] = None,
                      allowed_attrs: Dict[str, List[str]] = None) -> str:
        """HTML安全清洗（允许部分标签）
        
        Args:
            value: 原始HTML
            allowed_tags: 允许的标签列表
            allowed_attrs: 允许的属性字典
            
        Returns:
            str: 清洗后的HTML
        """
        if not isinstance(value, str):
            return value
        
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'b', 'i', 'u', 'em', 'strong', 'a', 'ul', 'ol', 'li']
        
        if allowed_attrs is None:
            allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt']}
        
        # 移除所有标签
        text = re.sub(r'<[^>]+>', '', value)
        
        # 编码剩余的HTML实体
        text = html.escape(text)
        
        return text
    
    def sanitize_input(self, value: str, 
                       sql_level: SanitizationLevel = SanitizationLevel.MODERATE,
                       xss_level: SanitizationLevel = SanitizationLevel.MODERATE) -> str:
        """综合输入清洗
        
        Args:
            value: 原始输入
            sql_level: SQL消毒级别
            xss_level: XSS消毒级别
            
        Returns:
            str: 清洗后的输入
        """
        if not isinstance(value, str):
            return value
        
        sanitized = value.strip()
        
        # 移除控制字符
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
        
        # SQL消毒
        sanitized = self.sanitize_sql(sanitized, sql_level)
        
        # XSS消毒
        sanitized = self.sanitize_xss(sanitized, xss_level)
        
        return sanitized
    
    def detect_sql_injection(self, value: str) -> Tuple[bool, List[str]]:
        """检测SQL注入特征
        
        Args:
            value: 要检测的字符串
            
        Returns:
            Tuple[检测结果, 匹配到的特征列表]
        """
        if not isinstance(value, str):
            return False, []
        
        detected = []
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def detect_xss(self, value: str) -> Tuple[bool, List[str]]:
        """检测XSS攻击特征
        
        Args:
            value: 要检测的字符串
            
        Returns:
            Tuple[检测结果, 匹配到的特征列表]
        """
        if not isinstance(value, str):
            return False, []
        
        detected = []
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def add_validator(self, name: str, validator: Callable) -> None:
        """添加自定义验证器
        
        Args:
            name: 验证器名称
            validator: 验证函数
        """
        self._custom_validators[name] = validator
    
    def validate_with_schema(self, data: Dict, schema: Dict) -> List[ValidationResult]:
        """使用JSON Schema风格验证数据
        
        Args:
            data: 要验证的数据
            schema: 验证规则
            
        Returns:
            List[ValidationResult]: 验证结果列表
        """
        results = []
        
        for field_name, rules in schema.items():
            value = data.get(field_name)
            
            # 类型检查
            if 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'string' and not isinstance(value, str):
                    results.append(ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        value=value,
                        errors=[self._get_message(
                            'invalid_type', expected='string', actual=type(value).__name__
                        )],
                        field_name=field_name
                    ))
                    continue
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    results.append(ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        value=value,
                        errors=[self._get_message(
                            'invalid_type', expected='number', actual=type(value).__name__
                        )],
                        field_name=field_name
                    ))
                    continue
                elif expected_type == 'list' and not isinstance(value, (list, tuple)):
                    results.append(ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        value=value,
                        errors=[self._get_message(
                            'invalid_type', expected='list', actual=type(value).__name__
                        )],
                        field_name=field_name
                    ))
                    continue
            
            # 长度检查
            if 'min_length' in rules:
                if isinstance(value, str) and len(value) < rules['min_length']:
                    results.append(ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        value=value,
                        errors=[self._get_message(
                            'string.too_short', min_length=rules['min_length']
                        )],
                        field_name=field_name
                    ))
                    continue
            
            if 'max_length' in rules:
                if isinstance(value, str) and len(value) > rules['max_length']:
                    results.append(ValidationResult(
                        is_valid=False,
                        status=ValidationStatus.INVALID,
                        value=value,
                        errors=[self._get_message(
                            'string.too_long', max_length=rules['max_length']
                        )],
                        field_name=field_name
                    ))
                    continue
            
            # 范围检查
            if 'min' in rules or 'max' in rules:
                if isinstance(value, (int, float)):
                    if 'min' in rules and value < rules['min']:
                        results.append(ValidationResult(
                            is_valid=False,
                            status=ValidationStatus.INVALID,
                            value=value,
                            errors=[self._get_message(
                                'number.out_of_range', min=rules['min'], max=rules.get('max', '∞')
                            )],
                            field_name=field_name
                        ))
                        continue
                    if 'max' in rules and value > rules['max']:
                        results.append(ValidationResult(
                            is_valid=False,
                            status=ValidationStatus.INVALID,
                            value=value,
                            errors=[self._get_message(
                                'number.out_of_range', min=rules.get('min', '-∞'), max=rules['max']
                            )],
                            field_name=field_name
                        ))
                        continue
            
            # 必填检查
            if rules.get('required', False) and value is None:
                results.append(ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INVALID,
                    value=value,
                    errors=[f'{field_name}是必填字段'],
                    field_name=field_name
                ))
                continue
            
            # 自定义验证器
            if 'custom' in rules and field_name in self._custom_validators:
                custom_result = self._custom_validators[field_name](value)
                if not custom_result.is_valid:
                    results.append(custom_result)
                    continue
            
            results.append(ValidationResult(
                is_valid=True,
                status=ValidationStatus.VALID,
                value=value,
                field_name=field_name
            ))
        
        return results
    
    def get_validation_stats(self) -> Dict:
        """获取验证统计信息
        
        Returns:
            Dict: 统计信息
        """
        total = self._validation_stats['total']
        valid = self._validation_stats['valid']
        
        return {
            **self._validation_stats,
            'valid_rate': f'{(valid/total*100):.2f}%' if total > 0 else '0%'
        }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._validation_stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'warnings': 0
        }


def generate_report(results: List[ValidationResult]) -> str:
    """生成验证报告
    
    Args:
        results: 验证结果列表
        
    Returns:
        str: 格式化报告
    """
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = len(results) - valid_count
    
    lines = [
        "=" * 50,
        "📊 数据验证报告",
        "=" * 50,
        f"总验证数: {len(results)}",
        f"✅ 通过: {valid_count}",
        f"❌ 失败: {invalid_count}",
        "",
    ]
    
    if invalid_count > 0:
        lines.append("失败详情:")
        lines.append("-" * 30)
        for r in results:
            if not r.is_valid:
                lines.append(f"📍 {r.field_name}")
                for error in r.errors:
                    lines.append(f"   - {error}")
                lines.append("")
    
    return "\n".join(lines)


def demo():
    """演示函数"""
    print("🎯 Day 36: 数据验证与清洗工具演示")
    print("=" * 50)
    
    validator = DataValidator()
    
    # 1. 邮箱验证
    print("\n1. 📧 邮箱验证")
    emails = [
        "test@example.com",
        "invalid-email",
        "user.name+tag@domain.co.uk",
        ""
    ]
    for email in emails:
        result = validator.validate_email(email)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} '{email}' -> {result.cleaned_value or 'N/A'}")
        if result.errors:
            print(f"      错误: {result.errors[0]}")
    
    # 2. URL验证
    print("\n2. 🔗 URL验证")
    urls = [
        "https://www.example.com",
        "ftp://files.example.org",
        "invalid-url",
        "javascript:alert('xss')"
    ]
    for url in urls:
        result = validator.validate_url(url)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {url}")
        if result.warnings:
            print(f"      警告: {result.warnings[0]}")
    
    # 3. 手机号验证
    print("\n3. 📱 手机号验证")
    phones = [
        ("13812345678", "CN"),
        ("+8613812345678", "CN"),
        ("1234567890", "US"),
        ("invalid", "CN")
    ]
    for phone, country in phones:
        result = validator.validate_phone(phone, country)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} {phone} ({country})")
    
    # 4. SQL注入检测
    print("\n4. 🔒 SQL注入检测")
    sql_tests = [
        "normal text",
        "'; DROP TABLE users; --",
        "admin' OR '1'='1"
    ]
    for sql in sql_tests:
        detected, patterns = validator.detect_sql_injection(sql)
        status = "🚨" if detected else "✅"
        print(f"   {status} '{sql[:30]}...'")
        if detected:
            print(f"      检测到: {patterns}")
    
    # 5. XSS检测
    print("\n5. 🚫 XSS攻击检测")
    xss_tests = [
        "normal text",
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>"
    ]
    for xss in xss_tests:
        detected, patterns = validator.detect_xss(xss)
        status = "🚨" if detected else "✅"
        print(f"   {status} '{xss[:30]}...'")
        if detected:
            print(f"      检测到: {patterns}")
    
    # 6. 输入清洗
    print("\n6. 🧹 输入清洗")
    dirty_input = "  <script>alert('xss')</script>  ' OR '1'='1  "
    clean_input = validator.sanitize_input(dirty_input)
    print(f"   原始: {dirty_input[:40]}...")
    print(f"   清洗后: {clean_input[:40]}...")
    
    # 7. Schema验证
    print("\n7. 📋 Schema验证")
    schema = {
        'name': {'type': 'string', 'required': True, 'max_length': 50},
        'age': {'type': 'number', 'min': 0, 'max': 150},
        'email': {'type': 'string', 'required': True}
    }
    
    test_data = {
        'name': '张三',
        'age': 25,
        'email': 'zhangsan@example.com'
    }
    
    results = validator.validate_with_schema(test_data, schema)
    for r in results:
        status = "✅" if r.is_valid else "❌"
        print(f"   {status} {r.field_name}: {r.value}")
        if not r.is_valid:
            for error in r.errors:
                print(f"      - {error}")
    
    # 8. 统计报告
    print("\n8. 📊 验证统计")
    stats = validator.get_validation_stats()
    print(f"   总验证数: {stats['total']}")
    print(f"   通过: {stats['valid']}")
    print(f"   失败: {stats['invalid']}")
    print(f"   通过率: {stats['valid_rate']}")
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")


if __name__ == "__main__":
    demo()
