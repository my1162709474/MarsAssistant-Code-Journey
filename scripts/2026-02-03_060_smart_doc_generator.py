#!/usr/bin/env python3
"""
🗂️ 智能代码文档生成器
AI驱动的代码文档自动生成工具

功能：
- 自动分析代码结构生成文档
- 支持多种编程语言
- 生成API文档、README、函数注释
- 智能提取代码意图和功能描述
"""

import ast
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class CodeDocumentGenerator:
    """智能代码文档生成器"""
    
    # 语言关键词映射
    LANGUAGE_PATTERNS = {
        'python': ['def ', 'class ', 'import ', 'from ', '=', '#'],
        'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'import ', 'export'],
        'java': ['public ', 'private ', 'protected ', 'class ', 'void ', 'import '],
        'go': ['func ', 'type ', 'import ', 'const ', 'var '],
        'rust': ['fn ', 'struct ', 'impl ', 'pub ', 'let '],
    }
    
    # 代码意图关键词
    INTENT_KEYWORDS = {
        'data_processing': ['parse', 'transform', 'convert', 'filter', 'map', 'reduce'],
        'file_io': ['read', 'write', 'open', 'save', 'load', 'export', 'import'],
        'api': ['request', 'response', 'endpoint', 'api', 'http', 'fetch', 'client'],
        'database': ['query', 'insert', 'update', 'delete', 'connect', 'transaction'],
        'testing': ['test', 'assert', 'mock', 'verify', 'validate', 'check'],
        'utils': ['util', 'helper', 'tool', 'common', 'shared', 'base'],
        'algorithm': ['sort', 'search', 'find', 'calculate', 'compute', 'optimize'],
        'ui': ['render', 'display', 'show', 'view', 'component', 'widget'],
    }
    
    def __init__(self):
        self.stats = {'files_processed': 0, 'docs_generated': 0, 'entities_found': 0}
    
    def detect_language(self, code: str) -> str:
        """检测编程语言"""
        scores = {}
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in code)
            if score > 0:
                scores[lang] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'python'  # 默认Python
    
    def extract_python_entities(self, code: str) -> List[Dict[str, Any]]:
        """提取Python代码实体（类、函数、导入等）"""
        entities = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # 提取类
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or ""
                entities.append({
                    'type': 'class',
                    'name': node.name,
                    'line': node.lineno,
                    'docstring': docstring,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                })
            
            # 提取函数
            elif isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or ""
                args = [arg.arg for arg in node.args.args]
                entities.append({
                    'type': 'function',
                    'name': node.name,
                    'line': node.lineno,
                    'docstring': docstring,
                    'args': args,
                    'returns': self._get_return_type(node)
                })
        
        self.stats['entities_found'] += len(entities)
        return entities
    
    def _get_return_type(self, node) -> str:
        """获取函数返回类型"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return 'Any'
    
    def extract_code_intent(self, code: str) -> List[str]:
        """提取代码意图"""
        code_lower = code.lower()
        intents = []
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in code_lower for kw in keywords):
                intents.append(intent)
        
        return intents if intents else ['general']
    
    def generate_docstring(self, entity: Dict[str, Any]) -> str:
        """为实体生成文档字符串"""
        lines = []
        
        if entity['type'] == 'class':
            lines.append(f"## {entity['name']}")
            if entity.get('docstring'):
                lines.append(f"\n{entity['docstring']}")
            if entity.get('bases'):
                lines.append(f"\n**继承自**: {', '.join(entity['bases'])}")
            if entity.get('methods'):
                lines.append(f"\n**方法**:\n- " + "\n- ".join(entity['methods']))
        
        elif entity['type'] == 'function':
            lines.append(f"### `{entity['name']}()`")
            if entity.get('docstring'):
                lines.append(f"\n{entity['docstring']}")
            if entity.get('args'):
                lines.append(f"\n**参数**:\n")
                for arg in entity['args']:
                    lines.append(f"- `{arg}`: ")
            if entity.get('returns'):
                lines.append(f"\n**返回**: `{entity['returns']}`")
        
        return '\n'.join(lines)
    
    def generate_readme_section(self, file_path: str, entities: List[Dict]) -> str:
        """生成README文档片段"""
        filename = Path(file_path).stem.replace('_', ' ').title()
        intent = self.extract_code_intent(open(file_path).read())
        intent_str = ' / '.join(intent)
        
        lines = [
            f"## {filename}",
            f"- **文件**: `{file_path}`",
            f"- **类型**: {' / '.join(set(e['type'] for e in entities))}",
            f"- **用途**: {intent_str}",
            "",
            "### 实体",
        ]
        
        for entity in entities:
            lines.append(f"- **{entity['type']}**: `{entity['name']}`")
            if entity.get('docstring'):
                # 取第一句话作为简介
                first_sentence = entity['docstring'].split('.')[0]
                lines.append(f"  - {first_sentence}.")
        
        return '\n'.join(lines)
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            language = self.detect_language(code)
            entities = []
            
            if language == 'python':
                try:
                    entities = self.extract_python_entities(code)
                except SyntaxError:
                    # 简单的正则提取作为后备
                    entities = self._simple_extract_entities(code)
            
            intent = self.extract_code_intent(code)
            
            self.stats['files_processed'] += 1
            self.stats['docs_generated'] += len(entities)
            
            return {
                'file': file_path,
                'language': language,
                'entities': entities,
                'intent': intent,
                'line_count': len(code.splitlines()),
                'code': code  # 用于base64编码
            }
        except Exception as e:
            return {'file': file_path, 'error': str(e)}
    
    def _simple_extract_entities(self, code: str) -> List[Dict]:
        """简单的实体提取（正则作为后备）"""
        entities = []
        
        # 提取类和函数
        class_pattern = r'class\s+(\w+)'
        func_pattern = r'def\s+(\w+)'
        
        for match in re.finditer(class_pattern, code):
            entities.append({
                'type': 'class',
                'name': match.group(1),
                'docstring': '',
                'methods': []
            })
        
        for match in re.finditer(func_pattern, code):
            entities.append({
                'type': 'function',
                'name': match.group(1),
                'docstring': '',
                'args': [],
                'returns': 'Any'
            })
        
        return entities
    
    def batch_analyze(self, directory: str, extensions: List[str] = ['.py']) -> List[Dict]:
        """批量分析目录中的文件"""
        results = []
        path = Path(directory)
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                result = self.analyze_file(str(file_path))
                if 'error' not in result:
                    results.append(result)
        
        return results
    
    def generate_markdown_docs(self, analysis_results: List[Dict], output_file: str = "DOCUMENTATION.md"):
        """生成完整的Markdown文档"""
        lines = [
            "# 自动生成的代码文档",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n统计: {self.stats['files_processed']} 个文件, {self.stats['docs_generated']} 个实体",
            "",
            "---",
            "",
            "# 目录",
        ]
        
        for result in analysis_results:
            filename = Path(result['file']).stem
            lines.append(f"- [{filename}](#{filename.lower().replace('_', '-')})")
        
        lines.append("")
        
        for result in analysis_results:
            lines.append(f"## {Path(result['file']).stem}")
            lines.append(f"\n**文件**: `{result['file']}`")
            lines.append(f"**语言**: {result['language']}")
            lines.append(f"**行数**: {result['line_count']}")
            lines.append(f"**类型**: {', '.join(set(e['type'] for e in result['entities']))}")
            
            for entity in result['entities']:
                lines.append("")
                docstring = self.generate_docstring(entity)
                lines.append(docstring)
            
            lines.append("\n---")
        
        content = '\n'.join(lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 文档已生成: {output_file}")
        return content
    
    def export_to_json(self, analysis_results: List[Dict], output_file: str = "docs.json"):
        """导出分析结果为JSON"""
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'stats': self.stats,
            'files': analysis_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"📦 数据已导出: {output_file}")
        return export_data


def demo():
    """演示函数"""
    print("🗂️ 智能代码文档生成器演示")
    print("=" * 50)
    
    # 创建示例代码
    sample_code = '''
#!/usr/bin/env python3
"""
示例计算器模块
提供基本的数学运算功能
"""

class Calculator:
    """一个简单的计算器类"""
    
    def __init__(self, precision: int = 2):
        """初始化计算器
        
        Args:
            precision: 小数精度
        """
        self.precision = precision
    
    def add(self, a: float, b: float) -> float:
        """加法运算
        
        Args:
            a: 第一个数
            b: 第二个数
            
        Returns:
            两数之和
        """
        return round(a + b, self.precision)
    
    def multiply(self, a: float, b: float) -> float:
        """乘法运算"""
        return round(a * b, self.precision)


def calculate_average(numbers: List[float]) -> float:
    """计算列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
