#!/usr/bin/env python3
"""
智能代码文档生成器 - Day 021
根据代码自动生成文档

功能:
1. 分析Python代码结构
2. 提取函数、类、参数信息
3. 生成Markdown格式文档
"""

import ast
import re
from typing import Dict, List, Any
from datetime import datetime


class CodeDocGenerator:
    """代码文档生成器类"""
    
    def __init__(self):
        self.imports = []
        self.classes = []
        self.functions = []
        self.standalone_functions = []
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析Python文件并提取信息"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            self._extract_info(tree)
            return self._generate_doc()
        except SyntaxError as e:
            return {"error": f"语法错误: {e}"}
    
    def _extract_info(self, tree: ast.AST):
        """从AST中提取信息"""
        self.imports = []
        self.classes = []
        self.functions = []
        self.standalone_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                self.imports.append(f"from {node.module} import ...")
            elif isinstance(node, ast.ClassDef):
                self.classes.append(self._extract_class_info(node))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                self.standalone_functions.append(self._extract_function_info(node))
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """提取类信息"""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function_info(item))
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": methods,
            "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }
    
    def _extract_function_info(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
        """提取函数信息"""
        args = []
        for arg in node.args.args:
            default = ""
            if arg.default:
                default = f"= {ast.literal_eval(ast.dump(arg.default))}"
            args.append({
                "name": arg.arg,
                "type": arg.annotation.id if arg.annotation and isinstance(arg.annotation, ast.Name) else "Any",
                "default": default
            })
        
        returns = "Any"
        if node.returns:
            if isinstance(node.returns, ast.Name):
                returns = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                returns = str(node.returns.value)
        
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "args": args,
            "returns": returns,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _generate_doc(self) -> Dict[str, Any]:
        """生成文档"""
        return {
            "imports": list(set(self.imports)),
            "classes": self.classes,
            "standalone_functions": self.standalone_functions,
            "generated_at": datetime.now().isoformat()
        }
    
    def to_markdown(self, doc_info: Dict[str, Any], title: str = "API Documentation") -> str:
        """生成Markdown格式文档"""
        if "error" in doc_info:
            return f"# Error\n\n{doc_info['error']}"
        
        md = f"# {title}\n\n"
        md += f"*生成时间: {doc_info['generated_at']}*\n\n"
        
        # Imports
        if doc_info['imports']:
            md += "## 导入模块\n\n"
            md += "```python\n"
            for imp in doc_info['imports']:
                md += f"import {imp}\n"
            md += "```\n\n"
        
        # Classes
        for cls in doc_info['classes']:
            md += f"## 类: {cls['name']}\n\n"
            if cls['docstring']:
                md += f"{cls['docstring']}\n\n"
            if cls['bases']:
                md += f"*继承自: {', '.join(cls['bases'])}*\n\n"
            
            if cls['methods']:
                md += "### 方法\n\n"
                for method in cls['methods']:
                    md += self._function_to_markdown(method, "#### ")
        
        # Standalone Functions
        if doc_info['standalone_functions']:
            md += "## 函数\n\n"
            for func in doc_info['standalone_functions']:
                md += self._function_to_markdown(func, "### ")
        
        return md
    
    def _function_to_markdown(self, func: Dict[str, Any], header: str = "### ") -> str:
        """将函数信息转为Markdown"""
        md = f"{header} `{func['name']}`\n\n"
        
        if func['docstring']:
            md += f"{func['docstring']}\n\n"
        
        # Parameters
        if func['args']:
            md += "**参数:**\n\n"
            md += "| 名称 | 类型 | 默认值 |\n"
            md += "|------|------|--------|\n"
            for arg in func['args']:
                md += f"| `{arg['name']}` | `{arg['type']}` | `{arg['default']}` |\n"
            md += "\n"
        
        # Returns
        md += f"**返回:** `{func['returns']}`\n\n"
        
        if func['is_async']:
            md += "*这是一个异步函数*\n\n"
        
        return md


def main():
    """主函数 - 生成示例文档"""
    # 示例代码
    example_code = '''
class Calculator:
    """简单的计算器类"""
    
    def add(self, a: int, b: int) -> int:
        """加法运算
        
        Args:
            a: 第一个加数
            b: 第二个加数
        
        Returns:
            两数之和
        """
        return a + b
    
    async def multiply(self, a: float, b: float) -> float:
        """乘法运算（异步）
        
        Args:
            a: 第一个乘数
            b: 第二个乘数
        
        Returns:
            两数之积
        """
        return a * b

def gcd(a: int, b: int) -> int:
    """计算最大公约数
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        最大公约数
    """
    while b:
        a, b = b, a % b
    return a
'''
    
    # 临时写入示例代码
    with open('/tmp/example.py', 'w') as f:
        f.write(example_code)
    
    # 生成文档
    generator = CodeDocGenerator()
    doc_info = generator.parse_file('/tmp/example.py')
    md_content = generator.to_markdown(doc_info, "计算器 API 文档")
    
    print(md_content)
    
    # 保存文档
    with open('/tmp/example_doc.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("\n文档已保存到 /tmp/example_doc.md")


if __name__ == "__main__":
    main()
