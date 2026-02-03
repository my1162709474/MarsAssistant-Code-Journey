#!/usr/bin/env python3
"""
智能代码文档生成器 - Day 63
Auto-Documentation Generator

自动分析代码并生成专业文档，支持多种编程语言。
"""

import ast
import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import os


class DocstringStyle(Enum):
    """文档字符串风格"""
    GOOGLE = "google"
    SPHINX = "sphinx"
    NUMPY = "numpy"
    REESTRUCTUREDTEXT = "restructuredtext"
    AUTO = "auto"


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
    UNKNOWN = "unknown"


@dataclass
class FunctionDoc:
    """函数文档信息"""
    name: str
    params: List[Dict[str, str]] = field(default_factory=list)
    returns: str = ""
    description: str = ""
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    complexity: str = "medium"
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassDoc:
    """类文档信息"""
    name: str
    description: str = ""
    attributes: List[Dict[str, str]] = field(default_factory=list)
    methods: List[FunctionDoc] = field(default_factory=list)
    inheritance: str = ""
    decorators: List[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
    """模块文档信息"""
    file_path: str
    language: Language = Language.UNKNOWN
    description: str = ""
    author: str = ""
    version: str = ""
    created_date: str = ""
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    constants: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class PythonDocGenerator:
    """Python文档生成器"""
    
    def __init__(self, style: DocstringStyle = DocstringStyle.AUTO):
        self.style = style
        self.keywords = self._load_keywords()
    
    def _load_keywords(self) -> Dict[str, str]:
        """加载常用关键词翻译"""
        return {
            "init": "初始化",
            "process": "处理",
            "handle": "处理",
            "create": "创建",
            "get": "获取",
            "set": "设置",
            "update": "更新",
            "delete": "删除",
            "validate": "验证",
            "parse": "解析",
            "convert": "转换",
            "calculate": "计算",
            "analyze": "分析",
            "generate": "生成",
            "build": "构建",
            "execute": "执行",
            "run": "运行",
            "start": "启动",
            "stop": "停止",
            "reset": "重置",
            "clear": "清除",
            "add": "添加",
            "remove": "移除",
            "find": "查找",
            "search": "搜索",
            "filter": "过滤",
            "sort": "排序",
            "merge": "合并",
            "split": "拆分",
            "load": "加载",
            "save": "保存",
            "read": "读取",
            "write": "写入",
            "open": "打开",
            "close": "关闭",
            "connect": "连接",
            "disconnect": "断开",
            "send": "发送",
            "receive": "接收",
            "request": "请求",
            "response": "响应",
            "error": "错误",
            "success": "成功",
            "debug": "调试",
            "log": "日志",
            "print": "打印",
            "display": "显示",
            "render": "渲染",
            "draw": "绘制",
            "paint": "绘制",
        }
    
    def _translate(self, text: str) -> str:
        """中英文混合翻译"""
        words = re.findall(r'[A-Za-z]+', text)
        translated = text
        for word in words:
            lower_word = word.lower()
            if lower_word in self.keywords:
                translated = re.sub(
                    r'\b' + word + r'\b',
                    f"{self.keywords[lower_word]}({word})",
                    translated,
                    count=1
                )
        return translated
    
    def _get_param_type(self, param: ast.arg) -> str:
        """获取参数类型"""
        return "any"
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """获取返回值类型"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Subscript):
                if isinstance(node.returns.value, ast.Name):
                    base = node.returns.value.id
                else:
                    base = "any"
                if isinstance(node.returns.slice, ast.Name):
                    return f"{base}[{node.returns.slice.id}]"
                return f"{base}[...]"
        return ""
    
    def _analyze_complexity(self, node: ast.FunctionDef) -> str:
        """分析函数复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        if complexity <= 3:
            return "low"
        elif complexity <= 7:
            return "medium"
        elif complexity <= 12:
            return "high"
        return "critical"
    
    def _extract_docstring(self, node: ast.FunctionDef | ast.ClassDef) -> str:
        """提取文档字符串"""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.s, str)):
            return ast.get_docstring(node) or ""
        return ""
    
    def _parse_google_docstring(self, docstring: str) -> Dict[str, Any]:
        """解析Google风格文档字符串"""
        result = {
            "description": "",
            "args": [],
            "returns": "",
            "raises": [],
            "examples": []
        }
        
        lines = docstring.strip().split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.lower().startswith('args:'):
                current_section = "args"
            elif line.lower().startswith('returns:'):
                current_section = "returns"
            elif line.lower().startswith('raises:'):
                current_section = "raises"
            elif line.lower().startswith('example:'):
                current_section = "examples"
            elif current_section == "args" and line.startswith('-'):
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    result["args"].append({
                        "name": parts[0].strip(),
                        "type": parts[1].strip()
                    })
            elif current_section == "returns" and line:
                result["returns"] = line
            elif current_section == "raises" and line:
                result["raises"].append(line)
            elif current_section == "examples" and line:
                result["examples"].append(line)
            elif not current_section:
                result["description"] += line + " "
        
        return result
    
    def extract_class_info(self, node: ast.ClassDef) -> ClassDoc:
        """提取类信息"""
        doc = ClassDoc(name=node.name)
        doc.description = self._extract_docstring(node)
        
        # 提取基类
        if node.bases:
            doc.inheritance = ", ".join(
                b.id if isinstance(b, ast.Name) else "..." 
                for b in node.bases
            )
        
        # 提取装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                doc.decorators.append(decorator.id)
        
        # 提取属性
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_type = "any"
                if item.annotation:
                    if isinstance(item.annotation, ast.Name):
                        attr_type = item.annotation.id
                doc.attributes.append({
                    "name": item.target.id,
                    "type": attr_type,
                    "description": ""
                })
        
        # 提取方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self.extract_function_info(item)
                doc.methods.append(method_doc)
        
        return doc
    
    def extract_function_info(self, node: ast.FunctionDef) -> FunctionDoc:
        """提取函数信息"""
        doc = FunctionDoc(name=node.name)
        doc.description = self._extract_docstring(node)
        doc.complexity = self._analyze_complexity(node)
        
        # 提取参数
        for arg in node.args.args:
            if arg.arg != 'self':
                param = {
                    "name": arg.arg,
                    "type": self._get_param_type(arg),
                    "description": ""
                }
                doc.params.append(param)
        
        # 提取返回值
        doc.returns = self._get_return_type(node)
        
        # 提取装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                doc.decorators.append(decorator.id)
        
        return doc
    
    def extract_module_info(self, source: str, file_path: str) -> ModuleDoc:
        """提取模块信息"""
        module_doc = ModuleDoc(file_path=file_path)
        module_doc.language = Language.PYTHON
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"解析错误: {e}")
            return module_doc
        
        # 提取导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_doc.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_doc.imports.append(node.module)
        
        # 提取常量
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    if node.targets[0].id.isupper():
                        value = ""
                        if isinstance(node.value, ast.Constant):
                            value = str(node.value.value)
                        module_doc.constants.append({
                            "name": node.targets[0].id,
                            "value": value
                        })
        
        # 提取类和函数
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self.extract_class_info(node)
                module_doc.classes.append(class_doc)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    func_doc = self.extract_function_info(node)
                    module_doc.functions.append(func_doc)
        
        return module_doc
    
    def generate_google_docstring(self, func_doc: FunctionDoc) -> str:
        """生成Google风格文档字符串"""
        lines = []
        
        if func_doc.description:
            lines.append(func_doc.description)
            lines.append("")
        
        if func_doc.params:
            lines.append("Args:")
            for param in func_doc.params:
                name = param.get('name', '')
                ptype = param.get('type', '')
                desc = param.get('description', '')
                if desc:
                    lines.append(f"    {name} ({ptype}): {desc}")
                else:
                    lines.append(f"    {name} ({ptype}): ")
            lines.append("")
        
        if func_doc.returns:
            lines.append(f"Returns:")
            lines.append(f"    {func_doc.returns}")
            lines.append("")
        
        if func_doc.raises:
            lines.append("Raises:")
            for exc in func_doc.raises:
                lines.append(f"    {exc}")
            lines.append("")
        
        if func_doc.examples:
            lines.append("Examples:")
            for ex in func_doc.examples:
                lines.append(f"    {ex}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_markdown_doc(self, module_doc: ModuleDoc) -> str:
        """生成Markdown格式文档"""
        lines = []
        
        # 模块头部
        lines.append(f"# {module_doc.file_path}")
        lines.append("")
        if module_doc.description:
            lines.append(f"## 概述")
            lines.append("")
            lines.append(module_doc.description)
            lines.append("")
        
        # 元信息
        if module_doc.author or module_doc.version:
            lines.append("## 元信息")
            lines.append("")
            if module_doc.author:
                lines.append(f"- **作者**: {module_doc.author}")
            if module_doc.version:
                lines.append(f"- **版本**: {module_doc.version}")
            if module_doc.created_date:
                lines.append(f"- **创建日期**: {module_doc.created_date}")
            lines.append("")
        
        # 导入
        if module_doc.imports:
            lines.append("## 导入模块")
            lines.append("```python")
            for imp in module_doc.imports[:10]:
                lines.append(f"import {imp}")
            if len(module_doc.imports) > 10:
                lines.append(f"# ... 共 {len(module_doc.imports)} 个导入")
            lines.append("```")
            lines.append("")
        
        # 类
        if module_doc.classes:
            lines.append("## 类")
            lines.append("")
            for cls in module_doc.classes:
                lines.append(f"### {cls.name}")
                if cls.inheritance:
                    lines.append(f"继承自: `{cls.inheritance}`")
                if cls.description:
                    lines.append("")
                    lines.append(cls.description)
                if cls.attributes:
                    lines.append("")
                    lines.append("#### 属性")
                    lines.append("")
                    for attr in cls.attributes:
                        lines.append(f"- `{attr['name']}` ({attr['type']})")
                if cls.methods:
                    lines.append("")
                    lines.append("#### 方法")
                    lines.append("")
                    for method in cls.methods:
                        lines.append(f"##### `{method.name}()`")
                        lines.append(f"- 复杂度: {method.complexity}")
                        if method.params:
                            params_str = ", ".join(
                                f"`{p['name']}`" for p in method.params
                            )
                            lines.append(f"- 参数: {params_str}")
                        if method.returns:
                            lines.append(f"- 返回: {method.returns}")
                        lines.append("")
        
        # 函数
        if module_doc.functions:
            lines.append("## 函数")
            lines.append("")
            for func in module_doc.functions:
                lines.append(f"### `{func.name}()`")
                lines.append(f"- 复杂度: {func.complexity}")
                if func.params:
                    params_str = ", ".join(
                        f"`{p['name']}`" for p in func.params
                    )
                    lines.append(f"- 参数: {params_str}")
                if func.returns:
                    lines.append(f"- 返回: {func.returns}")
                if func.description:
                    lines.append("")
                    lines.append(func.description)
                lines.append("")
        
        # 常量
        if module_doc.constants:
            lines.append("## 常量")
            lines.append("")
            for const in module_doc.constants:
                lines.append(f"- `{const['name']}` = {const['value']}")
            lines.append("")
        
        # 使用示例
        lines.append("## 使用示例")
        lines.append("```python")
        lines.append(f"# 导入模块")
        module_name = os.path.basename(module_doc.file_path).replace('.py', '')
        lines.append(f"from {module_name} import *")
        lines.append("```")
        lines.append("")
        
        return "\n".join(lines)


class DocumentationGenerator:
    """多语言文档生成器"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.java': Language.JAVA,
        '.cpp': Language.CPP,
        '.cc': Language.CPP,
        '.c': Language.C_CPP,
        '.h': Language.C_CPP,
        '.go': Language.GO,
        '.rs': Language.RUST,
        '.rb': Language.RUBY,
        '.php': Language.PHP,
    }
    
    def __init__(self):
        self.python_generator = PythonDocGenerator()
    
    def detect_language(self, file_path: str) -> Language:
        """检测语言"""
        ext = os.path.splitext(file_path)[1].lower()
        return self.SUPPORTED_EXTENSIONS.get(ext, Language.UNKNOWN)
    
    def generate_doc(self, file_path: str, style: str = "markdown") -> str:
        """生成文档"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        language = self.detect_language(file_path)
        
        if language == Language.PYTHON:
            module_doc = self.python_generator.extract_module_info(source, file_path)
            return self.python_generator.generate_markdown_doc(module_doc)
        else:
            return self._generate_generic_doc(source, file_path, language)
    
    def _generate_generic_doc(self, source: str, file_path: str, language: Language) -> str:
        """生成通用文档"""
        lines = []
        lines.append(f"# {os.path.basename(file_path)}")
        lines.append(f"- 语言: {language.value}")
        lines.append(f"- 文件: {file_path}")
        lines.append("")
        
        # 统计信息
        code_lines = len([l for l in source.split('\n') if l.strip()])
        comment_lines = len([l for l in source.split('\n') if l.strip().startswith(('//', '#', '*'))])
        blank_lines = len(source.split('\n')) - code_lines - comment_lines
        
        lines.append("## 统计信息")
        lines.append(f"- 代码行数: {code_lines}")
        lines.append(f"- 注释行数: {comment_lines}")
        lines.append(f"- 空白行数: {blank_lines}")
        lines.append("")
        
        return "\n".join(lines)


def demo():
    """演示"""
    print("=" * 60)
    print("智能代码文档生成器 - Day 63")
    print("Auto-Documentation Generator")
    print("=" * 60)
    print()
    
    # 示例代码
    sample_code = '''
"""
示例模块 - 演示文档生成功能
"""

import os
import json
from typing import List, Dict

# 常量定义
MAX_SIZE = 1000
DEFAULT_TIMEOUT = 30

class DataProcessor:
    """数据处理器类 - 用于处理和分析数据"""
    
    def __init__(self, config: Dict[str, any] = None):
        """初始化数据处理器
        
        Args:
            config: 配置参数字典
        """
        self.config = config or {}
        self.data = []
    
    def load_from_file(self, file_path: str) -> bool:
        """从文件加载数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def process(self, callback=None) -> List[Dict]:
        """处理数据
        
        Args:
            callback: 处理回调函数
            
        Returns:
            处理后的数据列表
        """
        results = []
        for item in self.data:
            if callback:
                item = callback(item)
            results.append(item)
        return results


def validate_input(data: any, schema: Dict) -> bool:
    """验证输入数据是否符合模式
    
    Args:
        data: 输入数据
        schema: JSON Schema
        
    Returns:
        是否符合模式
    """
    if not data:
        return False
    return True


class APIClient:
    """API客户端 - 用于发送HTTP请求"""
    
    def __init__(self, base_url: str):
        """初始化API客户端
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.headers = {}
    
    def set_header(self, key: str, value: str):
        """设置请求头
        
        Args:
            key: 头名称
            value: 头值
        """
        self.headers[key] = value
    
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """发送GET请求
        
        Args:
            endpoint: 端点路径
            params: 查询参数
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}/{endpoint}"
        # 模拟请求
        return {"status": "ok", "url": url}
'''
    
    # 生成文档
    generator = PythonDocGenerator()
    module_doc = generator.extract_module_info(sample_code, "example.py")
    doc = generator.generate_markdown_doc(module_doc)
    
    print("生成的文档:")
    print("-" * 60)
    print(doc)
    print("-" * 60)
    
    print("\n📊 统计信息:")
    print(f"- 类数量: {len(module_doc.classes)}")
    print(f"- 函数数量: {len(module_doc.functions)}")
    print(f"- 导入数量: {len(module_doc.imports)}")
    print(f"- 常量数量: {len(module_doc.constants)}")
    
    print("\n✅ 文档生成演示完成!")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        demo()
        return
    
    command = sys.argv[1]
    
    if command == "demo":
        demo()
    elif command == "generate":
        if len(sys.argv) < 3:
            print("用法: generate <file_path> [--style markdown]")
            return
        
        file_path = sys.argv[2]
        style = "markdown"
        
        generator = DocumentationGenerator()
        doc = generator.generate_doc(file_path, style)
        
        output_path = file_path.replace('.py', '_docs.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc)
        
        print(f"文档已生成: {output_path}")
    else:
        print(f"未知命令: {command}")
        print("可用命令: demo, generate")


if __name__ == "__main__":
    main()
