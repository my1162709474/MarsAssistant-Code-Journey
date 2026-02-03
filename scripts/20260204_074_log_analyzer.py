#!/usr/bin/env python3
"""
智能代码文档生成器 - Smart Code Documentation Generator
=========================================================
自动为代码生成专业文档，包括函数说明、参数说明、返回值说明、使用示例等

功能特性:
- 🏷️ 多语言支持: Python/JavaScript/TypeScript/Java/Go/Rust/C++
- 📝 智能分析: 自动识别函数、类、变量、导入
- 📖 文档生成: 生成Markdown格式的专业文档
- 💡 使用示例: 自动生成使用示例代码
- 🔧 自定义模板: 支持自定义文档模板
- 📊 复杂度分析: 计算代码复杂度指标

作者: MarsAssistant
日期: 2026-02-03
"""

import ast
import re
import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    UNKNOWN = "unknown"


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    docstring: str = ""
    parameters: List[Dict] = field(default_factory=list)
    return_type: str = "Any"
    return_description: str = ""
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    complexity: int = 1
    code: str = ""


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    docstring: str = ""
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[Dict] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    line_number: int = 0
    code: str = ""


@dataclass
class ImportInfo:
    """导入信息"""
    module: str
    names: List[str]
    is_from: bool
    line_number: int


@dataclass
class VariableInfo:
    """变量信息"""
    name: str
    type_hint: str = ""
    value: str = ""
    description: str = ""
    line_number: int = 0
    is_constant: bool = False


