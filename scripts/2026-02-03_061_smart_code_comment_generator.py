#!/usr/bin/env python3
"""
智能代码注释生成器 - Day 61
自动为代码生成智能注释，包括函数说明、参数说明、返回值说明等
"""

import ast
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    docstring: str
    args: list
    returns: Optional[str]
    line_number: int


class SmartCodeCommentGenerator:
    """智能代码注释生成器"""
    
    def __init__(self):
        self.comment_styles = {
            "google": self._google_style,
            "numpy": self._numpy_style,
            "sphinx": self._sphinx_style,
            "simple": self._simple_style,
        }
    
    def analyze_code(self, code: str) -> list[FunctionInfo]:
        """分析代码，提取函数信息"""
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    info = self._extract_function_info(node)
                    if info:
                        functions.append(info)
            
            return functions
        except SyntaxError as e:
            print(f"语法错误: {e}")
            return []
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Optional[FunctionInfo]:
        """提取单个函数信息"""
        # 获取参数信息
        args = []
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "type": self._get_type_hint(arg),
                "default": self._get_default_value(node.args.defaults, arg),
            }
            args.append(arg_info)
        
        # 获取返回值信息
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)
        
        # 获取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        return FunctionInfo(
            name=node.name,
            docstring=docstring,
            args=args,
            returns=returns,
            line_number=node.lineno,
        )
    
    def _get_type_hint(self, arg: ast.arg) -> str:
        """获取参数类型提示"""
        return "Any"
    
    def _get_default_value(self, defaults: list, arg: ast.arg) -> Optional[str]:
        """获取参数默认值"""
        return None
    
    def generate_comment(self, func_info: FunctionInfo, style: str = "google") -> str:
        """生成注释"""
        style_func = self.comment_styles.get(style, self._google_style)
        return style_func(func_info)
    
    def _google_style(self, func_info: FunctionInfo) -> str:
        """Google风格注释"""
        lines = [f'    """{func_info.docstring}"""' if func_info.docstring else '    """']
        
        for arg in func_info.args:
            arg_desc = arg.get("description", "")
            lines.insert(1, f"    Args:")
            lines.append(f"        {arg['name']} ({arg.get('type', 'Any')}): {arg_desc}")
        
        if func_info.returns:
            lines.append(f"    Returns:")
            lines.append(f"        {func_info.returns}: 函数执行结果")
        
        return "\n".join(lines)
    
    def _numpy_style(self, func_info: FunctionInfo) -> str:
        """NumPy风格注释"""
        lines = ['"""']
        if func_info.docstring:
            lines.append(func_info.docstring)
        
        lines.append("")
        for arg in func_info.args:
            lines.append(f"{arg['name']} : {arg.get('type', 'Any')}")
            lines.append(f"    {arg.get('description', '')}")
        
        if func_info.returns:
            lines.append(f"Returns")
            lines.append(f"    {func_info.returns}")
        
        lines.append('"""')
        return "\n".join(lines)
    
    def _sphinx_style(self, func_info: FunctionInfo) -> str:
        """Sphinx风格注释"""
        lines = ['"""']
        if func_info.docstring:
            lines.append(func_info.docstring)
        
        for arg in func_info.args:
            lines.append(f":param {arg['name']}: {arg.get('description', '')}")
            lines.append(f":type {arg['name']}: {arg.get('type', 'Any')}")
        
        if func_info.returns:
            lines.append(f":return: 函数执行结果")
            lines.append(f":rtype: {func_info.returns}")
        
        lines.append('"""')
        return "\n".join(lines)
    
    def _simple_style(self, func_info: FunctionInfo) -> str:
        """简单风格注释"""
        desc = func_info.docstring or "函数功能说明"
        lines = [f'    """{desc}"""']
        
        if func_info.args:
            lines.append(f"    # 参数: {', '.join(a['name'] for a in func_info.args)}")
        if func_info.returns:
            lines.append(f"    # 返回值: {func_info.returns}")
        
        return "\n".join(lines)
    
    def add_comments_to_code(self, code: str, style: str = "google") -> str:
        """为代码添加注释"""
        functions = self.analyze_code(code)
        
        if not functions:
            return code
        
        result_lines = code.split('\n')
        
        for func in reversed(functions):
            comment = self.generate_comment(func, style)
            comment_lines = comment.split('\n')
            
            insert_pos = func.line_number - 1
            indented_comment = []
            for line in comment_lines:
                if line.strip():
                    indented_comment.append(line)
            
            if indented_comment:
                result_lines.insert(insert_pos, '\n'.join(indented_comment))
        
        return '\n'.join(result_lines)


def demo():
    """演示"""
    generator = SmartCodeCommentGenerator()
    
    # 示例代码
    sample_code = '''
def calculate_statistics(data):
    """计算数据集的统计信息"""
    total = sum(data)
    average = total / len(data)
    return {"total": total, "average": average}

def process_user_data(user_id, include_details=True):
    """处理用户数据"""
    pass
'''
    
    print("=" * 50)
    print("智能代码注释生成器 - 演示")
    print("=" * 50)
    
    # 分析代码
    functions = generator.analyze_code(sample_code)
    print(f"\n发现 {len(functions)} 个函数:\n")
    
    for func in functions:
        print(f"函数: {func.name}")
        print(f"  参数: {[a['name'] for a in func.args]}")
        print(f"  返回: {func.returns}")
        print()
    
    # 生成注释
    print("Google风格注释:")
    print("-" * 30)
    for func in functions:
        print(generator.generate_comment(func, "google"))
        print()


if __name__ == "__main__":
    demo()
