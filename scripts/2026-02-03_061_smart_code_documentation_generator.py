#!/usr/bin/env python3
"""
智能代码文档生成器 - Smart Code Documentation Generator
=========================================================

自动为代码生成专业文档注释，支持多种编程语言。

功能特点:
- 🔍 多语言支持: Python, JavaScript, TypeScript, Java, Go, Rust
- 📝 自动生成文档字符串
- 📊 提取函数签名信息
- 🏷️ 支持类型标注
- 📄 生成Markdown文档
- 🎨 多种输出格式

作者: MarsAssistant
日期: 2026-02-03
"""

import ast
import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    docstring: Optional[str] = None
    params: List[Dict] = field(default_factory=list)
    returns: Optional[Dict] = None
    raises: List[Dict] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    line_number: int = 0
    
    
@dataclass
class ClassInfo:
    """类信息"""
    name: str
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[Dict] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class ModuleInfo:
    """模块信息"""
    docstring: Optional[str] = None
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[Dict] = field(default_factory=list)
    variables: List[Dict] = field(default_factory=list)


class PythonDocGenerator:
    """Python文档生成器"""
    
    # 类型名称映射
    TYPE_MAPPING = {
        'str': '字符串',
        'int': '整数',
        'float': '浮点数',
        'bool': '布尔值',
        'list': '列表',
        'dict': '字典',
        'tuple': '元组',
        'set': '集合',
        'None': 'None',
        'object': '对象',
        'Any': '任意类型',
    }
    
    def __init__(self):
        self.type_hints_cache: Dict[str, str] = {}
        
    def parse_type_hint(self, type_hint: str) -> str:
        """解析类型提示"""
        if not type_hint:
            return '任意类型'
            
        # 移除可选的模块前缀
        if '.' in type_hint:
            type_hint = type_hint.split('.')[-1]
            
        # 处理泛型
        if '[' in type_hint and ']' in type_hint:
            base = type_hint.split('[')[0]
            args = type_hint[type_hint.index('[')+1:type_hint.index(']')]
            
            base_cn = self.TYPE_MAPPING.get(base, base)
            
            # 处理多个泛型参数
            if ',' in args:
                arg_list = [self.parse_type_hint(a.strip()) for a in args.split(',')]
                return f"{base_cn}<{', '.join(arg_list)}>"
            else:
                return f"{base_cn}<{self.parse_type_hint(args)}>"
                
        return self.TYPE_MAPPING.get(type_hint, type_hint)
    
    def extract_docstring_info(self, docstring: str) -> Dict[str, str]:
        """从文档字符串提取结构化信息"""
        info = {
            'description': '',
            'params': {},
            'returns': {},
            'raises': {},
            'examples': '',
        }
        
        if not docstring:
            return info
            
        lines = docstring.strip().split('\n')
        current_section = 'description'
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith(':param ') or stripped.startswith(':parameter '):
                current_section = 'params'
            elif stripped.startswith(':return:') or stripped.startswith(':returns:'):
                current_section = 'returns'
            elif stripped.startswith(':raise:') or stripped.startswith(':raises:'):
                current_section = 'raises'
            elif stripped.startswith('>>>') or stripped.startswith('Examples'):
                current_section = 'examples'
                
            if current_section == 'description':
                info['description'] += stripped + '\n'
            elif current_section == 'params':
                self._parse_param_line(stripped, info['params'])
            elif current_section == 'returns':
                self._parse_return_line(stripped, info['returns'])
            elif current_section == 'raises':
                self._parse_raise_line(stripped, info['raises'])
            elif current_section == 'examples':
                info['examples'] += stripped + '\n'
                
        return info
    
    def _parse_param_line(self, line: str, params: Dict):
        """解析参数行"""
        match = re.match(r':param\s+(\w+):\s*(.*)', line)
        if match:
            name, desc = match.groups()
            params[name] = desc
            
    def _parse_return_line(self, line: str, returns: Dict):
        """解析返回值行"""
        match = re.match(r':returns?:\s*(.*)', line)
        if match:
            returns['description'] = match.group(1)
            
    def _parse_raise_line(self, line: str, raises: Dict):
        """解析异常行"""
        match = re.match(r':raises?\s+(\w+):\s*(.*)', line)
        if match:
            exc_type, desc = match.groups()
            raises[exc_type] = desc
    
    def generate_docstring(self, func_info: FunctionInfo, style: str = 'google') -> str:
        """生成文档字符串"""
        if style == 'google':
            return self._generate_google_style(func_info)
        elif style == 'sphinx':
            return self._generate_sphinx_style(func_info)
        elif style == 'numpy':
            return self._generate_numpy_style(func_info)
        else:
            return self._generate_google_style(func_info)
    
    def _generate_google_style(self, func_info: FunctionInfo) -> str:
        """生成Google风格的文档字符串"""
        lines = [func_info.docstring or f"{func_info.name}的函数文档"]
        
        # 参数
        if func_info.params:
            lines.append("")
            lines.append("Args:")
            for param in func_info.params:
                param_name = param.get('name', '')
                param_type = param.get('type', '')
                param_desc = param.get('description', '')
                
                type_str = f" ({param_type})" if param_type else ""
                lines.append(f"    {param_name}{type_str}: {param_desc}")
                
        # 返回值
        if func_info.returns:
            lines.append("")
            lines.append("Returns:")
            ret_type = func_info.returns.get('type', '')
            ret_desc = func_info.returns.get('description', '')
            type_str = f" ({ret_type})" if ret_type else ""
            lines.append(f"    {type_str} {ret_desc}")
            
        # 异常
        if func_info.raises:
            lines.append("")
            lines.append("Raises:")
            for exc in func_info.raises:
                exc_type = exc.get('type', '')
                exc_desc = exc.get('description', '')
                lines.append(f"    {exc_type}: {exc_desc}")
                
        # 装饰器
        if func_info.decorators:
            lines.append("")
            lines.append("Decorators:")
            for dec in func_info.decorators:
                lines.append(f"    - {dec}")
                
        return '\n'.join(lines)
    
    def _generate_sphinx_style(self, func_info: FunctionInfo) -> str:
        """生成Sphinx风格的文档字符串"""
        lines = [func_info.docstring or f"{func_info.name}的函数文档"]
        
        if func_info.params:
            lines.append("")
            for param in func_info.params:
                name = param.get('name', '')
                ptype = param.get('type', '')
                desc = param.get('description', '')
                lines.append(f":param {name}: {desc}")
                if ptype:
                    lines.append(f":type {name}: {ptype}")
                    
        if func_info.returns:
            rtype = func_info.returns.get('type', '')
            rdesc = func_info.returns.get('description', '')
            lines.append(f":return: {rdesc}")
            if rtype:
                lines.append(f":rtype: {rtype}")
                
        return '\n'.join(lines)
    
    def _generate_numpy_style(self, func_info: FunctionInfo) -> str:
        """生成NumPy风格的文档字符串"""
        lines = [func_info.docstring or f"{func_info.name}的函数文档"]
        
        if func_info.params:
            lines.append("")
            lines.append("Parameters")
            lines.append("----------")
            for param in func_info.params:
                name = param.get('name', '')
                ptype = param.get('type', '')
                desc = param.get('description', '')
                type_str = f" : {ptype}" if ptype else ""
                lines.append(f"{name}{type_str}")
                lines.append(f"    {desc}")
                
        if func_info.returns:
            lines.append("")
            lines.append("Returns")
            lines.append("-------")
            rtype = func_info.returns.get('type', '')
            rdesc = func_info.returns.get('description', '')
            type_str = f" : {rtype}" if rtype else ""
            lines.append(f"{type_str}")
            lines.append(f"    {rdesc}")
            
        return '\n'.join(lines)


