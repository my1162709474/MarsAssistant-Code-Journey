#!/usr/bin/env python3
"""
AI Code Completion Engine
智能代码补全引擎 - 基于上下文的智能代码补全工具

功能:
- 基于上下文的代码补全
- 多语言支持
- 自定义补全规则
- 实时补全建议

作者: MarsAssistant
日期: 2026-02-04
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"


@dataclass
class CompletionSuggestion:
    """代码补全建议"""
    text: str
    kind: str = "text"
    detail: str = ""
    score: float = 0.0
    icon: str = "📝"


@dataclass
class CompletionContext:
    """补全上下文"""
    language: Language
    before_cursor: str = ""
    after_cursor: str = ""
    indentation: int = 0
    current_line: str = ""
    file_path: Optional[str] = None


class CodePattern:
    """代码模式匹配器"""
    
    PATTERNS = {
        Language.PYTHON: [
            (r'def\s+(\w+)\s*\((.*?)\)', 'function', '函数定义'),
            (r'class\s+(\w+)', 'class', '类定义'),
            (r'if\s+', 'if', '条件语句'),
            (r'for\s+', 'for', '循环语句'),
            (r'while\s+', 'while', 'while循环'),
            (r'try:', 'try', '异常处理'),
            (r'with\s+', 'with', '上下文管理'),
            (r'import\s+', 'import', '导入语句'),
            (r'from\s+', 'from_import', '从模块导入'),
            (r'def\s+__\w+__\(self', 'dunder', '双下划线方法'),
        ],
        Language.JAVASCRIPT: [
            (r'function\s+(\w+)\s*\(', 'function', '函数定义'),
            (r'const\s+(\w+)\s*=', 'const', '常量定义'),
            (r'let\s+(\w+)\s*=', 'let', '变量定义'),
            (r'class\s+', 'class', '类定义'),
            (r'if\s*\(', 'if', '条件语句'),
            (r'for\s*\(', 'for', '循环语句'),
            (r'async\s+function', 'async', '异步函数'),
            (r'->\s*', 'arrow', '箭头函数'),
        ],
        Language.JAVA: [
            (r'public\s+class\s+', 'class', '公共类'),
            (r'private\s+void\s+(\w+)', 'method', '私有方法'),
            (r'public\s+void\s+(\w+)', 'method', '公共方法'),
            (r'if\s*\(', 'if', '条件语句'),
            (r'for\s*\(', 'for', '循环语句'),
            (r'@Override', 'override', '重写方法'),
        ],
    }
    
    KEYWORDS = {
        Language.PYTHON: [
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 
            'except', 'finally', 'with', 'as', 'import', 'from', 'return',
            'yield', 'raise', 'pass', 'break', 'continue', 'lambda',
            'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None',
            'async', 'await', 'self', 'super', 'print', 'len', 'range',
        ],
        Language.JAVASCRIPT: [
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 
            'while', 'do', 'switch', 'case', 'break', 'continue', 'return',
            'try', 'catch', 'finally', 'throw', 'new', 'this', 'class',
            'extends', 'import', 'export', 'default', 'async', 'await',
            'true', 'false', 'null', 'undefined', 'typeof', 'instanceof',
        ],
        Language.JAVA: [
            'public', 'private', 'protected', 'class', 'interface', 
            'extends', 'implements', 'static', 'final', 'void', 'int',
            'String', 'boolean', 'if', 'else', 'for', 'while', 'do',
            'switch', 'case', 'break', 'continue', 'return', 'try',
            'catch', 'finally', 'throw', 'throws', 'new', 'this',
            'super', 'null', 'true', 'false', '@Override', '@Test',
        ],
    }
    
    SNIPPETS = {
        Language.PYTHON: {
            'if': "if condition:\n    pass",
            'for': "for item in iterable:\n    pass",
            'while': "while condition:\n    pass",
            'try': "try:\n    pass\nexcept Exception as e:\n    pass",
            'class': "class ClassName:\n    def __init__(self):\n        pass",
            'def': "def function_name(arg1, arg2):\n    pass",
            'with': "with open('file.txt', 'r') as f:\n    pass",
            'lambda': "lambda x: x",
            'list_comp': "[x for x in iterable]",
            'dict_comp': "{k: v for k, v in items}",
        },
        Language.JAVASCRIPT: {
            'if': "if (condition) {\n    \n}",
            'for': "for (let i = 0; i < length; i++) {\n    \n}",
            'while': "while (condition) {\n    \n}",
            'try': "try {\n    \n} catch (error) {\n    \n}",
            'class': "class ClassName {\n    constructor() {\n        \n    }\n}",
            'const': "const variableName = value;",
            'arrow': "const funcName = (params) => {\n    \n};",
            'async': "async function functionName(params) {\n    \n}",
            'import': "import moduleName from 'module';",
            'export': "export default functionName;",
        },
        Language.JAVA: {
            'class': "public class ClassName {\n    \n}",
            'method': "public void methodName() {\n    \n}",
            'if': "if (condition) {\n    \n}",
            'for': "for (int i = 0; i < n; i++) {\n    \n}",
            'foreach': "for (Type item : collection) {\n    \n}",
            'try': "try {\n    \n} catch (Exception e) {\n    e.printStackTrace();\n}",
            'main': "public static void main(String[] args) {\n    \n}",
            'println': "System.out.println();",
            'scanner': "Scanner scanner = new Scanner(System.in);",
            'array': "Type[] array = new Type[length];",
        },
    }


class CompletionEngine:
    """AI代码补全引擎主类"""
    
    def __init__(self):
        self.language = None
        self.history: List[str] = []
        self.custom_snippets: Dict[str, Dict] = {}
        
    def detect_language(self, code: str, file_path: Optional[str] = None) -> Language:
        """检测编程语言"""
        if file_path:
            ext = file_path.split('.')[-1].lower()
            ext_map = {
                'py': Language.PYTHON,
                'js': Language.JAVASCRIPT,
                'ts': Language.TYPESCRIPT,
                'java': Language.JAVA,
                'cpp': Language.CPP,
                'c': Language.C,
                'go': Language.GO,
                'rs': Language.RUST,
                'rb': Language.RUBY,
                'php': Language.PHP,
                'swift': Language.SWIFT,
                'kt': Language.KOTLIN,
            }
            if ext in ext_map:
                return ext_map[ext]
        
        # 基于内容检测
        if re.search(r'def\s+\w+\s*\(', code):
            return Language.PYTHON
        elif re.search(r'function\s+\w+|const\s+\w+\s*=', code):
            return Language.JAVASCRIPT
        elif re.search(r'public\s+class|System\.out', code):
            return Language.JAVA
        
        return Language.PYTHON  # 默认
    
    def get_context(self, code: str, cursor_pos: int) -> CompletionContext:
        """提取补全上下文"""
        before = code[:cursor_pos]
        after = code[cursor_pos:]
        
        # 获取当前行
        current_line_start = before.rfind('\n') + 1
        current_line = before[current_line_start:]
        
        # 计算缩进
        indentation = len(current_line) - len(current_line.lstrip())
        
        # 检测语言
        language = self.detect_language(code)
        
        return CompletionContext(
            language=language,
            before_cursor=before,
            after_cursor=after,
            indentation=indentation,
            current_line=current_line,
        )
    
    def get_word_before_cursor(self, context: CompletionContext) -> str:
        """获取光标前的单词"""
        match = re.search(r'\b(\w*)$', context.current_line)
        return match.group(1) if match else ""
    
    def suggest_completions(self, code: str, cursor_pos: int) -> List[CompletionSuggestion]:
        """生成代码补全建议"""
        context = self.get_context(code, cursor_pos)
        word = self.get_word_before_cursor(context)
        suggestions = []
        
        # 1. 关键词补全
        suggestions.extend(self._suggest_keywords(context, word))
        
        # 2. 代码片段补全
        suggestions.extend(self._suggest_snippets(context, word))
        
        # 3. 基于上下文的智能补全
        suggestions.extend(self._suggest_contextual(context, word))
        
        # 4. 自定义片段
        suggestions.extend(self._suggest_custom(context, word))
        
        # 按分数排序
        suggestions.sort(key=lambda x: x.score, reverse=True)
        
        return suggestions[:10]  # 返回前10个建议
    
    def _suggest_keywords(self, context: CompletionContext, prefix: str) -> List[CompletionSuggestion]:
        """关键词补全建议"""
        keywords = CodePattern.KEYWORDS.get(context.language, [])
        suggestions = []
        
        for kw in keywords:
            if kw.startswith(prefix) and kw != prefix:
                score = 1.0 - (len(prefix) / len(kw)) if prefix else 0.5
                suggestions.append(CompletionSuggestion(
                    text=kw,
                    kind="keyword",
                    detail="关键词",
                    score=score,
                    icon="🔑"
                ))
        
        return suggestions
    
    def _suggest_snippets(self, context: CompletionContext, prefix: str) -> List[CompletionSuggestion]:
        """代码片段补全建议"""
        snippets = CodePattern.SNIPPETS.get(context.language, {})
        suggestions = []
        
        for name, snippet in snippets.items():
            if name.startswith(prefix) and prefix:
                # 计算缩进调整
                adjusted = self._adjust_indentation(snippet, context.indentation)
                suggestions.append(CompletionSuggestion(
                    text=adjusted,
                    kind="snippet",
                    detail=f"代码片段: {name}",
                    score=0.9,
                    icon="📦"
                ))
        
        return suggestions
    
    def _adjust_indentation(self, snippet: str, base_indent: int) -> str:
        """调整代码片段缩进"""
        lines = snippet.split('\n')
        adjusted = []
        
        for i, line in enumerate(lines):
            if line.strip():
                # 计算行的原始缩进
                original_indent = len(line) - len(line.lstrip())
                new_indent = base_indent + original_indent
                adjusted.append(' ' * new_indent + line.lstrip())
            else:
                adjusted.append('')
        
        return '\n'.join(adjusted)
    
    def _suggest_contextual(self, context: CompletionContext, prefix: str) -> List[CompletionSuggestion]:
        """上下文智能补全"""
        suggestions = []
        
        # 基于当前行的模式匹配
        for pattern, ptype, desc in CodePattern.PATTERNS.get(context.language, []):
            if re.search(pattern, context.before_cursor):
                if ptype == 'function' and prefix:
                    suggestions.append(CompletionSuggestion(
                        text=f"({prefix})",
                        kind="completion",
                        detail="函数调用",
                        score=0.8,
                        icon="🔧"
                    ))
                elif ptype == 'import':
                    if context.language == Language.PYTHON:
                        suggestions.append(CompletionSuggestion(
                            text="import ",
                            kind="completion",
                            detail="导入模块",
                            score=0.85,
                            icon="📥"
                        ))
        
        return suggestions
    
    def _suggest_custom(self, context: CompletionContext, prefix: str) -> List[CompletionSuggestion]:
        """自定义代码片段"""
        suggestions = []
        
        for name, data in self.custom_snippets.items():
            if name.startswith(prefix):
                suggestions.append(CompletionSuggestion(
                    text=data.get('snippet', ''),
                    kind="custom",
                    detail=data.get('description', '自定义片段'),
                    score=0.95,
                    icon="⭐"
                ))
        
        return suggestions
    
    def add_custom_snippet(self, name: str, snippet: str, description: str = ""):
        """添加自定义代码片段"""
        self.custom_snippets[name] = {
            'snippet': snippet,
            'description': description
        }
    
    def apply_completion(self, code: str, cursor_pos: int, suggestion: CompletionSuggestion) -> Tuple[str, int]:
        """应用补全建议"""
        before = code[:cursor_pos]
        after = code[cursor_pos:]
        
        # 移除已输入的前缀
        word = re.search(r'\b(\w*)$', before)
        if word:
            prefix_end = cursor_pos - len(word.group(1))
            before = code[:prefix_end]
        
        new_code = before + suggestion.text + after
        new_cursor = len(before) + len(suggestion.text)
        
        return new_code, new_cursor
    
    def generate_completion_report(self) -> Dict:
        """生成补全统计报告"""
        return {
            "supported_languages": [lang.value for lang in Language],
            "total_keywords": sum(len(kw) for kw in CodePattern.KEYWORDS.values()),
            "total_snippets": sum(len(sn) for sn in CodePattern.SNIPPETS.values()),
            "custom_snippets": len(self.custom_snippets),
            "engine_version": "1.0.0",
        }


def main():
    """演示代码补全引擎"""
    engine = CompletionEngine()
    
    # 测试代码
    test_code = '''
def calculate_sum(numbers):
    total = 0
    for num in 
'''
    
    print("=" * 50)
    print("🤖 AI Code Completion Engine")
    print("=" * 50)
    
    # 检测语言
    language = engine.detect_language(test_code)
    print(f"\n检测语言: {language.value}")
    
    # 获取补全位置
    cursor_pos = len(test_code)
    
    # 生成补全建议
    suggestions = engine.suggest_completions(test_code, cursor_pos)
    
    print(f"\n📋 补全建议 (共 {len(suggestions)} 个):")
    print("-" * 50)
    
    for i, sug in enumerate(suggestions, 1):
        print(f"{i}. [{sug.icon}] {sug.text}")
        print(f"   类型: {sug.kind} | 详情: {sug.detail} | 分数: {sug.score:.2f}")
    
    # 报告
    print("\n📊 引擎统计:")
    report = engine.generate_completion_report()
    for key, value in report.items():
        print(f"  - {key}: {value}")
    
    # 添加自定义片段示例
    engine.add_custom_snippet(
        "todo",
        "# TODO: \npass",
        "TODO注释模板"
    )
    
    print("\n✅ 演示完成!")


if __name__ == "__main__":
    main()
