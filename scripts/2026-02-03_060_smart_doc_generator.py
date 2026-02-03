#!/usr/bin/env python3
"""
智能代码文档生成器 - Smart Code Documentation Generator
自动为代码生成API文档、注释和README

功能:
- 自动分析代码结构
- 生成API文档
- 创建使用示例
- 支持多种编程语言

使用方法:
    python smart_doc_generator.py analyze main.py
    python smart_doc_generator.py generate main.py --format markdown
    python smart_doc_generator.py demo
"""

import ast
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
import argparse


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"


@dataclass
class FunctionDoc:
    """函数文档信息"""
    name: str
    docstring: str = ""
    params: List[Dict] = field(default_factory=list)
    returns: str = ""
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    complexity: int = 1


@dataclass
class ClassDoc:
    """类文档信息"""
    name: str
    docstring: str = ""
    methods: List[FunctionDoc] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    line_number: int = 0
    inheritance: str = ""


@dataclass
class FileDoc:
    """文件文档信息"""
    path: str
    language: Language = Language.UNKNOWN
    description: str = ""
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    examples: str = ""


class PythonDocGenerator:
    """Python文档生成器"""
    
    @staticmethod
    def extract_docstring(docstring: str) -> str:
        """提取清洁的文档字符串"""
        if not docstring:
            return ""
        # 移除缩进
        lines = docstring.strip().split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned.append(stripped)
        return ' '.join(cleaned)
    
    @staticmethod
    def parse_param(param: ast.arg) -> Dict:
        """解析参数信息"""
        return {
            "name": param.arg,
            "type": "Any",
            "description": ""
        }
    
    @staticmethod
    def get_type_hint(annotation: ast.AST) -> str:
        """获取类型提示"""
        if annotation is None:
            return "Any"
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                base = annotation.value.id
            else:
                base = "Any"
            if isinstance(annotation.slice, ast.Tuple):
                args = ", ".join([PythonDocGenerator.get_type_hint(a) for a in annotation.slice.elts])
                return f"{base}[{args}]"
            else:
                return f"{base}[{PythonDocGenerator.get_type_hint(annotation.slice)}]"
        elif isinstance(annotation, ast.BinOp):
            return "Any"
        return "Any"
    
    @classmethod
    def analyze_file(cls, content: str, file_path: str) -> FileDoc:
        """分析Python文件"""
        doc = FileDoc(path=file_path, language=Language.PYTHON)
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            doc.description = "Syntax error - unable to parse"
            return doc
        
        # 收集导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    doc.imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    doc.imports.append(f"from {module} import {alias.name}")
        
        # 分析类
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = ClassDoc(
                    name=node.name,
                    line_number=node.lineno
                )
                
                # 文档字符串
                if node.body and isinstance(node.body[0], ast.Expr):
                    class_doc.docstring = cls.extract_docstring(ast.get_docstring(node))
                
                # 基类
                if node.bases:
                    class_doc.inheritance = ", ".join([cls.get_type_hint(base) for base in node.bases])
                
                # 分析方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        func_doc = cls.analyze_function(item)
                        class_doc.methods.append(func_doc)
                        if func_doc.name.startswith('_') and not func_doc.name.startswith('__'):
                            class_doc.attributes.append(func_doc.name)
                
                # 属性
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        class_doc.attributes.append(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_doc.attributes.append(target.id)
                
                doc.classes.append(class_doc)
        
        # 分析顶层函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef) if hasattr(node, 'parent') else True:
                # 检查是否在类外
                is_toplevel = True
                for child in ast.walk(tree):
                    if isinstance(child, ast.ClassDef):
                        for item in child.body:
                            if item is node:
                                is_toplevel = False
                                break
                if is_toplevel:
                    doc.functions.append(cls.analyze_function(node))
        
        # 分析常量
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    name = node.targets[0].id
                    if name.isupper() and not name.startswith('_'):
                        doc.constants.append(name)
        
        # 生成描述
        if doc.classes:
            doc.description = f"Python module with {len(doc.classes)} class(es) and {len(doc.functions)} function(s)"
        elif doc.functions:
            doc.description = f"Python module with {len(doc.functions)} function(s)"
        else:
            doc.description = "Python module"
        
        return doc
    
    @classmethod
    def analyze_function(cls, node: ast.FunctionDef) -> FunctionDoc:
        """分析函数"""
        func_doc = FunctionDoc(
            name=node.name,
            line_number=node.lineno
        )
        
        # 装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_doc.decorators.append(f"@{decorator.id}")
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                func_doc.decorators.append(f"@{decorator.func.id}(...)")
        
        # 文档字符串
        if node.body and isinstance(node.body[0], ast.Expr):
            func_doc.docstring = cls.extract_docstring(ast.get_docstring(node))
        
        # 参数
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                param = cls.parse_param(arg)
                if arg.annotation:
                    param["type"] = cls.get_type_hint(arg.annotation)
                func_doc.params.append(param)
        
        # 返回类型
        if node.returns:
            func_doc.returns = cls.get_type_hint(node.returns)
        
        # 简单复杂度计算
        func_doc.complexity = cls.calculate_complexity(node)
        
        return func_doc
    
    @staticmethod
    def calculate_complexity(node: ast.AST) -> int:
        """计算函数复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Compare)):
                complexity += 1
        return complexity
    
    @classmethod
    def generate_markdown(cls, doc: FileDoc) -> str:
        """生成Markdown文档"""
        lines = []
        
        # 标题
        lines.append(f"# {Path(doc.path).stem}")
        lines.append("")
        lines.append(f"**Language:** {doc.language.value}")
        lines.append("")
        lines.append(f">{doc.description}")
        lines.append("")
        
        # 目录
        if doc.classes or doc.functions:
            lines.append("## Table of Contents")
            lines.append("")
            if doc.classes:
                lines.append("- [Classes](#classes)")
                for class_doc in doc.classes:
                    lines.append(f"  - [{class_doc.name}](#{class_doc.name.lower()})")
            if doc.functions:
                lines.append("- [Functions](#functions)")
            lines.append("")
        
        # 导入
        if doc.imports:
            lines.append("## Imports")
            lines.append("```python")
            for imp in doc.imports[:10]:  # 限制数量
                lines.append(imp)
            if len(doc.imports) > 10:
                lines.append(f"# ... and {len(doc.imports) - 10} more")
            lines.append("```")
            lines.append("")
        
        # 类
        if doc.classes:
            lines.append("## Classes")
            lines.append("")
            for class_doc in doc.classes:
                lines.append(f"### `{class_doc.name}`")
                lines.append("")
                if class_doc.inheritance:
                    lines.append(f"*Inherits from: {class_doc.inheritance}*")
                    lines.append("")
                if class_doc.docstring:
                    lines.append(f"{class_doc.docstring}")
                    lines.append("")
                if class_doc.attributes:
                    lines.append("**Attributes:**")
                    lines.append("")
                    for attr in class_doc.attributes:
                        lines.append(f"- `{attr}`")
                    lines.append("")
                
                # 方法
                if class_doc.methods:
                    lines.append("**Methods:**")
                    lines.append("")
                    for method in class_doc.methods:
                        lines.append(f"#### `{method.name}`")
                        if method.decorators:
                            for dec in method.decorators:
                                lines.append(f"{dec}")
                        if method.docstring:
                            lines.append("")
                            lines.append(f"{method.docstring}")
                        if method.params:
                            lines.append("")
                            lines.append("**Parameters:**")
                            lines.append("")
                            for param in method.params:
                                lines.append(f"- `{param['name']}` ({param['type']})")
                        if method.returns:
                            lines.append("")
                            lines.append(f"**Returns:** `{method.returns}`")
                        lines.append("")
                    lines.append("")
        
        # 函数
        if doc.functions:
            lines.append("## Functions")
            lines.append("")
            for func in doc.functions:
                lines.append(f"### `{func.name}`")
                lines.append("")
                if func.decorators:
                    for dec in func.decorators:
                        lines.append(f"{dec}")
                if func.docstring:
                    lines.append("")
                    lines.append(f"{func.docstring}")
                if func.params:
                    lines.append("")
                    lines.append("**Parameters:**")
                    lines.append("")
                    for param in func.params:
                        lines.append(f"- `{param['name']}` ({param['type']})")
                if func.returns:
                    lines.append("")
                    lines.append(f"**Returns:** `{func.returns}`")
                lines.append("")
        
        # 常量
        if doc.constants:
            lines.append("## Constants")
            lines.append("")
            for const in doc.constants:
                lines.append(f"- `{const}`")
            lines.append("")
        
        # 使用示例
        lines.append("## Usage Examples")
        lines.append("```python")
        lines.append(f"# Import the module")
        module_name = Path(doc.path).stem
        if doc.classes:
            lines.append(f"from {module_name} import {doc.classes[0].name}")
        elif doc.functions:
            lines.append(f"from {module_name} import {doc.functions[0].name}")
        lines.append("```")
        lines.append("")
        
        return '\n'.join(lines)


class DocumentationGenerator:
    """文档生成器主类"""
    
    def __init__(self):
        self.generators = {
            Language.PYTHON: PythonDocGenerator,
        }
    
    def analyze(self, file_path: str) -> FileDoc:
        """分析文件并提取文档信息"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        language = self.detect_language(file_path)
        
        generator = self.generators.get(language)
        if not generator:
            # 默认使用Python生成器
            generator = PythonDocGenerator
        
        return generator.analyze_file(content, file_path)
    
    def generate(self, file_path: str, format: str = 'markdown') -> str:
        """生成文档"""
        doc = self.analyze(file_path)
        
        if format == 'markdown':
            return PythonDocGenerator.generate_markdown(doc)
        elif format == 'json':
            return self.to_json(doc)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def detect_language(self, file_path: str) -> Language:
        """检测编程语言"""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.java': Language.JAVA,
            '.go': Language.GO,
            '.rs': Language.RUST,
        }
        
        return language_map.get(ext, Language.UNKNOWN)
    
    def to_json(self, doc: FileDoc) -> str:
        """转换为JSON"""
        return json.dumps({
            "path": doc.path,
            "language": doc.language.value,
            "description": doc.description,
            "classes": [
                {
                    "name": c.name,
                    "docstring": c.docstring,
                    "methods": [
                        {
                            "name": m.name,
                            "docstring": m.docstring,
                            "params": m.params,
                            "returns": m.returns,
                            "complexity": m.complexity
                        }
                        for m in c.methods
                    ],
                    "attributes": c.attributes,
                    "inheritance": c.inheritance
                }
                for c in doc.classes
            ],
            "functions": [
                {
                    "name": f.name,
                    "docstring": f.docstring,
                    "params": f.params,
                    "returns": f.returns,
                    "complexity": f.complexity
                }
                for f in doc.functions
            ],
            "imports": doc.imports,
            "constants": doc.constants
        }, indent=2, ensure_ascii=False)


