#!/usr/bin/env python3
"""
智能代码文档生成器 - Day 53
Smart Code Documentation Generator

功能：
- 自动分析Python代码并生成文档字符串
- 支持函数、类、模块级别的文档生成
- 智能推断参数类型和返回值
- 支持多种文档格式（Google/NumPy/Sphinx）
- 批量处理整个项目
"""

import ast
import os
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class FunctionInfo:
    """函数信息类"""
    name: str
    lineno: int
    args: List[str]
    defaults: List[Any]
    returns: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """类信息类"""
    name: str
    lineno: int
    docstring: str = ""
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)


class CodeAnalyzer(ast.NodeVisitor):
    """Python代码分析器"""
    
    def __init__(self):
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.classes_stack: List[ClassInfo] = []
        self.module_docstring: str = ""
        
    def visit_FunctionDef(self, node):
        """访问函数定义"""
        func_info = self._extract_function_info(node)
        
        if self.classes_stack:
            self.classes_stack[-1].methods.append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """访问异步函数定义"""
        node.name = f"async_{node.name}"  # 标记为异步函数
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        """访问类定义"""
        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno
        )
        
        # 提取类的docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            class_info.docstring = node.body[0].value.value
        
        self.classes_stack.append(class_info)
        self.generic_visit(node)
        self.classes_stack.pop()
        
        self.classes.append(class_info)
    
    def visit_Module(self, node):
        """访问模块"""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            self.module_docstring = node.body[0].value.value
        self.generic_visit(node)
    
    def _extract_function_info(self, node) -> FunctionInfo:
        """提取函数信息"""
        args_list = []
        defaults_list = []
        
        if node.args.args:
            for arg in node.args.args:
                args_list.append(arg.arg)
        
        if node.args.defaults:
            for default in node.args.defaults:
                defaults_list.append(self._get_default_value(default))
        
        # 提取返回值类型
        returns = ""
        if node.returns and isinstance(node.returns, ast.Name):
            returns = node.returns.id
        elif node.returns and isinstance(node.returns, ast.Constant):
            returns = str(node.returns.value)
        
        # 提取现有docstring
        docstring = ""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)
        
        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            args=args_list,
            defaults=defaults_list,
            returns=returns,
            docstring=docstring,
            decorators=decorators
        )
    
    def _get_default_value(self, node) -> Any:
        """获取默认值"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return "..."
        elif isinstance(node, ast.List):
            return []
        elif isinstance(node, ast.Dict):
            return {}
        elif isinstance(node, ast.Tuple):
            return ()
        return None


class DocumentationGenerator:
    """文档生成器类"""
    
    def __init__(self, style: str = "google"):
        self.style = style
        self.type_hints = {
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'list': 'List[Any]',
            'dict': 'Dict[str, Any]',
            'tuple': 'tuple',
            'set': 'set',
            'bytes': 'bytes',
            'object': 'object',
            'None': 'None',
            'pathlib.Path': 'Path',
            'pathlib.PosixPath': 'Path'
        }
    
    def generate_module_docstring(self, analyzer: CodeAnalyzer, filename: str) -> str:
        """生成模块级文档字符串"""
        date = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f'"""',
            f'{filename} - 智能代码文档生成',
            '',
            f'创建日期: {date}',
            '',
            '功能：自动生成的文档字符串',
            '"""'
        ]
        return '\n'.join(lines)
    
    def generate_function_docstring(self, func: FunctionInfo, indent: str = "") -> str:
        """生成函数文档字符串"""
        if self.style == "google":
            return self._generate_google_style(func, indent)
        elif self.style == "numpy":
            return self._generate_numpy_style(func, indent)
        elif self.style == "sphinx":
            return self._generate_sphinx_style(func, indent)
        return self._generate_google_style(func, indent)
    
    def _generate_google_style(self, func: FunctionInfo, indent: str) -> str:
        """生成Google风格的文档字符串"""
        lines = [f'{indent}"""']
        
        # 函数描述
        desc = self._get_func_description(func)
        lines.append(f'{indent}{desc}')
        lines.append(f'{indent}')
        
        # 参数
        if func.args:
            lines.append(f'{indent}Args:')
            for i, arg in enumerate(func.args):
                param_type = self._infer_param_type(func, arg)
                default_val = ""
                if func.defaults and i < len(func.defaults):
                    default_val = f", optional"
                lines.append(f'{indent}    {arg} ({param_type}): {default_val}')
            lines.append(f'{indent}')
        
        # 返回值
        if func.returns:
            lines.append(f'{indent}Returns:')
            lines.append(f'{indent}    {func.returns}: 函数返回值说明')
            lines.append(f'{indent}')
        
        # 异步标记
        if func.name.startswith('async_'):
            lines.append(f'{indent}    async function')
            lines.append(f'{indent}')
        
        lines.append(f'{indent}"""')
        return '\n'.join(lines)
    
    def _generate_numpy_style(self, func: FunctionInfo, indent: str) -> str:
        """生成NumPy风格的文档字符串"""
        lines = [f'{indent}"""']
        
        desc = self._get_func_description(func)
        lines.append(f'{indent}{desc}')
        lines.append(f'{indent}')
        
        # 参数
        if func.args:
            lines.append(f'{indent}Parameters')
            lines.append(f'{indent}----------')
            for i, arg in enumerate(func.args):
                param_type = self._infer_param_type(func, arg)
                default_val = ""
                if func.defaults and i < len(func.defaults):
                    default_val = f"optional"
                lines.append(f'{indent}{arg} : {param_type}')
                lines.append(f'{indent}    Parameter description {default_val}')
            lines.append(f'{indent}')
        
        # 返回值
        if func.returns:
            lines.append(f'{indent}Returns')
            lines.append(f'{indent}-------')
            lines.append(f'{indent}{func.returns}')
            lines.append(f'{indent}    Return value description')
            lines.append(f'{indent}')
        
        lines.append(f'{indent}"""')
        return '\n'.join(lines)
    
    def _generate_sphinx_style(self, func: FunctionInfo, indent: str) -> str:
        """生成Sphinx/ReadTheDocs风格的文档字符串"""
        lines = [f'{indent}"""']
        
        desc = self._get_func_description(func)
        lines.append(f'{indent}{desc}')
        lines.append(f'{indent}')
        
        # 参数
        if func.args:
            lines.append(f'{indent}:param {func.name}:')
            for arg in func.args:
                lines.append(f'{indent}    :param {arg}: Parameter description')
            lines.append(f'{indent}')
        
        # 返回值
        if func.returns:
            lines.append(f'{indent}:returns: Return value description')
            lines.append(f'{indent}:rtype: {func.returns}')
            lines.append(f'{indent}')
        
        lines.append(f'{indent}"""')
        return '\n'.join(lines)
    
    def _get_func_description(self, func: FunctionInfo) -> str:
        """获取函数描述"""
        func_name = func.name
        if func_name.startswith('async_'):
            func_name = func_name[5:]
        
        descriptions = {
            'analyze': '分析Python代码并提取信息',
            'generate': '生成文档字符串',
            'extract': '提取特定信息',
            'validate': '验证数据或参数',
            'process': '处理数据',
            'transform': '转换数据格式',
            'parse': '解析输入数据',
            'format': '格式化输出',
            'create': '创建新对象或文件',
            'update': '更新现有数据',
            'delete': '删除对象或数据',
            'get': '获取信息',
            'set': '设置属性',
            'calculate': '计算数值',
            'compute': '计算结果',
            'initialize': '初始化对象或状态',
            'run': '执行操作',
            'execute': '执行命令或函数',
            'handle': '处理事件或请求',
            'build': '构建对象或数据'
        }
        
        base_name = func_name.lower().replace('_', '')
        for key, desc in descriptions.items():
            if key in base_name:
                return desc
        
        return f'{func_name.replace("_", " ").title()}函数'
    
    def _infer_param_type(self, func: FunctionInfo, param: str) -> str:
        """推断参数类型"""
        # 检查默认值的类型
        if func.defaults:
            for i, arg in enumerate(func.args):
                if arg == param and i < len(func.defaults):
                    default = func.defaults[i]
                    if isinstance(default, str):
                        return 'str'
                    elif isinstance(default, bool):
                        return 'bool'
                    elif isinstance(default, int):
                        return 'int'
                    elif isinstance(default, float):
                        return 'float'
                    elif isinstance(default, list):
                        return 'List[Any]'
                    elif isinstance(default, dict):
                        return 'Dict[str, Any]'
        
        # 检查参数名推断类型
        param_lower = param.lower()
        if 'name' in param_lower or 'string' in param_lower:
            return 'str'
        elif 'count' in param_lower or 'index' in param_lower or 'num' in param_lower:
            return 'int'
        elif 'flag' in param_lower or 'is_' in param_lower or 'has_' in param_lower:
            return 'bool'
        elif 'list' in param_lower or 'items' in param_lower:
            return 'List[Any]'
        elif 'dict' in param_lower or 'map' in param_lower or 'data' in param_lower:
            return 'Dict[str, Any]'
        elif 'path' in param_lower:
            return 'Path'
        elif 'file' in param_lower:
            return 'Path or str'
        
        return 'Any'
    
    def generate_class_docstring(self, class_info: ClassInfo, indent: str = "") -> str:
        """生成类文档字符串"""
        lines = [f'{indent}"""']
        lines.append(f'{indent}{class_info.name}类')
        lines.append(f'{indent}')
        lines.append(f'{indent}功能说明：{self._get_class_description(class_info)}')
        
        if class_info.attributes:
            lines.append(f'{indent}')
            lines.append(f'{indent}Attributes:')
            for attr in class_info.attributes:
                lines.append(f'{indent}    {attr} (Any): 属性说明')
        
        if class_info.methods:
            lines.append(f'{indent}')
            lines.append(f'{indent}Methods:')
            for method in class_info.methods:
                lines.append(f'{indent}    {method.name}: {method.name.replace("_", " ").title()}')
        
        lines.append(f'{indent}"""')
        return '\n'.join(lines)
    
    def _get_class_description(self, class_info: ClassInfo) -> str:
        """获取类描述"""
        name_lower = class_info.name.lower()
        
        if 'analyzer' in name_lower:
            return '代码分析器，用于分析Python代码结构'
        elif 'generator' in name_lower:
            return '文档生成器，用于生成代码文档'
        elif 'parser' in name_lower:
            return '解析器，用于解析和转换数据'
        elif 'handler' in name_lower:
            return '处理器，用于处理特定类型的请求或数据'
        elif 'manager' in name_lower:
            return '管理器，用于管理特定资源或功能'
        elif 'builder' in name_lower:
            return '构建器，用于构建复杂对象'
        elif 'service' in name_lower:
            return '服务类，提供特定功能的接口'
        elif 'util' in name_lower or 'utility' in name_lower:
            return '工具类，提供通用工具函数'
        elif 'info' in name_lower:
            return '信息类，存储和管理特定信息'
        
        return f'{class_info.name}类'


