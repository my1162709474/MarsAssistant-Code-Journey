#!/usr/bin/env python3
"""
智能正则表达式生成器 🧩
根据自然语言描述自动生成正则表达式

功能:
- 自然语言转正则表达式
- 常用模式模板
- 正则表达式测试和验证
- 多语言支持（中文、英文）
"""

import re
from typing import Dict, List, Optional, Tuple


class RegexGenerator:
    """智能正则表达式生成器"""
    
    # 常用模式模板
    PATTERNS: Dict[str, Dict] = {
        # 基础类型
        "integer": {
            "desc": "整数（正负）",
            "regex": r"^-?\d+$",
            "examples": ["123", "-456", "0"]
        },
        "positive_integer": {
            "desc": "正整数",
            "regex": r"^\d+$",
            "examples": ["123", "456", "0"]
        },
        "float": {
            "desc": "浮点数",
            "regex": r"^-?\d+(\.\d+)?$",
            "examples": ["3.14", "-2.5", "100"]
        },
        "email": {
            "desc": "邮箱地址",
            "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "examples": ["user@example.com", "name.test@domain.org"]
        },
        "phone": {
            "desc": "手机号（中国）",
            "regex": r"^1[3-9]\d{9}$",
            "examples": ["13812345678", "15987654321"]
        },
        "url": {
            "desc": "URL地址",
            "regex": r"^https?://[^\s/$.?#].[^\s]*$",
            "examples": ["https://example.com", "http://test.org/path"]
        },
        "ip_address": {
            "desc": "IP地址",
            "regex": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            "examples": ["192.168.1.1", "10.0.0.255"]
        },
        "date": {
            "desc": "日期（YYYY-MM-DD）",
            "regex": r"^\d{4}-\d{2}-\d{2}$",
            "examples": ["2024-01-15", "2026-02-02"]
        },
        "time": {
            "desc": "时间（HH:MM:SS）",
            "regex": r"^\d{2}:\d{2}:\d{2}$",
            "examples": ["14:30:00", "08:05:30"]
        },
        "datetime": {
            "desc": "日期时间",
            "regex": r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            "examples": ["2024-01-15 14:30:00"]
        },
        
        # 中文相关
        "chinese": {
            "desc": "中文字符",
            "regex": r"^[\u4e00-\u9fa5]+$",
            "examples": ["你好世界", "中文测试"]
        },
        "chinese_name": {
            "desc": "中文姓名（2-4个汉字）",
            "regex": r"^[\u4e00-\u9fa5]{2,4}$",
            "examples": ["张三", "李四"]
        },
        "chinese_phone": {
            "desc": "中国大陆电话（座机）",
            "regex": r"^0\d{2,3}-\d{7,8}$",
            "examples": ["010-12345678", "021-1234567"]
        },
        "id_card": {
            "desc": "身份证号（中国）",
            "regex": r"^\d{17}[\dXx]$",
            "examples": ["110101199001011234"]
        },
        
        # 英文相关
        "english_word": {
            "desc": "英文单词",
            "regex": r"^[a-zA-Z]+$",
            "examples": ["hello", "World"]
        },
        "english_sentence": {
            "desc": "英文句子（首字母大写）",
            "regex": r"^[A-Z][a-zA-Z\s]*[.!?]$",
            "examples": ["Hello world.", "This is a test!"]
        },
        
        # 身份证/护照
        "passport": {
            "desc": "护照号码",
            "regex": r"^[A-Z]{1,2}\d{6,9}$",
            "examples": ["G12345678", "E1234567"]
        },
        
        # 银行卡/信用卡
        "credit_card": {
            "desc": "信用卡号（16位）",
            "regex": r"^\d{16}$",
            "examples": ["1234567812345678"]
        },
        "bank_card": {
            "desc": "银行卡号（16-19位）",
            "regex": r"^\d{16,19}$",
            "examples": ["6222021234567890"]
        },
        
        # 邮政编码
        "zip_code_cn": {
            "desc": "邮政编码（中国）",
            "regex": r"^\d{6}$",
            "examples": ["100000", "200000"]
        },
        "zip_code_us": {
            "desc": "邮政编码（美国）",
            "regex": r"^\d{5}(-\d{4})?$",
            "examples": ["12345", "12345-6789"]
        },
        
        # 社会化媒体
        "username": {
            "desc": "用户名（3-16位字母数字）",
            "regex": r"^[a-zA-Z0-9_]{3,16}$",
            "examples": ["user123", "test_user"]
        },
        "hashtag": {
            "desc": "标签（Hashtag）",
            "regex": r"^#[\w\u4e00-\u9fa5]+$",
            "examples": ["#tag", "#中文标签"]
        },
        
        # 文件相关
        "file_name": {
            "desc": "文件名（不含路径）",
            "regex": r"^[^\/\\:*?\"<>|]+$",
            "examples": ["document.txt", "my-file.py"]
        },
        "file_extension": {
            "desc": "文件扩展名",
            "regex": r"\.[a-zA-Z0-9]+$",
            "examples": [".txt", ".py", ".js"]
        },
        
        # HTML/XML
        "html_tag": {
            "desc": "HTML标签",
            "regex": r"<[^>]+>",
            "examples": ["<div>", "<p>Content</p>"]
        },
        "email_html": {
            "desc": "邮箱（HTML格式）",
            "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "examples": ["user@example.com"]
        },
    }
    
    # 自然语言映射
    NATURAL_MAPPING: Dict[str, List[str]] = {
        "integer": ["整数", "数字", "whole number", "integer"],
        "float": ["小数", "浮点数", "decimal", "float"],
        "email": ["邮箱", "邮件", "email", "mail"],
        "phone": ["手机", "手机号", "phone", "mobile"],
        "url": ["网址", "链接", "url", "website", "link"],
        "ip": ["IP", "IP地址", "ip address"],
        "date": ["日期", "date"],
        "time": ["时间", "time"],
        "chinese": ["中文", "汉字", "chinese", "china"],
        "username": ["用户名", "账号", "user name", "username", "account"],
        "password": ["密码", "password"],
        "hashtag": ["标签", "话题", "tag", "hashtag"],
    }
    
    def __init__(self):
        """初始化正则表达式生成器"""
        self.history: List[Tuple[str, str, str]] = []  # (描述, 正则, 结果)
    
    def get_pattern(self, pattern_name: str) -> Optional[Dict]:
        """获取预定义模式"""
        return self.PATTERNS.get(pattern_name.lower())
    
    def list_patterns(self, category: Optional[str] = None) -> List[Tuple[str, str]]:
        """列出所有可用模式"""
        patterns = []
        for name, info in self.PATTERNS.items():
            patterns.append((name, info["desc"]))
        return sorted(patterns, key=lambda x: x[0])
    
    def generate_from_natural(self, description: str) -> Optional[str]:
        """从自然语言描述生成正则表达式"""
        desc_lower = description.lower()
        
        # 匹配预定义模式
        for pattern_name, keywords in self.NATURAL_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in desc_lower:
                    pattern = self.get_pattern(pattern_name)
                    if pattern:
                        return pattern["regex"]
        
        # 尝试动态生成
        return self._generate_advanced(desc_lower)
    
    def _generate_advanced(self, description: str) -> Optional[str]:
        """高级正则生成（基于描述智能推断）"""
        
        # 数字相关
        if re.search(r'\d|数字|number', description):
            if '正' in description or '正数' in description or 'positive' in description:
                return r'^\d+$'
            if '负' in description or '负数' in description or 'negative' in description:
                return r'^-?\d+$'
            if '小' in description or '浮点' in description or 'decimal' in description:
                return r'^-?\d+(\.\d+)?$'
            return r'^\d+$'
        
        # 字符长度
        length_match = re.search(r'(\d+)\s*个?\s*([字|字符|字母])', description)
        if length_match:
            num = length_match.group(1)
            char_type = length_match.group(2)
            if '字' in char_type or '字符' in char_type:
                if '中' in description:
                    return f'^[\u4e00-\u9fa5]{{{num}}}$'
                return f'^.{{{num}}}$'
        
        # 英文
        if re.search(r'英|english|letter', description):
            if '大' in description:
                return r'^[A-Z]+$'
            if '小' in description:
                return r'^[a-z]+$'
            return r'^[a-zA-Z]+$'
        
        return None
    
    def test_pattern(self, pattern: str, test_strings: List[str]) -> Dict:
        """测试正则表达式"""
        try:
            compiled = re.compile(pattern)
            results = {}
            for s in test_strings:
                match = compiled.match(s)
                results[s] = bool(match)
            return {
                "success": True,
                "results": results,
                "match_count": sum(results.values())
            }
        except re.error as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_patterns(self, text: str, pattern: str) -> List[str]:
        """从文本中提取匹配的字符串"""
        try:
            matches = re.findall(pattern, text)
            return matches
        except re.error:
            return []
    
    def replace_pattern(self, text: str, pattern: str, replacement: str) -> str:
        """使用正则表达式替换文本"""
        try:
            return re.sub(pattern, replacement, text)
        except re.error:
            return text
    
    def explain_pattern(self, pattern: str) -> str:
        """解释正则表达式的含义"""
        explanations = {
            r'^': '字符串开始',
            r'$': '字符串结束',
            r'\d': '数字（0-9）',
            r'\w': '字母、数字、下划线',
            r'\s': '空白字符',
            r'.': '任意字符（除换行符）',
            r'+': '一次或多次',
            r'*': '零次或多次',
            r'?': '零次或一次',
            r'{n}': '恰好n次',
            r'{n,}': '至少n次',
            r'{n,m}': 'n到m次',
            r'[]': '字符集合',
            r'()': '捕获组',
            r'|': '或',
            r'\\': '转义',
            r'[\u4e00-\u9fa5]': '中文字符',
        }
        
        explanation = []
        for regex, desc in sorted(explanations.items(), key=lambda x: -len(x[0])):
            if regex in pattern:
                explanation.append(f"{regex}: {desc}")
        
        return '\n'.join(explanation) if explanation else "标准正则表达式语法"
    
    def generate(self, description: str) -> Dict:
        """生成正则表达式的主方法"""
        # 尝试直接匹配
        for name, info in self.PATTERNS.items():
            if name.lower() == description.lower() or info["desc"] == description:
                self.history.append((description, info["regex"], "success"))
                return {
                    "success": True,
                    "pattern": info["regex"],
                    "description": info["desc"],
                    "examples": info["examples"],
                    "source": f"预定义模式: {name}"
                }
        
        # 自然语言生成
        regex = self.generate_from_natural(description)
        if regex:
            self.history.append((description, regex, "success"))
            return {
                "success": True,
                "pattern": regex,
                "description": "智能生成",
                "examples": ["需自行验证"],
                "source": "自然语言生成"
            }
        
        return {
            "success": False,
            "error": "无法识别的模式，请尝试更详细的描述",
            "suggestions": [name for name in self.PATTERNS.keys()]
        }