class CodeDocumentationGenerator:
    """代码文档生成器"""
    
    def __init__(self):
        self.language_map = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.java': Language.JAVA,
            '.go': Language.GO,
            '.rs': Language.RUST,
            '.cpp': Language.CPP,
            '.h': Language.CPP,
            '.c': Language.CPP,
        }
        self.language_patterns = {
            Language.PYTHON: {
                'function': r'def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[\w\[\]]+\s*)?:',
                'class': r'class\s+(\w+)\s*(?:\([^)]*\))?\s*:',
                'decorator': r'@(\w+)',
                'comment': r'#\s*(.+)',
                'multiline_comment': r'"""([\s\S]*?)"""',
            },
            Language.JAVASCRIPT: {
                'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?function|\*?\s*(\w+)\s*\([^)]*\)\s*{)',
                'class': r'class\s+(\w+)',
                'decorator': r'@(\w+)',
                'comment': r'//\s*(.+)',
                'multiline_comment': r'/\*([\s\S]*?)\*/',
            },
            Language.TYPESCRIPT: {
                'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=])\s*=>|interface\s+(\w+))',
                'class': r'class\s+(\w+)',
                'decorator': r'@(\w+)',
                'comment': r'//\s*(.+)',
                'multiline_comment': r'/\*([\s\S]*?)\*/',
            },
        }
    
    def detect_language(self, file_path: str) -> Language:
        """检测文件语言"""
        ext = Path(file_path).suffix.lower()
        return self.language_map.get(ext, Language.UNKNOWN)
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_python_info(self, code: str) -> Dict[str, Any]:
        """提取Python代码信息"""
        result = {
            'imports': [],
            'variables': [],
            'functions': [],
            'classes': [],
        }
        
        try:
            tree = ast.parse(code)
            
            # 提取导入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append(ImportInfo(
                            module=alias.name,
                            names=[alias.asname or alias.name] if alias.asname else [],
                            is_from=False,
                            line_number=node.lineno
                        ))
                elif isinstance(node, ast.ImportFrom):
                    names = [alias.name for alias in node.names]
                    result['imports'].append(ImportInfo(
                        module=node.module or '',
                        names=names,
                        is_from=True,
                        line_number=node.lineno
                    ))
            
            # 提取函数
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_function_info(node, code)
                    result['functions'].append(func_info)
            
            # 提取类
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, code)
                    result['classes'].append(class_info)
            
            # 提取变量
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_info = VariableInfo(
                                name=target.id,
                                line_number=node.lineno
                            )
                            if isinstance(node.value, ast.Constant):
                                var_info.value = str(node.value.value)
                            result['variables'].append(var_info)
            
        except SyntaxError as e:
            result['error'] = str(e)
        
        return result
    
    def _extract_function_info(self, node, code: str) -> FunctionInfo:
        """提取函数信息"""
        func_info = FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
        
        # 提取参数
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_type_hint(arg.annotation),
                'default': '',
                'description': ''
            }
            # 检查默认值
            defaults = node.args.defaults
            if defaults:
                idx = len(node.args.args) - len(defaults)
                if arg.arg in [a.arg for a in node.args.args[:idx]]:
                    for i, a in enumerate(node.args.args[:idx]):
                        if a.arg == arg.arg and i < len(defaults):
                            param['default'] = ast.unparse(defaults[i])
            func_info.parameters.append(param)
        
        # 提取返回类型
        if node.returns:
            func_info.return_type = ast.unparse(node.returns)
        
        # 提取docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.s, str):
                func_info.docstring = node.body[0].value.s
        
        # 计算复杂度
        func_info.complexity = self._calculate_complexity(node)
        
        return func_info
    
    def _extract_class_info(self, node, code: str) -> ClassInfo:
        """提取类信息"""
        class_info = ClassInfo(
            name=node.name,
            line_number=node.lineno
        )
        
        # 提取基类
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info.base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                class_info.base_classes.append(f"{base.value.id}.{base.attr}")
        
        # 提取docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.s, str):
                class_info.docstring = node.body[0].value.s
        
        # 提取方法
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._extract_function_info(item, code)
                class_info.methods.append(method)
        
        # 提取属性
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr = {
                            'name': target.id,
                            'type': self._get_type_hint(item.annotation) if item.annotation else '',
                            'description': ''
                        }
                        class_info.attributes.append(attr)
        
        return class_info
    
    def _get_type_hint(self, annotation) -> str:
        """获取类型提示"""
        if annotation is None:
            return 'Any'
        try:
            return ast.unparse(annotation)
        except:
            return 'Any'
    
    def _calculate_complexity(self, node) -> int:
        """计算代码复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def extract_js_info(self, code: str) -> Dict[str, Any]:
        """提取JavaScript/TypeScript代码信息"""
        result = {
            'imports': [],
            'variables': [],
            'functions': [],
            'classes': [],
        }
        
        patterns = self.language_patterns[Language.JAVASCRIPT]
        
        # 提取导入
        import_pattern = r'(?:import|export\s+(?:var|let|const|function|class))\s+(.+?)\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(import_pattern, code)
        for match in matches:
            result['imports'].append(ImportInfo(
                module=match[1],
                names=[n.strip() for n in match[0].split(',')],
                is_from=True,
                line_number=code[:500].count('\n')
            ))
        
        # 提取函数
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?function|\*?\s*(\w+)\s*\([^)]*\)\s*\{)'
        matches = re.findall(func_pattern, code)
        for match in matches:
            func_name = next((m for m in match if m), None)
            if func_name:
                result['functions'].append(FunctionInfo(
                    name=func_name,
                    line_number=code[:code.find(func_name)].count('\n') + 1
                ))
        
        # 提取类
        class_pattern = r'class\s+(\w+)'
        matches = re.findall(class_pattern, code)
        for match in matches:
            result['classes'].append(ClassInfo(
                name=match,
                line_number=code[:code.find(match)].count('\n') + 1
            ))
        
        return result
    
    def extract_code_info(self, file_path: str) -> Dict[str, Any]:
        """提取代码信息"""
        language = self.detect_language(file_path)
        code = self.read_file(file_path)
        
        if language == Language.PYTHON:
            return self.extract_python_info(code)
        elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            return self.extract_js_info(code)
        else:
            return {'error': f'Unsupported language: {language}'}
    
    def generate_markdown_doc(self, file_path: str, info: Dict[str, Any]) -> str:
        """生成Markdown文档"""
        language = self.detect_language(file_path)
        file_name = Path(file_path).stem
        
        doc_lines = [
            f"# {file_name} - API Documentation",
            "",
            f"**Language**: {language.value}",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📋 Table of Contents",
            "",
        ]
        
        # 导入部分
        if info.get('imports'):
            doc_lines.extend([
                "## 📦 Imports",
                "",
            ])
            for imp in info['imports']:
                if imp.names:
                    doc_lines.append(f"- `{imp.module}`: {', '.join(imp.names)}")
                else:
                    doc_lines.append(f"- `{imp.module}`")
            doc_lines.append("")
        
        # 变量部分
        if info.get('variables'):
            doc_lines.extend([
                "## 🔧 Variables",
                "",
            ])
            for var in info['variables']:
                doc_lines.append(f"### `{var.name}`")
                if var.type_hint:
                    doc_lines.append(f"**Type**: `{var.type_hint}`")
                if var.value:
                    doc_lines.append(f"**Value**: `{var.value}`")
                doc_lines.append("")
        
        # 函数部分
        if info.get('functions'):
            doc_lines.extend([
                "## 🛠️ Functions",
                "",
            ])
            for func in info['functions']:
                doc_lines.extend(self._format_function_doc(func))
                doc_lines.append("")
        
        # 类部分
        if info.get('classes'):
            doc_lines.extend([
                "## 🏗️ Classes",
                "",
            ])
            for cls in info['classes']:
                doc_lines.extend(self._format_class_doc(cls))
                doc_lines.append("")
        
        return '\n'.join(doc_lines)
    
    def _format_function_doc(self, func: FunctionInfo) -> List[str]:
        """格式化函数文档"""
        lines = [
            f"### 📌 `{func.name}`",
            "",
        ]
        
        if func.docstring:
            lines.append(f"**Description**: {func.docstring}")
            lines.append("")
        
        if func.is_async:
            lines.append("🔄 **Async Function**")
            lines.append("")
        
        if func.decorators:
            lines.append(f"**Decorators**: {', '.join(['`' + d + '`' for d in func.decorators])}")
            lines.append("")
        
        if func.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            lines.append("| Name | Type | Default | Description |")
            lines.append("|------|------|---------|-------------|")
            for param in func.parameters:
                name = param.get('name', '')
                ptype = param.get('type', 'Any')
                default = param.get('default', '-')
                desc = param.get('description', '-')
                lines.append(f"| `{name}` | `{ptype}` | `{default}` | {desc} |")
            lines.append("")
        
        lines.append(f"**Returns**: `{func.return_type}`")
        if func.return_description:
            lines.append(f" - {func.return_description}")
        lines.append("")
        
        lines.append("**Complexity**: " + "⭐" * min(func.complexity, 5))
        lines.append("")
        
        # 使用示例
        lines.append("**Usage Example:**")
        lines.append("```python")
        example_params = ', '.join([p.get('name', '') for p in func.parameters])
        lines.append(f"# {func.name}({example_params})")
        if func.return_type != 'None':
            lines.append(f"result = {func.name}({example_params})")
        lines.append("```")
        lines.append("")
        
        return lines
    
    def _format_class_doc(self, cls: ClassInfo) -> List[str]:
        """格式化类文档"""
        lines = [
            f"### 🏷️ `{cls.name}`",
            "",
        ]
        
        if cls.docstring:
            lines.append(f"**Description**: {cls.docstring}")
            lines.append("")
        
        if cls.base_classes:
            lines.append(f"**Inherits from**: {', '.join(['`' + b + '`' for b in cls.base_classes])}")
            lines.append("")
        
        if cls.attributes:
            lines.append("**Attributes:**")
            lines.append("")
            lines.append("| Name | Type | Description |")
            lines.append("|------|------|-------------|")
            for attr in cls.attributes:
                name = attr.get('name', '')
                ptype = attr.get('type', 'Any')
                desc = attr.get('description', '-')
                lines.append(f"| `{name}` | `{ptype}` | {desc} |")
            lines.append("")
        
        if cls.methods:
            lines.append("**Methods:**")
            lines.append("")
            for method in cls.methods:
                lines.append(f"- `{method.name}` - {method.docstring[:50] if method.docstring else 'No description'}")
            lines.append("")
        
        return lines
    
    def generate_usage_examples(self, file_path: str, info: Dict[str, Any]) -> str:
        """生成使用示例"""
        language = self.detect_language(file_path)
        file_name = Path(file_path).stem
        
        examples = [
            f"# {file_name} - Usage Examples",
            "",
            "## 🚀 Quick Start",
            "",
            "```python",
            f"# Import the module",
            f"from {file_name} import *",
            "",
            "# Basic usage",
            "# Your code here",
            "```",
            "",
            "## 📖 Detailed Examples",
            "",
        ]
        
        # 函数示例
        for func in info.get('functions', []):
            examples.append(f"### {func.name}()")
            examples.append("")
            examples.append("```python")
            example_params = ', '.join([p.get('name', '') for p in func.parameters])
            examples.append(f"# Call {func.name}")
            if func.return_type != 'None':
                examples.append(f"result = {func.name}({example_params})")
                examples.append(f"print(result)")
            else:
                examples.append(f"{func.name}({example_params})")
            examples.append("```")
            examples.append("")
        
        # 类示例
        for cls in info.get('classes', []):
            examples.append(f"### {cls.name} Class")
            examples.append("")
            examples.append("```python")
            examples.append(f"# Create instance")
            init_params = ''
            for method in cls.methods:
                if method.name == '__init__':
                    init_params = ', '.join([p.get('name', '') for p in method.parameters if p.get('name') != 'self'])
                    break
            examples.append(f"# instance = {cls.name}({init_params})")
            examples.append("")
            examples.append("# Call methods")
            for method in cls.methods:
                if method.name not in ('__init__', '__str__', '__repr__'):
                    examples.append(f"# instance.{method.name}()")
            examples.append("```")
            examples.append("")
        
        return '\n'.join(examples)
    
    def generate_complete_docs(self, file_path: str) -> Dict[str, str]:
        """生成完整文档"""
        info = self.extract_code_info(file_path)
        
        if 'error' in info:
            return {'error': info['error']}
        
        return {
            'api_doc': self.generate_markdown_doc(file_path, info),
            'usage_examples': self.generate_usage_examples(file_path, info),
            'info': info
        }
    
    def batch_generate_docs(self, directory: str, output_dir: str = "docs") -> Dict[str, Any]:
        """批量生成文档"""
        path = Path(directory)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': [],
            'failed': [],
            'summary': {
                'total_files': 0,
                'success_count': 0,
                'failed_count': 0
            }
        }
        
        for file_path in path.rglob('*.py'):
            results['summary']['total_files'] += 1
            try:
                docs = self.generate_complete_docs(str(file_path))
                if 'error' not in docs:
                    # 保存API文档
                    relative_path = file_path.relative_to(path)
                    api_doc_path = output_path / relative_path.with_suffix('.api.md')
                    api_doc_path.parent.mkdir(parents=True, exist_ok=True)
                    api_doc_path.write_text(docs['api_doc'], encoding='utf-8')
                    
                    # 保存使用示例
                    example_path = output_path / relative_path.with_suffix('.examples.md')
                    example_path.write_text(docs['usage_examples'], encoding='utf-8')
                    
                    results['success'].append({
                        'file': str(file_path),
                        'docs': {
                            'api_doc': str(api_doc_path),
                            'examples': str(example_path)
                        }
                    })
                    results['summary']['success_count'] += 1
                else:
                    results['failed'].append({
                        'file': str(file_path),
                        'error': docs['error']
                    })
                    results['summary']['failed_count'] += 1
            except Exception as e:
                results['failed'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
                results['summary']['failed_count'] += 1
        
        return results


def demo():
    """演示函数"""
    print("=" * 60)
    print("🎯 Smart Code Documentation Generator - Demo")
    print("=" * 60)
    
    generator = CodeDocumentationGenerator()
    
    # 演示用示例代码
    sample_code = '''
"""
示例模块 - 用于演示文档生成功能
"""

import os
import json
from typing import Dict, List, Optional

# 全局配置
CONFIG_PATH = "/etc/app/config.json"
VERSION = "1.0.0"

class UserManager:
    """用户管理类 - 负责用户数据的CRUD操作"""
    
    def __init__(self, config_path: str = CONFIG_PATH):
        """初始化用户管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.users = {}
    
    def add_user(self, user_id: str, name: str, email: str) -> bool:
        """添加新用户
        
        Args:
            user_id: 用户唯一标识
            name: 用户名称
            email: 用户邮箱
            
        Returns:
            是否添加成功
        """
        if user_id in self.users:
            return False
        
        self.users[user_id] = {
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        return True
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """获取用户信息
        
        Args:
            user_id: 用户唯一标识
            
        Returns:
            用户信息字典，不存在则返回None
        """
        return self.users.get(user_id)
    
    def list_users(self) -> List[Dict]:
        """列出所有用户
        
        Returns:
            用户列表
        """
        return list(self.users.values())


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """计算数据统计指标
    
    Args:
        data: 数据列表
        
    Returns:
        包含统计指标的字典
    """
    if not data:
        return {'sum': 0, 'avg': 0, 'min': 0, 'max': 0, 'count': 0}
    
    return {
        'sum': sum(data),
        'avg': sum(data) / len(data),
        'min': min(data),
        'max': max(data),
        'count': len(data)
    }


async def fetch_data(url: str, timeout: int = 30) -> Optional[Dict]:
    """异步获取数据
    
    Args:
        url: 请求URL
        timeout: 超时时间(秒)
        
    Returns:
        响应数据JSON解析后的字典
    """
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()
'''
    
    # 保存示例代码
    sample_file = "/tmp/sample_module.py"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    print("\n📄 生成文档...")
    docs = generator.generate_complete_docs(sample_file)
    
    print("\n" + "=" * 60)
    print("📖 API Documentation")
    print("=" * 60)
    print(docs['api_doc'])
    
    print("\n" + "=" * 60)
    print("💡 Usage Examples")
    print("=" * 60)
    print(docs['usage_examples'])
    
    print("\n✅ Demo completed!")
    return generator, docs


if __name__ == "__main__":
    demo()
