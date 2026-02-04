#!/usr/bin/env python3
"""
Unit Test Generator - 自动生成单元测试工具
Day 81: Code Snippet Test Generator

功能:
- 自动分析Python/JavaScript文件
- 生成pytest风格的单元测试
- 支持函数签名提取和参数推断
- 多种断言策略
"""

import ast
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class FunctionExtractor(ast.NodeVisitor):
    """AST访问器: 提取函数信息"""
    
    def __init__(self):
        self.functions: List[Dict] = []
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_info = {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'defaults': [self._get_default_value(d) for d in node.args.defaults],
            'docstring': ast.get_docstring(node),
            'returns': self._get_type_annotation(node.returns),
            'line': node.lineno,
            'class': self.current_class
        }
        self.functions.append(func_info)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def _get_default_value(self, node: ast.AST) -> Any:
        """获取默认值"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return f"/* computed */"
        return None
    
    def _get_type_annotation(self, node: ast.AST) -> str:
        """获取类型注解"""
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return ast.unparse(node)
        return ast.unparse(node)


class JavaScriptFunctionExtractor:
    """JavaScript函数提取器(正则+简单解析)"""
    
    # 匹配函数声明的正则
    PATTERNS = {
        'function': r'function\s+(\w+)\s*\(([^)]*)\)',
        'arrow': r'(\w+)\s*=\s*\(([^)]*)\)\s*=>',
        'const_arrow': r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
        'class_method': r'(\w+)\s*\(([^)]*)\)\s*\{',
        'async_function': r'async\s+function\s+(\w+)\s*\(([^)]*)\)',
    }
    
    @classmethod
    def extract_functions(cls, content: str) -> List[Dict]:
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 函数声明
            match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                functions.append({
                    'name': match.group(1),
                    'args': cls._parse_args(match.group(2)),
                    'line': i + 1
                })
            
            # async函数
            match = re.search(r'async\s+function\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                functions.append({
                    'name': match.group(1),
                    'args': cls._parse_args(match.group(2)),
                    'line': i + 1,
                    'async': True
                })
        
        return functions
    
    @classmethod
    def _parse_args(cls, args_str: str) -> List[str]:
        """解析参数列表"""
        if not args_str.strip():
            return []
        return [arg.strip() for arg in args_str.split(',')]


class UnitTestGenerator:
    """单元测试生成器"""
    
    def __init__(self, language: str = 'python'):
        self.language = language
        self.test_cases = []
    
    def generate_test(self, func_info: Dict, module_name: str = "test_module") -> str:
        """为单个函数生成测试代码"""
        if self.language == 'python':
            return self._generate_python_test(func_info, module_name)
        else:
            return self._generate_js_test(func_info, module_name)
    
    def _generate_python_test(self, func_info: Dict, module_name: str) -> str:
        """生成Python测试代码"""
        func_name = func_info['name']
        args = func_info['args']
        defaults = func_info['defaults']
        
        # 生成参数
        test_args = self._generate_test_args(args, defaults)
        
        # 生成测试用例
        test_code = f'''import pytest
from {module_name} import {func_name}


class Test{func_name.capitalize()}:
    """Test class for {func_name}"""
    
    def test_basic(self):
        """Basic functionality test"""
'''
        # 添加参数
        if args:
            test_code += f'        result = {func_name}({", ".join(test_args)})\n'
            test_code += '        assert result is not None\n'
        else:
            test_code += f'        result = {func_name}()\n'
            test_code += '        assert result is not None\n'
        
        test_code += '''
    def test_edge_cases(self):
        """Edge cases test"""
'''
        # 添加边界测试
        for i, arg in enumerate(args[:2]):  # 只测试前2个参数
            test_code += f'        # Test {arg} edge cases\n'
            test_code += f'        {arg}_values = [None, 0, 1, -1, "", [], {{}}]\n'
            test_code += f'        for val in {arg}_values:\n'
            test_code += f'            try:\n'
            test_code += f'                result = {func_name}({self._replace_arg(test_args, i, "val")})\n'
            test_code += f'                # Test passed for value: {{val}}\n'
            test_code += f'            except (TypeError, ValueError):\n'
            test_code += f'                # Expected for invalid input\n'
            test_code += f'                pass\n'
        
        test_code += '''
    def test_return_type(self):
        """Return type validation test"""
'''
        if args:
            test_code += f'        result = {func_name}({", ".join(test_args)})\n'
        else:
            test_code += f'        result = {func_name}()\n'
        
        test_code += '''        # Add type-specific assertions here
        assert isinstance(result, (dict, list, str, int, float, bool, type(None)))
    
    def test_with_mock_data(self):
        """Test with realistic mock data"""
        mock_data = self._get_mock_data()
'''
        if args:
            test_code += f'        result = {func_name}({", ".join(test_args)})\n'
            test_code += '        assert result is not None\n'
        else:
            test_code += f'        result = {func_name}()\n'
            test_code += '        assert result is not None\n'
        
        test_code += '''    
    @staticmethod
    def _get_mock_data():
        """Generate mock test data"""
        return {
            "string": "test_string",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
'''
        return test_code
    
    def _generate_js_test(self, func_info: Dict, module_name: str) -> str:
        """生成JavaScript测试代码"""
        func_name = func_info['name']
        args = func_info['args']
        is_async = func_info.get('async', False)
        
        test_code = f'''// Unit tests for {func_name}
const {func_name} = require('./{module_name}');

describe('{func_name}', () => {{
    test('basic functionality', () => {{
'''
        if args:
            test_code += f'        const result = {func_name}({", ".join(args)});\n'
        else:
            test_code += f'        const result = {func_name}();\n'
        
        if is_async:
            test_code += '''        await expect(result).resolves.not.toBeUndefined();
'''
        else:
            test_code += '''        expect(result).toBeDefined();
'''
        
        test_code += '''    });

    test('edge cases', () => {
'''
        for i, arg in enumerate(args[:2]):
            test_code += f'        // Test {arg} edge cases\n'
            test_code += f'        const {arg}Values = [null, 0, 1, -1, "", [], {{}}];\n'
            test_code += f'        {arg}Values.forEach(val => {{\n'
            test_code += f'            expect(() => {func_name}({self._replace_js_arg(args, i, "val")}).not.toThrow();\n'
            test_code += f'        }});\n'
        
        test_code += '''    });

    test('return type validation', () => {
'''
        if args:
            test_code += f'        const result = {func_name}({", ".join(args)});\n'
        else:
            test_code += f'        const result = {func_name}();\n'
        
        test_code += '''        expect(typeof result).toBe('object');
    });
});
'''
        return test_code
    
    def _generate_test_args(self, args: List[str], defaults: List) -> List[str]:
        """生成测试参数值"""
        result = []
        default_idx = len(defaults) - len(args)
        
        for i, arg in enumerate(args):
            if i >= default_idx and defaults[i - default_idx]:
                result.append(f"_test_{arg}_{i}")
            elif arg in ['str', 'string']:
                result.append(f'"test_{arg}"')
            elif arg in ['num', 'number', 'int', 'float']:
                result.append(f"42")
            elif arg in ['lst', 'list', 'arr', 'array']:
                result.append(f"[1, 2, 3]")
            elif arg in ['dict', 'obj', 'dictionary']:
                result.append(f'{{"key": "value"}}')
            elif arg in ['bool', 'flag']:
                result.append("True" if self.language == 'python' else "true")
            elif arg == 'data':
                result.append("mock_data" if self.language == 'python' else "mockData")
            elif arg == 'callback':
                result.append("lambda x: x" if self.language == 'python' else "x => x")
            elif arg == 'func':
                result.append("lambda x: x" if self.language == 'python' else "x => x")
            else:
                result.append(f'"test_{arg}"' if self.language == 'python' else f'"test_{arg}"')
        
        return result
    
    def _replace_arg(self, args: List[str], idx: int, new_val: str) -> str:
        """替换参数值"""
        return [new_val if i == idx else arg for i, arg in enumerate(args)]
    
    def _replace_js_arg(self, args: List[str], idx: int, new_val: str) -> str:
        """JS版本替换参数"""
        return [new_val if i == idx else arg for i, arg in enumerate(args)]


class TestGeneratorCLI:
    """测试生成器命令行工具"""
    
    def __init__(self):
        self.generators = {
            'python': UnitTestGenerator('python'),
            'js': UnitTestGenerator('javascript'),
            'javascript': UnitTestGenerator('javascript')
        }
    
    def run(self, args=None):
        """运行CLI"""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        if parsed_args.file:
            self.generate_from_file(
                parsed_args.file,
                parsed_args.output or "tests/",
                parsed_args.language or self._detect_language(parsed_args.file)
            )
        else:
            parser.print_help()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description="Unit Test Generator - 自动生成单元测试",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s file.py                    # 从Python文件生成测试
  %(prog)s file.js --output tests/    # 指定输出目录
  %(prog)s file.py --lang js          # 指定JavaScript语言
  %(prog)s -b                         # 生成基础测试模板
            """
        )
        parser.add_argument('file', nargs='?', help='源文件路径')
        parser.add_argument('-o', '--output', help='输出目录')
        parser.add_argument('-l', '--lang', choices=['python', 'js', 'javascript'],
                          help='编程语言')
        parser.add_argument('-b', '--basic', action='store_true',
                          help='生成基础测试模板')
        return parser
    
    def _detect_language(self, file_path: str) -> str:
        """检测语言"""
        ext = Path(file_path).suffix.lower()
        if ext == '.py':
            return 'python'
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            return 'javascript'
        return 'python'
    
    def generate_from_file(self, file_path: str, output_dir: str = "tests/",
                          language: str = 'python'):
        """从文件生成测试"""
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if language == 'python':
            tree = ast.parse(content)
            extractor = FunctionExtractor()
            extractor.visit(tree)
            functions = extractor.functions
        else:
            functions = JavaScriptFunctionExtractor.extract_functions(content)
        
        if not functions:
            print(f"警告: 未在 {file_path} 中找到函数")
            return
        
        print(f"找到 {len(functions)} 个函数")
        
        # 生成测试文件
        os.makedirs(output_dir, exist_ok=True)
        module_name = Path(file_path).stem
        
        for func in functions:
            generator = self.generators.get(language, self.generators['python'])
            test_code = generator.generate_test(func, module_name)
            
            test_file = os.path.join(output_dir, f"test_{func['name']}.py")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)
            print(f"生成测试: {test_file}")
        
        print(f"完成! 共生成 {len(functions)} 个测试文件")


def main():
    """主函数"""
    cli = TestGeneratorCLI()
    cli.run()


if __name__ == "__main__":
    main()