'''
    
    # 创建临时文件
    with open('/tmp/sample_calculator.py', 'w') as f:
        f.write(sample_code)
    
    # 使用文档生成器
    generator = CodeDocumentGenerator()
    
    # 分析文件
    result = generator.analyze_file('/tmp/sample_calculator.py')
    
    print(f"\n📊 分析结果:")
    print(f"- 语言: {result['language']}")
    print(f"- 行数: {result['line_count']}")
    print(f"- 实体数量: {len(result['entities'])}")
    
    print(f"\n📝 发现的实体:")
    for entity in result['entities']:
        print(f"  - [{entity['type']}] {entity['name']}")
        if entity.get('docstring'):
            print(f"    文档: {entity['docstring'][:50]}...")
    
    # 生成文档
    print(f"\n📄 生成文档字符串:")
    for entity in result['entities']:
        doc = generator.generate_docstring(entity)
        print(doc[:100] + "..." if len(doc) > 100 else doc)
    
    print(f"\n✅ 统计: {generator.stats}")
    
    # 清理
    import os
    os.remove('/tmp/sample_calculator.py')


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo()
        return
    
    generator = CodeDocumentGenerator()
    
    print("🗂️ 智能代码文档生成器")
    print("=" * 40)
    print("用法:")
    print("  python smart_doc_generator.py <文件路径>")
    print("  python smart_doc_generator.py <目录路径> --batch")
    print("  python smart_doc_generator.py --demo")
    print()
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
        
        if Path(path).is_file():
            result = generator.analyze_file(path)
            print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif Path(path).is_dir():
            results = generator.batch_analyze(path)
            print(f"分析了 {len(results)} 个文件")
            
            # 生成文档
            generator.generate_markdown_docs(results, "DOCUMENTATION.md")
            generator.export_to_json(results, "docs.json")


if __name__ == '__main__':
    main()
