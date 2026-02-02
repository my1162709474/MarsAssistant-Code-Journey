#!/usr/bin/env python3
"""
正则表达式测试器和学习工具
Smart Regex Tester & Learning Tool

功能：
1. 实时测试正则表达式匹配
2. 提供常用正则表达式模板
3. 正则表达式语法高亮和解释
4. 支持多种匹配模式
5. 正则表达式学习和测试

作者：AI Assistant
日期：2026-02-02
"""

import re
import sys
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class MatchMode(Enum):
    """匹配模式"""
    FINDALL = "findall"      # 查找所有匹配
    SEARCH = "search"        # 搜索第一个匹配
    MATCH = "match"          # 开头匹配
    FINDITER = "finditer"    # 迭代查找


class Color:
    """终端颜色类"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # 亮色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


@dataclass
class MatchResult:
    """匹配结果"""
    match_text: str
    start: int
    end: int
    groups: Tuple[str, ...]
    groupdict: Dict[str, str]
    match_mode: MatchMode


class RegexTemplate:
    """常用正则表达式模板"""
    
    TEMPLATES = {
        "email": {
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "description": "匹配电子邮箱地址",
            "example": "user@example.com"
        },
        "phone_cn": {
            "pattern": r"1[3-9]\d{9}",
            "description": "匹配中国大陆手机号码",
            "example": "13812345678"
        },
        "phone_us": {
            "pattern": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "description": "匹配美国电话号码",
            "example": "(123) 456-7890"
        },
        "url": {
            "pattern": r"https?://[^\s<>\"]+|www\.[^\s<>\"]+",
            "description": "匹配URL地址",
            "example": "https://www.example.com"
        },
        "ipv4": {
            "pattern": r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            "description": "匹配IPv4地址",
            "example": "192.168.1.1"
        },
        "date_iso": {
            "pattern": r"\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])",
            "description": "匹配ISO格式日期 (YYYY-MM-DD)",
            "example": "2026-02-02"
        },
        "hex_color": {
            "pattern": r"#(?:[0-9A-Fa-f]{3}){1,2}\b",
            "description": "匹配十六进制颜色值",
            "example": "#FF5733"
        },
        "html_tag": {
            "pattern": r"<[^>]+>",
            "description": "匹配HTML标签",
            "example": "<div class='container'>"
        },
        "credit_card": {
            "pattern": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
            "description": "匹配信用卡号码",
            "example": "4111111111111111"
        },
        "uuid": {
            "pattern": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
            "description": "匹配UUID",
            "example": "550e8400-e29b-41d4-a716-446655440000"
        },
        "version": {
            "pattern": r"\d+\.\d+(?:\.\d+)?(?:[-+][a-zA-Z0-9.+]+)?",
            "description": "匹配版本号",
            "example": "1.2.3-beta"
        },
        "username": {
            "pattern": r"^[a-zA-Z][a-zA-Z0-9_-]{2,16}$",
            "description": "匹配用户名 (字母开头，3-16位)",
            "example": "user_123"
        },
        "password_strong": {
            "pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            "description": "强密码：8位以上，包含大小写字母、数字和特殊字符",
            "example": "Pass1234@"
        },
        "python_identifier": {
            "pattern": r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            "description": "匹配Python标识符",
            "example": "variable_name"
        },
        "camel_case": {
            "pattern": r"^[a-z]+(?:[A-Z][a-z]+)*$",
            "description": "匹配驼峰命名法",
            "example": "camelCase"
        },
        "snake_case": {
            "pattern": r"^[a-z]+(?:_[a-z]+)*$",
            "description": "匹配下划线命名法",
            "example": "snake_case"
        },
        "number_int": {
            "pattern": r"-?\d+",
            "description": "匹配整数",
            "example": "123"
        },
        "number_float": {
            "pattern": r"-?\d+\.\d+(?:[eE][+-]?\d+)?",
            "description": "匹配浮点数",
            "example": "3.14159"
        },
        "currency": {
            "pattern": r"[$€£¥]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
            "description": "匹配货币金额",
            "example": "$1,234.56"
        },
        "hashtag": {
            "pattern": r"#\w+",
            "description": "匹配话题标签",
            "example": "#python"
        },
        "chinese": {
            "pattern": r"[\u4e00-\u9fff]+",
            "description": "匹配中文字符",
            "example": "你好"
        },
    }
    
    @classmethod
    def get_names(cls) -> List[str]:
        """获取所有模板名称"""
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def get_template(cls, name: str) -> Optional[Dict[str, str]]:
        """获取指定模板"""
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def list_templates(cls) -> None:
        """列出所有模板"""
        print(f"\n{Color.BOLD}{Color.CYAN}可用正则表达式模板：{Color.RESET}\n")
        for i, (name, template) in enumerate(cls.TEMPLATES.items(), 1):
            print(f"  {i:2d}. {Color.GREEN}{name:<15}{Color.RESET} - {template['description']}")
        print()


class RegexTester:
    """正则表达式测试器"""
    
    def __init__(self, flags: int = re.MULTILINE):
        self.flags = flags
        self.history: List[Dict[str, Any]] = []
    
    def set_flags(self, flags: int) -> None:
        """设置匹配标志"""
        self.flags = flags
    
    def get_flag_string(self, flags: int) -> str:
        """获取标志字符串"""
        flag_names = []
        if flags & re.IGNORECASE:
            flag_names.append("i")
        if flags & re.MULTILINE:
            flag_names.append("m")
        if flags & re.DOTALL:
            flag_names.append("s")
        if flags & re.VERBOSE:
            flag_names.append("x")
        if flags & re.UNICODE:
            flag_names.append("u")
        return "".join(flag_names) if flag_names else "无"
    
    def test_pattern(self, pattern: str, text: str, mode: MatchMode = MatchMode.FINDALL) -> List[MatchResult]:
        """测试正则表达式"""
        try:
            regex = re.compile(pattern, self.flags)
            
            if mode == MatchMode.FINDALL:
                matches = regex.findall(text)
                results = []
                for match in matches:
                    if isinstance(match, tuple):
                        results.append(MatchResult(
                            match_text=str(match),
                            start=-1, end=-1,
                            groups=match,
                            groupdict={},
                            match_mode=mode
                        ))
                    else:
                        results.append(MatchResult(
                            match_text=match,
                            start=-1, end=-1,
                            groups=(match,),
                            groupdict={},
                            match_mode=mode
                        ))
                return results
            
            elif mode == MatchMode.SEARCH:
                match = regex.search(text)
                if match:
                    return [MatchResult(
                        match_text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        groups=match.groups(),
                        groupdict=match.groupdict(),
                        match_mode=mode
                    )]
                return []
            
            elif mode == MatchMode.MATCH:
                match = regex.match(text)
                if match:
                    return [MatchResult(
                        match_text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        groups=match.groups(),
                        groupdict=match.groupdict(),
                        match_mode=mode
                    )]
                return []
            
            elif mode == MatchMode.FINDITER:
                matches = regex.finditer(text)
                results = []
                for match in matches:
                    results.append(MatchResult(
                        match_text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        groups=match.groups(),
                        groupdict=match.groupdict(),
                        match_mode=mode
                    ))
                return results
            
        except re.error as e:
            raise ValueError(f"正则表达式错误: {e}")
        
        return []
    
    def highlight_match(self, text: str, results: List[MatchResult]) -> str:
        """高亮显示匹配结果"""
        if not results:
            return text
        
        sorted_results = sorted(results, key=lambda x: x.start, reverse=True)
        
        highlighted = text
        for result in sorted_results:
            if result.start >= 0:
                matched = text[result.start:result.end]
                highlighted = (
                    highlighted[:result.start] +
                    f"{Color.BG_CYAN}{Color.BLACK}" + matched + f"{Color.RESET}" +
                    highlighted[result.end:]
                )
        
        return highlighted
    
    def explain_pattern(self, pattern: str) -> str:
        """解释正则表达式"""
        explanations = []
        
        clean_pattern = re.sub(r'\s+#.*$', '', pattern, flags=re.MULTILINE)
        clean_pattern = re.sub(r'\s+', '', clean_pattern)
        
        i = 0
        while i < len(clean_pattern):
            char = clean_pattern[i]
            
            if char == '[':
                end = clean_pattern.find(']', i)
                if end != -1:
                    char_class = clean_pattern[i+1:end]
                    explanations.append(f"字符类: [{char_class}]")
                    i = end + 1
                    continue
            
            if char == '(':
                if i + 1 < len(clean_pattern) and clean_pattern[i+1] == '?':
                    if i + 2 < len(clean_pattern) and clean_pattern[i+2] == ':':
                        explanations.append("非捕获组")
                        i += 3
                        continue
                    elif i + 2 < len(clean_pattern) and clean_pattern[i+2] == '<':
                        end = clean_pattern.find('>', i)
                        if end != -1:
                            group_name = clean_pattern[i+3:end]
                            explanations.append(f"命名捕获组: <{group_name}>")
                            i = end + 1
                            continue
                else:
                    explanations.append("捕获组")
                    i += 1
                    continue
            
            if char in '*+?':
                quantifier = char
                if i + 1 < len(clean_pattern) and clean_pattern[i+1] == '?':
                    quantifier += '?'
                    i += 1
                
                if quantifier == '*':
                    explanations.append("量词: 0次或多次 (贪婪)")
                elif quantifier == '*?':
                    explanations.append("量词: 0次或多次 (非贪婪)")
                elif quantifier == '+':
                    explanations.append("量词: 1次或多次 (贪婪)")
                elif quantifier == '+?':
                    explanations.append("量词: 1次或多次 (非贪婪)")
                elif quantifier == '?':
                    explanations.append("量词: 0次或1次")
                elif quantifier == '??':
                    explanations.append("量词: 0次或1次 (非贪婪)")
                i += 1
                continue
            
            if char == '{':
                end = clean_pattern.find('}', i)
                if end != -1:
                    quant = clean_pattern[i+1:end]
                    explanations.append(f"量词范围: {{{quant}}}")
                    i = end + 1
                    continue
            
            if char == '^':
                explanations.append("行首锚点")
            elif char == '$':
                explanations.append("行尾锚点")
            elif char == '\\b':
                explanations.append("单词边界")
            elif char == '\\B':
                explanations.append("非单词边界")
            
            if char == '\\':
                if i + 1 < len(clean_pattern):
                    next_char = clean_pattern[i+1]
                    escapes = {
                        'd': '数字',
                        'D': '非数字',
                        'w': '单词字符',
                        'W': '非单词字符',
                        's': '空白字符',
                        'S': '非空白字符',
                    }
                    if next_char in escapes:
                        explanations.append(f"预定义: \\{next_char} ({escapes[next_char]})")
                        i += 2
                        continue
            
            if char == '|':
                explanations.append("分支选择")
            
            if char not in ['.', '|', '(', ')', '[', ']', '{', '}']:
                if char not in '^$*+?\\':
                    explanations.append(f"字面字符: '{char}'")
            
            i += 1
        
        return "\n".join(explanations)
    
    def add_to_history(self, pattern: str, text: str, results: List[MatchResult]) -> None:
        """添加到历史记录"""
        self.history.append({
            "pattern": pattern,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "result_count": len(results),
            "timestamp": "2026-02-02 17:15"
        })
        
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def show_history(self) -> None:
        """显示历史记录"""
        if not self.history:
            print(f"\n{Color.YELLOW}暂无历史记录{Color.RESET}\n")
            return
        
        print(f"\n{Color.BOLD}{Color.CYAN}最近使用记录：{Color.RESET}\n")
        for i, item in enumerate(self.history[-10:], 1):
            print(f"  {i}. 模式: {item['pattern'][:30]}")
            print(f"     结果数: {item['result_count']}")
            print()


def quick_test(pattern: str, text: str, flags: int = re.MULTILINE) -> List[Dict]:
    """快速测试正则表达式"""
    tester = RegexTester(flags)
    results = tester.test_pattern(pattern, text)
    
    output = []
    for i, result in enumerate(results, 1):
        output.append({
            "index": i,
            "match": result.match_text,
            "start": result.start,
            "end": result.end,
            "groups": result.groups,
        })
    
    return output


def batch_test(patterns: List[str], text: str) -> Dict[str, List[Dict]]:
    """批量测试多个正则表达式"""
    results = {}
    for pattern in patterns:
        try:
            results[pattern] = quick_test(pattern, text)
        except ValueError as e:
            results[pattern] = [{"error": str(e)}]
    return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="正则表达式测试器和学习工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python smart_regex_tester.py -p "\\d+" -t "abc123def456"
  python smart_regex_tester.py -p "email" -t "test@example.com" --template
  python smart_regex_tester.py -e "\\d{3}-\\d{4}"
  python smart_regex_tester.py -l
  python smart_regex_tester.py --interactive
        """
    )
    
    parser.add_argument("-p", "--pattern", help="正则表达式模式")
    parser.add_argument("-t", "--text", help="测试文本")
    parser.add_argument("-e", "--explain", help="解释正则表达式")
    parser.add_argument("-l", "--list", action="store_true", help="列出所有模板")
    parser.add_argument("--template", action="store_true", help="将pattern视为模板名称")
    parser.add_argument("-m", "--mode", choices=["findall", "search", "match", "finditer"],
                        default="findall", help="匹配模式")
    parser.add_argument("-f", "--flags", default="m", help="匹配标志 (i/m/s/x/u)")
    parser.add_argument("--no-highlight", action="store_true", help="关闭高亮")
    parser.add_argument("-i", "--interactive", action="store_true", help="进入交互模式")
    parser.add_argument("-j", "--json", action="store_true", help="JSON格式输出")
    parser.add_argument("-b", "--batch", help="批量测试文件 (每行一个模式)")
    
    args = parser.parse_args()
    
    # 解析标志
    flags = 0
    for f in args.flags:
        if f == 'i':
            flags |= re.IGNORECASE
        elif f == 'm':
            flags |= re.MULTILINE
        elif f == 's':
            flags |= re.DOTALL
        elif f == 'x':
            flags |= re.VERBOSE
        elif f == 'u':
            flags |= re.UNICODE
    
    tester = RegexTester(flags)
    template = RegexTemplate()
    
    if args.interactive:
        from InteractiveMode import InteractiveMode
        InteractiveMode().run()
        return
    
    if args.list:
        template.list_templates()
        return
    
    if args.explain:
        explanation = tester.explain_pattern(args.explain)
        print(f"\n{Color.BOLD}表达式解释:{Color.RESET}\n")
        print(explanation)
        print()
        return
    
    if args.batch and args.text:
        with open(args.batch, 'r') as f:
            patterns = [line.strip() for line in f if line.strip()]
        results = batch_test(patterns, args.text)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for pattern, matches in results.items():
                print(f"\n{Color.CYAN}模式: {pattern}{Color.RESET}")
                print(f"  结果: {matches}")
        return
    
    if args.pattern and args.text:
        if args.template:
            tmpl = template.get_template(args.pattern)
            if tmpl:
                pattern = tmpl['pattern']
                print(f"使用模板: {args.pattern}")
                print(f"描述: {tmpl['description']}")
            else:
                print(f"未找到模板: {args.pattern}")
                return
        else:
            pattern = args.pattern
        
        mode = MatchMode(args.mode)
        results = tester.test_pattern(pattern, args.text, mode)
        
        if args.json:
            output = {
                "pattern": pattern,
                "text": args.text,
                "mode": mode.value,
                "count": len(results),
                "results": [
                    {
                        "match": r.match_text,
                        "start": r.start,
                        "end": r.end,
                        "groups": r.groups,
                    }
                    for r in results
                ]
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(f"\n{Color.BOLD}匹配结果 ({len(results)}个):{Color.RESET}\n")
            
            if not args.no_highlight and results:
                highlighted = tester.highlight_match(args.text, results)
                print(highlighted)
                print()
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {Color.GREEN}'{result.match_text}'{Color.RESET}")
                if result.start >= 0:
                    print(f"     位置: {result.start}-{result.end}")
                if result.groups:
                    print(f"     分组: {result.groups}")
                print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