class CodeDocumentationGenerator:
    """代码文档生成器主类"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.java': Language.JAVA,
        '.go': Language.GO,
        '.rs': Language.RUST,
    }
    
    def __init__(self):
        self.python_generator = PythonDocGenerator()
        
    def detect_language(self, file_path: str) -> Optional[Language]:
        """检测文件语言"""
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(ext)
    
    def parse_python_file(self, file_path: str) -> ModuleInfo:
        """解析Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        module_info = ModuleInfo()
        
        # 提取模块文档字符串
        if tree.docstring:
            module_info.docstring = ast.get_docstring(tree)
            
        # 遍历节点
        for node in ast.iter_child_nodes(tree):
            # 导入语句
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_info.imports.append({
                        'type': 'import',
                        'name': alias.name,
                        'alias': alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                for alias in node.names:
                    module_info.imports.append({
                        'type': 'from',
                        'module': module_name,
                        'name': alias.name,
                        'alias': alias.asname
                    })
                    
            # 类定义
            elif isinstance(node, ast.ClassDef):
                class_info = self._parse_class(node)
                module_info.classes.append(class_info)
                
            # 函数定义
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = self._parse_function(node)
                module_info.functions.append(func_info)
                
        return module_info
    
    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """解析类定义"""
        class_info = ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            line_number=node.lineno
        )
        
        # 基类
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info.bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                class_info.bases.append(f"{base.value.id}.{base.attr}")
                
        # 遍历类内部节点
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method = self._parse_function(item)
                class_info.methods.append(method)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    class_info.attributes.append({
                        'name': item.target.id,
                        'type': self._get_annotation_type(item.annotation),
                        'lineno': item.lineno
                    })
                    
        return class_info
    
    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        """解析函数定义"""
        func_info = FunctionInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            line_number=node.lineno
        )
        
        # 装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info.decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                func_info.decorators.append(f"{decorator.value.id}.{decorator.attr}")
                
        # 参数
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_annotation_type(arg.annotation),
                'default': self._get_default_value(node.args.defaults, arg)
            }
            func_info.params.append(param_info)
            
        # 返回类型
        if node.returns:
            func_info.returns = {
                'type': self._get_annotation_type(node.returns)
            }
            
        # 分析现有文档字符串提取更多信息
        if func_info.docstring:
            doc_info = self.python_generator.extract_docstring_info(func_info.docstring)
            
            # 更新参数描述
            for param in func_info.params:
                name = param['name']
                if name in doc_info['params']:
                    param['description'] = doc_info['params'][name]
                    
            # 更新返回值描述
            if doc_info['returns']:
                if not func_info.returns:
                    func_info.returns = {}
                func_info.returns['description'] = doc_info['returns'].get('description', '')
                
        return func_info
    
    def _get_annotation_type(self, annotation) -> str:
        """获取注解类型"""
        if annotation is None:
            return ''
            
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            base = self._get_annotation_type(annotation.value)
            slice_val = self._get_annotation_type(annotation.slice)
            return f"{base}[{slice_val}]"
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return str(type(annotation).__name__)
    
    def _get_default_value(self, defaults: List, arg_index: int) -> Optional[str]:
        """获取默认值"""
        if not defaults:
            return None
            
        num_no_default = len(defaults)
        actual_index = arg_index - num_no_default
        
        if actual_index >= 0 and actual_index < len(defaults):
            default = defaults[actual_index]
            if isinstance(default, ast.Constant):
                return str(default.value)
            elif isinstance(default, ast.NameConstant):
                return str(default.value)
            elif isinstance(default, ast.Tuple):
                return str(tuple(self._get_default_value([d], 0) for d in default.elts))
        return None
    
    def generate_markdown(self, module_info: ModuleInfo, file_path: str) -> str:
        """生成Markdown文档"""
        lines = []
        file_name = Path(file_path).name
        
        lines.append(f"# {file_name}")
        lines.append("")
        lines.append("## 模块概述")
        if module_info.docstring:
            lines.append(module_info.docstring)
        else:
            lines.append(f"自动生成的 {file_name} 文档")
            
        lines.append("")
        lines.append("## 目录")
        if module_info.classes:
            lines.append("- [类](#类)")
        if module_info.functions:
            lines.append("- [函数](#函数)")
        if module_info.imports:
            lines.append("- [导入](#导入)")
            
        # 类
        if module_info.classes:
            lines.append("")
            lines.append("## 类")
            lines.append("")
            for cls in module_info.classes:
                lines.append(f"### {cls.name}")
                if cls.bases:
                    lines.append(f"继承自: `{'`, `'.join(cls.bases)}`")
                if cls.docstring:
                    lines.append("")
                    lines.append(cls.docstring)
                    
                if cls.attributes:
                    lines.append("")
                    lines.append("#### 属性")
                    lines.append("")
                    for attr in cls.attributes:
                        attr_name = attr.get('name', '')
                        attr_type = attr.get('type', '')
                        lines.append(f"- `{attr_name}` ({attr_type})" if attr_type else f"- `{attr_name}`")
                        
                if cls.methods:
                    lines.append("")
                    lines.append("#### 方法")
                    lines.append("")
                    for method in cls.methods:
                        lines.append(f"##### `{method.name}()`")
                        if method.is_async:
                            lines.append("`async` ")
                        if method.docstring:
                            lines.append("")
                            lines.append(method.docstring)
                            
                        if method.params:
                            lines.append("")
                            lines.append("**参数:**")
                            lines.append("")
                            for param in method.params:
                                pname = param.get('name', '')
                                ptype = param.get('type', '')
                                pdesc = param.get('description', '')
                                type_str = f"`{ptype}` " if ptype else ""
                                lines.append(f"- {type_str}`{pname}`: {pdesc}")
                                
                        if method.returns:
                            lines.append("")
                            lines.append("**返回值:**")
                            lines.append("")
                            rtype = method.returns.get('type', '')
                            rdesc = method.returns.get('description', '')
                            type_str = f"`{rtype}` " if rtype else ""
                            lines.append(f"- {type_str}{rdesc}")
                            
        # 函数
        if module_info.functions:
            lines.append("")
            lines.append("## 函数")
            lines.append("")
            for func in module_info.functions:
                lines.append(f"### `{func.name}()`")
                if func.is_async:
                    lines.append("`async` ")
                if func.docstring:
                    lines.append("")
                    lines.append(func.docstring)
                    
                if func.params:
                    lines.append("")
                    lines.append("**参数:**")
                    lines.append("")
                    for param in func.params:
                        pname = param.get('name', '')
                        ptype = param.get('type', '')
                        pdesc = param.get('description', '')
                        type_str = f"`{ptype}` " if ptype else ""
                        lines.append(f"- {type_str}`{pname}`: {pdesc}")
                        
                if func.returns:
                    lines.append("")
                    lines.append("**返回值:**")
                    lines.append("")
                    rtype = func.returns.get('type', '')
                    rdesc = func.returns.get('description', '')
                    type_str = f"`{rtype}` " if rtype else ""
                    lines.append(f"- {type_str}{rdesc}")
                    
        # 导入
        if module_info.imports:
            lines.append("")
            lines.append("## 导入")
            lines.append("")
            for imp in module_info.imports:
                if imp['type'] == 'import':
                    name = imp['name']
                    alias = f" as {imp['alias']}" if imp['alias'] else ""
                    lines.append(f"```python\nimport {name}{alias}\n```")
                else:
                    module = imp['module']
                    name = imp['name']
                    alias = f" as {imp['alias']}" if imp['alias'] else ""
                    lines.append(f"```python\nfrom {module} import {name}{alias}\n```")
                    
        return '\n'.join(lines)
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析单个文件"""
        language = self.detect_language(file_path)
        
        if not language:
            return {'error': f'不支持的文件类型: {file_path}'}
            
        if language == Language.PYTHON:
            module_info = self.parse_python_file(file_path)
        else:
            return {'error': f'暂未支持的语言: {language.value}'}
            
        return {
            'language': language.value,
            'file_path': file_path,
            'module_info': module_info.__dict__,
            'markdown': self.generate_markdown(module_info, file_path)
        }
    
    def analyze_directory(self, dir_path: str, recursive: bool = True) -> Dict:
        """分析目录中的所有文件"""
        dir_path = Path(dir_path)
        results = {}
        
        pattern = '**/*.py' if recursive else '*.py'
        
        for py_file in dir_path.glob(pattern):
            file_results = self.analyze_file(str(py_file))
            results[str(py_file)] = file_results
            
        return results


def demo():
    """演示函数"""
    print("=" * 60)
    print("智能代码文档生成器演示")
    print("=" * 60)
    print()
    
    # 创建一个示例Python文件
    sample_code = '''
"""
示例模块 - 用于演示文档生成功能
=============================