class SmartDocGenerator:
    """智能文档生成器主类"""
    
    def __init__(self, style: str = "google"):
        self.analyzer = CodeAnalyzer()
        self.generator = DocumentationGenerator(style)
        self.style = style
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
            self.analyzer = CodeAnalyzer()
            self.analyzer.visit(tree)
            
            return {
                'file_path': file_path,
                'module_docstring': self.analyzer.module_docstring,
                'functions': [self._func_to_dict(f) for f in self.analyzer.functions],
                'classes': [self._class_to_dict(c) for c in self.analyzer.classes],
                'success': True
            }
        except SyntaxError as e:
            return {
                'file_path': file_path,
                'error': f'语法错误: {e}',
                'success': False
            }
    
    def generate_documentation(self, file_path: str, output_path: Optional[str] = None) -> str:
        """为文件生成文档字符串"""
        analysis = self.analyze_file(file_path)
        
        if not analysis['success']:
            return f"错误: {analysis.get('error', 'Unknown error')}"
        
        doc_lines = []
        
        # 模块文档
        if analysis['module_docstring']:
            doc_lines.append(analysis['module_docstring'])
        else:
            doc_lines.append(self.generator.generate_module_docstring(
                self.analyzer, 
                os.path.basename(file_path)
            ))
        
        doc_lines.append('')  # 空行
        
        # 函数文档
        for func in analysis['functions']:
            if not func['docstring']:
                func_obj = self._dict_to_func(func)
                doc_lines.append(self.generator.generate_function_docstring(func_obj))
            doc_lines.append('')  # 空行
        
        # 类文档
        for class_info in analysis['classes']:
            if not class_info['docstring']:
                class_obj = self._dict_to_class(class_info)
                doc_lines.append(self.generator.generate_class_docstring(class_obj))
            doc_lines.append('')  # 空行
        
        doc_content = '\n'.join(doc_lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        return doc_content
    
    def batch_process(self, directory: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """批量处理目录中的所有Python文件"""
        results = {}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    if output_dir:
                        rel_path = os.path.relpath(file_path, directory)
                        output_path = os.path.join(output_dir, rel_path)
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    else:
                        output_path = None
                    
                    doc = self.generate_documentation(file_path, output_path)
                    results[file_path] = doc
        
        return results
    
    def _func_to_dict(self, func: FunctionInfo) -> Dict[str, Any]:
        """将FunctionInfo转换为字典"""
        return {
            'name': func.name,
            'lineno': func.lineno,
            'args': func.args,
            'defaults': func.defaults,
            'returns': func.returns,
            'docstring': func.docstring,
            'decorators': func.decorators
        }
    
    def _class_to_dict(self, class_info: ClassInfo) -> Dict[str, Any]:
        """将ClassInfo转换为字典"""
        return {
            'name': class_info.name,
            'lineno': class_info.lineno,
            'docstring': class_info.docstring,
            'methods': [self._func_to_dict(m) for m in class_info.methods],
            'attributes': class_info.attributes
        }
    
    def _dict_to_func(self, func_dict: Dict[str, Any]) -> FunctionInfo:
        """将字典转换为FunctionInfo"""
        return FunctionInfo(
            name=func_dict['name'],
            lineno=func_dict['lineno'],
            args=func_dict['args'],
            defaults=func_dict['defaults'],
            returns=func_dict['returns'],
            docstring=func_dict['docstring'],
            decorators=func_dict['decorators']
        )
    
    def _dict_to_class(self, class_dict: Dict[str, Any]) -> ClassInfo:
        """将字典转换为ClassInfo"""
        return ClassInfo(
            name=class_dict['name'],
            lineno=class_dict['lineno'],
            docstring=class_dict['docstring'],
            methods=[self._dict_to_func(m) for m in class_dict['methods']],
            attributes=class_dict['attributes']
        )


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='智能代码文档生成器 - 自动为Python代码生成文档字符串'
    )
    parser.add_argument(
        'input', 
        help='输入文件或目录路径'
    )
    parser.add_argument(
        '-o', '--output',
        help='输出文件或目录路径（可选）'
    )
    parser.add_argument(
        '-s', '--style',
        choices=['google', 'numpy', 'sphinx'],
        default='google',
        help='文档风格（默认: google）'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录（输入为目录时）'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='在终端显示生成的文档'
    )
    
    args = parser.parse_args()
    
    generator = SmartDocGenerator(style=args.style)
    
    # 检查输入是文件还是目录
    if os.path.isfile(args.input):
        # 单文件处理
        doc = generator.generate_documentation(args.input, args.output)
        
        if args.show:
            print(doc)
            print('\n' + '='*60)
        
        print(f"✅ 文档已生成: {args.output or 'stdout'}")
    
    elif os.path.isdir(args.input):
        # 目录处理
        if not args.recursive:
            print("⚠️  警告: 输入是目录，使用 -r 参数递归处理子目录")
            return
        
        output_dir = args.output or args.input + '_docs'
        results = generator.batch_process(args.input, output_dir)
        
        print(f"✅ 已处理 {len(results)} 个文件")
        print(f"📁 文档保存在: {output_dir}")
        
        for file_path, doc in list(results.items())[:3]:  # 显示前3个
            print(f"\n📄 {file_path}:")
            print(doc[:200] + '...' if len(doc) > 200 else doc)
    
    else:
        print(f"❌ 错误: 找不到文件或目录: {args.input}")


if __name__ == "__main__":
    main()