def demo():
    """演示文档生成"""
    print("🧪 智能代码文档生成器演示")
    print("=" * 50)
    
    # 创建示例代码
    sample_code = '''
"""示例模块 - 演示文档生成功能"""

import json
from typing import List, Dict, Optional
import datetime


class UserManager:
    """用户管理类 - 演示类文档生成"""
    
    def __init__(self, debug: bool = False):
        """初始化用户管理器
        
        Args:
            debug: 是否启用调试模式
        """
        self.debug = debug
        self.users: List[Dict] = []
    
    def add_user(self, name: str, email: str, age: Optional[int] = None) -> bool:
        """添加新用户
        
        Args:
            name: 用户名
            email: 邮箱地址
            age: 年龄（可选）
        
        Returns:
            是否添加成功
        """
        if self.debug:
            print(f"Adding user: {name}")
        return True
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典，未找到返回None
        """
        for user in self.users:
            if user.get('id') == user_id:
                return user
        return None
    
    def list_users(self) -> List[Dict]:
        """列出所有用户
        
        Returns:
            用户列表
        """
        return self.users


def calculate_stats(numbers: List[float]) -> Dict[str, float]:
    """计算数值统计信息
    
    Args:
        numbers: 数值列表
    
    Returns:
        包含统计信息的字典
    """
    if not numbers:
        return {"sum": 0, "average": 0, "max": 0, "min": 0}
    
    total = sum(numbers)
    return {
        "sum": total,
        "average": total / len(numbers),
        "max": max(numbers),
        "min": min(numbers)
    }


# 示例常量
DEFAULT_TIMEOUT = 30
MAX_RETRY_COUNT = 3
'''
    
    # 保存示例文件
    sample_file = Path("/tmp/sample_module.py")
    sample_file.write_text(sample_code)
    
    # 生成文档
    generator = DocumentationGenerator()
    
    print("\n📊 分析结果:")
    doc = generator.analyze(str(sample_file))
    print(f"  - 语言: {doc.language.value}")
    print(f"  - 描述: {doc.description}")
    print(f"  - 类: {len(doc.classes)}")
    print(f"  - 函数: {len(doc.functions)}")
    print(f"  - 常量: {len(doc.constants)}")
    
    if doc.classes:
        print(f"\n📝 类详情:")
        for cls in doc.classes:
            print(f"  - {cls.name} ({len(cls.methods)} methods)")
    
    print("\n📄 生成的Markdown文档:")
    print("-" * 50)
    md = generator.generate(str(sample_file), format='markdown')
    print(md)
    
    # 清理
    sample_file.unlink()
    
    print("\n✅ 演示完成!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能代码文档生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s analyze main.py          # 分析文件
    %(prog)s generate main.py         # 生成Markdown文档
    %(prog)s generate main.py --format json  # 生成JSON文档
    %(prog)s demo                     # 运行演示
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析代码文件")
    analyze_parser.add_argument("file", help="代码文件路径")
    
    # generate命令
    generate_parser = subparsers.add_parser("generate", help="生成文档")
    generate_parser.add_argument("file", help="代码文件路径")
    generate_parser.add_argument("--format", default="markdown", 
                                choices=["markdown", "json"],
                                help="输出格式")
    generate_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # demo命令
    subparsers.add_parser("demo", help="运行演示")
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator()
    
    if args.command == "analyze":
        doc = generator.analyze(args.file)
        print(f"📊 分析结果: {doc.path}")
        print(f"  语言: {doc.language.value}")
        print(f"  描述: {doc.description}")
        print(f"  类: {len(doc.classes)}")
        print(f"  函数: {len(doc.functions)}")
        print(f"  常量: {len(doc.constants)}")
        print(f"  导入: {len(doc.imports)}")
        
    elif args.command == "generate":
        output = generator.generate(args.file, args.format)
        
        if args.output:
            Path(args.output).write_text(output)
            print(f"✅ 文档已保存到: {args.output}")
        else:
            print(output)
    
    elif args.command == "demo":
        demo()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
