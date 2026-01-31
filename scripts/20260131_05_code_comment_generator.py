#!/usr/bin/env python3
"""
AI Code Comment Generator
自动为代码生成专业注释
"""

import re
import hashlib

class CodeCommentGenerator:
    """代码注释生成器"""
    
    TEMPLATES = {
        'function': '''def {name}({params}):
    """{description}
    
    Args:
        {args_doc}
    
    Returns:
        {returns_doc}
    """,
        'class': '''class {name}:
    """{description}
    
    Attributes:
        {attrs_doc}
    """,
        'complex_logic': '# TODO: 需要优化这段逻辑 - {hint}',
    }
    
    KEYWORDS = {
        'api': 'API接口调用',
        'database': '数据库操作',
        'cache': '缓存处理',
        'auth': '认证授权',
        'error': '异常处理',
        'loop': '循环处理',
        'parse': '解析数据',
        'transform': '数据转换',
        'validate': '数据校验',
        'serialize': '序列化操作',
    }
    
    @staticmethod
    def generate_docstring(name: str, params: list, description: str = "") -> str:
        """生成函数文档字符串"""
        if not description:
            description = f"{name}函数执行核心逻辑"
        
        args_doc = "\n        ".join(f"{p}: 参数说明" for p in params) if params else "无"
        returns_doc = "返回值说明"
        
        return CodeCommentGenerator.TEMPLATES['function'].format(
            name=name,
            params=", ".join(params),
            description=description,
            args_doc=args_doc,
            returns_doc=returns_doc
        )
    
    @staticmethod
    def analyze_code_type(code: str) -> str:
        """分析代码类型"""
        if 'class ' in code:
            return 'class'
        elif 'def ' in code or 'func ' in code:
            return 'function'
        elif any(kw in code.lower() for kw in ['if ', 'for ', 'while ']):
            return 'logic'
        else:
            return 'general'
    
    @staticmethod
    def extract_functions(code: str) -> list:
        """提取函数列表"""
        pattern = r'(?:def|func)\s+(\w+)\s*\(([^)]*)\)'
        matches = re.findall(pattern, code)
        return [{'name': m[0], 'params': m[1].split(',') if m[1] else []} for m in matches]
    
    @staticmethod
    def generate_header_comment(filename: str) -> str:
        """生成文件头部注释"""
        date = "2026-01-31"
        checksum = hashlib.md5(filename.encode()).hexdigest()[:8]
        
        return f'''#!/usr/bin/env python3
"""
{filename}

创建日期: {date}
文件标识: {checksum}

功能描述:
    {CodeCommentGenerator._get_file_description(filename)}
""".format(
    filename=filename,
    checksum=checksum,
    description="这是一个自动生成的代码文件"
)
    
    @staticmethod
    def _get_file_description(filename: str) -> str:
        """根据文件名生成描述"""
        name_lower = filename.lower()
        if 'comment' in name_lower:
            return "代码注释生成与处理"
        elif 'tool' in name_lower or 'util' in name_lower:
            return "实用工具脚本"
        elif 'algorithm' in name_lower:
            return "算法实现与优化"
        else:
            return "自动化代码生成"


def main():
    """主函数 - 演示注释生成"""
    print("AI Code Comment Generator v1.0")
    print("=" * 40)
    
    # 演示函数注释生成
    demo_code = '''
def calculate_fibonacci(n):
    # 递归计算斐波那契数列
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
'''
    
    functions = CodeCommentGenerator.extract_functions(demo_code)
    for func in functions:
        docstring = CodeCommentGenerator.generate_docstring(
            func['name'], 
            func['params'],
            "计算斐波那契数列的第n项"
        )
        print(f"\n{func['name']} 的注释:")
        print(docstring)


if __name__ == "__main__":
    main()