def demo():
    """演示正则表达式生成器"""
    print("🧩 智能正则表达式生成器演示")
    print("=" * 50)
    
    generator = RegexGenerator()
    
    # 测试用例
    test_cases = [
        ("整数", "integer"),
        ("手机号", "phone"),
        ("邮箱", "email"),
        ("中文", "chinese"),
        ("用户名", "username"),
        ("日期", "date"),
    ]
    
    print("\n📋 预定义模式测试:")
    for desc, pattern_name in test_cases:
        pattern = generator.get_pattern(pattern_name)
        if pattern:
            print(f"\n{desc}: {pattern['regex']}")
            print(f"  示例: {pattern['examples']}")
    
    print("\n\n🔍 自然语言生成测试:")
    natural_tests = [
        "正整数",
        "负数",
        "网址链接",
        "英文单词",
    ]
    
    for desc in natural_tests:
        result = generator.generate(desc)
        if result["success"]:
            print(f"\n{desc} → {result['pattern']}")
            print(f"  来源: {result['source']}")
    
    print("\n\n🧪 正则表达式测试:")
    pattern = r"^\d{6}$"
    test_strings = ["123456", "12345", "1234567", "abcdef"]
    result = generator.test_pattern(pattern, test_strings)
    print(f"\n测试模式: {pattern}")
    for s, matched in result["results"].items():
        status = "✅ 匹配" if matched else "❌ 不匹配"
        print(f"  '{s}': {status}")
    
    print("\n\n📖 解释正则表达式:")
    pattern = r"^1[3-9]\d{9}$"
    explanation = generator.explain_pattern(pattern)
    print(f"\n模式: {pattern}")
    print(f"解释:\n{explanation}")
    
    print("\n\n✨ 演示完成!")


if __name__ == "__main__":
    demo()