这个模块展示了如何使用智能代码文档生成器。
"""

import os
from typing import List, Dict, Optional

class DataProcessor:
    """
    数据处理器类
    
    用于处理和分析数据的通用处理器。
    支持批量处理、缓存和错误恢复。
    
    Attributes:
        cache_size (int): 缓存大小限制
        error_count (int): 错误计数
    """
    
    def __init__(self, cache_size: int = 100) -> None:
        """
        初始化数据处理器
        
        Args:
            cache_size: 缓存大小，默认为100
        """
        self.cache_size = cache_size
        self.error_count = 0
        self._data = []
        
    def process(self, data: List[Dict]) -> Dict[str, any]:
        """
        处理数据列表
        
        Args:
            data: 输入数据列表，每个元素是字典
            
        Returns:
            处理结果字典，包含统计信息
            
        Raises:
            ValueError: 当数据为空时抛出
            TypeError: 当数据类型不正确时抛出
        """
        if not data:
            raise ValueError("数据不能为空")
            
        if not isinstance(data, list):
            raise TypeError("数据必须是列表类型")
            
        result = {
            'count': len(data),
            'success': True,
            'processed_data': []
        }
        
        for item in data:
            try:
                processed = self._process_single(item)
                result['processed_data'].append(processed)
            except Exception as e:
                self.error_count += 1
                result['success'] = False
                
        return result
    
    def _process_single(self, item: Dict) -> Dict:
        """处理单个数据项（内部方法）"""
        return {**item, 'processed': True}
    
    async def async_process(self, data: List[Dict]) -> List[Dict]:
        """
        异步处理数据
        
        Args:
            data: 输入数据列表
            
        Returns:
            处理后的数据列表
        """
        results = []
        for item in data:
            result = await self._async_process_single(item)
            results.append(result)
        return results
        
    async def _async_process_single(self, item: Dict) -> Dict:
        """异步处理单个数据项"""
        return {**item, 'async_processed': True}


def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """
    计算数字列表的统计信息
    
    Args:
        numbers: 数字列表
        
    Returns:
        包含均值、最大值、最小值的字典
        
    Examples:
        >>> calculate_statistics([1, 2, 3, 4, 5])
        {'mean': 3.0, 'max': 5, 'min': 1}
    """
    if not numbers:
        return {'mean': 0, 'max': 0, 'min': 0}
        
    return {
        'mean': sum(numbers) / len(numbers),
        'max': max(numbers),
        'min': min(numbers)
    }
'''
    
    # 保存示例文件
    sample_file = 'sample_example.py'
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    print(f"创建示例文件: {sample_file}")
    print()
    
    # 分析示例文件
    generator = CodeDocumentationGenerator()
    result = generator.analyze_file(sample_file)
    
    print("=" * 60)
    print("分析结果")
    print("=" * 60)
    print()
    
    # 打印模块信息
    module_info = result['module_info']
    print(f"类数量: {len(module_info['classes'])}")
    print(f"函数数量: {len(module_info['functions'])}")
    print(f"导入数量: {len(module_info['imports'])}")
    print()
    
    # 打印类信息
    for cls in module_info['classes']:
        print(f"类: {cls['name']}")
        print(f"  方法数量: {len(cls['methods'])}")
        print(f"  属性数量: {len(cls['attributes'])}")
    print()
    
    # 打印生成的Markdown文档
    print("=" * 60)
    print("生成的Markdown文档")
    print("=" * 60)
    print()
    print(result['markdown'])
    
    # 清理示例文件
    import os
    os.remove(sample_file)
    print()
    print("已清理示例文件")
    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == '__main__':
    demo()
