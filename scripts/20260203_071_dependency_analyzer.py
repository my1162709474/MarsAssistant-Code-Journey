#!/usr/bin/env python3
"""
Project Dependency Analyzer
自动分析Python项目的依赖关系，生成依赖树和冲突检测
"""

import ast
import os
import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from pathlib import Path
import argparse


@dataclass
class Dependency:
    """依赖信息"""
    name: str
    version: Optional[str] = None
    is_standard: bool = False
    imported_in: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    from_imports: List[str] = field(default_factory=list)


class DependencyAnalyzer:
    """依赖分析器"""
    
    # Python标准库模块列表
    STANDARD_LIB = {
        'os', 'sys', 're', 'json', 'csv', 'datetime', 'time', 'math',
        'collections', 'itertools', 'functools', 'operator', 'string',
        'pathlib', 'typing', 'abc', 'copy', 'io', 'buffer', 'array',
        'struct', 'pickle', 'shelve', 'sqlite3', 'glob', 'fnmatch',
        'linecache', 'tokenize', 'keyword', 'ast', 'dis', 'inspect',
        'traceback', 'warnings', 'logging', 'threading', 'multiprocessing',
        'subprocess', 'socket', 'email', 'html', 'xml', 'urllib', 'http',
        'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib', 'nntplib',
        'base64', 'binascii', 'quopri', 'uu', 'configparser', 'netrc',
        'plistlib', 'hashlib', 'hmac', 'secrets', 'tls', 'ssl',
        'platform', 'errno', 'ctypes', 'signal', 'stat', 'codes',
        'locale', 'gettext', 'getopt', 'argparse', 'optparse', 'tempfile',
        'shutil', 'glob', 'macpath', 'genericpath', 'posixpath', 'ntpath',
        'functools', 'tools', 'weakref', 'types', 'contextlib', 'dataclasses',
        'enum', 'graphlib', 'pprint', 'textwrap', 'unicodedata', 'stringprep',
        'codecs', 'encoding', 'mbcs', 'iso2022_jp', 'cp037', 'cp1006',
        'ascii', 'latin_1', 'utf_8', 'utf_16', 'utf_32', 'raw_input',
        'input', 'vars', 'dir', 'help', 'setattr', 'getattr', 'delattr',
        'globals', 'locals', 'exec', 'eval', 'compile', 'execfile',
        'exit', 'quit', 'quit', 'print', 'open', 'file', 'range', 'xrange'
    }
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.dependencies: Dict[str, Dependency] = {}
        self.files_analyzed = 0
        self.errors = []
    
    def analyze(self) -> Dict:
        """执行完整分析"""
        self._scan_project()
        self._resolve_versions()
        return self.get_report()
    
    def _scan_project(self):
        """扫描项目中的所有Python文件"""
        python_files = list(self.project_path.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip(py_file):
                continue
            self._analyze_file(py_file)
    
    def _should_skip(self, path: Path) -> bool:
        """判断是否跳过该文件"""
        skip_patterns = ['__pycache__', '.git', 'venv', 'env', '.venv', 
                         'node_modules', '.tox', '.nox', 'dist', 'build']
        return any(pattern in str(path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path):
        """分析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.files_analyzed += 1
            rel_path = str(file_path.relative_to(self.project_path))
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_dependency(alias.name, rel_path, alias.asname)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_dependency(
                            node.module,
                            rel_path,
                            from_imports=[alias.name for alias in node.names]
                        )
        
        except Exception as e:
            self.errors.append(f"{file_path}: {str(e)}")
    
    def _add_dependency(self, name: str, file_path: str, 
                       alias: Optional[str] = None,
                       from_imports: Optional[List[str]] = None):
        """添加依赖"""
        # 只取顶级模块名
        top_level = name.split('.')[0]
        
        if top_level not in self.dependencies:
            self.dependencies[top_level] = Dependency(
                name=top_level,
                is_standard=top_level in self.STANDARD_LIB
            )
        
        dep = self.dependencies[top_level]
        dep.imported_in.append(file_path)
        if alias:
            dep.alias = alias
        if from_imports:
            dep.from_imports.extend(from_imports)
    
    def _resolve_versions(self):
        """尝试解析依赖版本"""
        # 检查requirements.txt
        req_files = list(self.project_path.rglob("requirements.txt"))
        
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        if '>=' in line:
                            name, version = line.split('>=')
                            name = name.strip()
                            version = version.strip()
                        elif '==' in line:
                            name, version = line.split('==')
                            name = name.strip()
                            version = version.strip()
                        elif '>' in line:
                            name, version = line.split('>')
                            name = name.strip()
                            version = version.strip()
                        else:
                            name = line
                            version = None
                        
                        if name in self.dependencies:
                            self.dependencies[name].version = version
            
            except Exception:
                pass
    
    def get_external_dependencies(self) -> List[Dependency]:
        """获取外部依赖列表"""
        return [d for d in self.dependencies.values() if not d.is_standard]
    
    def get_standard_dependencies(self) -> List[Dependency]:
        """获取标准库依赖列表"""
        return [d for d in self.dependencies.values() if d.is_standard]
    
    def get_report(self) -> Dict:
        """生成分析报告"""
        return {
            'summary': {
                'files_analyzed': self.files_analyzed,
                'total_dependencies': len(self.dependencies),
                'external_count': len(self.get_external_dependencies()),
                'standard_count': len(self.get_standard_dependencies()),
                'errors': len(self.errors)
            },
            'external_dependencies': [
                {
                    'name': d.name,
                    'version': d.version,
                    'imported_in': list(set(d.imported_in)),
                    'from_imports': list(set(d.from_imports))
                }
                for d in self.get_external_dependencies()
            ],
            'standard_dependencies': [
                {
                    'name': d.name,
                    'imported_in': list(set(d.imported_in))
                }
                for d in self.get_standard_dependencies()
            ],
            'errors': self.errors
        }
    
    def print_summary(self):
        """打印简洁摘要"""
        report = self.get_report()
        summary = report['summary']
        
        print("\n" + "=" * 50)
        print("📊 依赖分析报告")
        print("=" * 50)
        print(f"📁 扫描文件数: {summary['files_analyzed']}")
        print(f"📦 外部依赖: {summary['external_count']}")
        print(f"📚 标准库: {summary['standard_count']}")
        print(f"❌ 解析错误: {summary['errors']}")
        
        if report['external_dependencies']:
            print("\n🔗 外部依赖:")
            for dep in sorted(report['external_dependencies'], key=lambda x: x['name']):
                version = f" (v{dep['version']})" if dep['version'] else ""
                print(f"  • {dep['name']}{version}")
        
        print()
    
    def generate_dot_graph(self) -> str:
        """生成DOT格式的依赖图"""
        lines = [
            'digraph Dependencies {',
            '  rankdir=LR;',
            '  node [shape=box, style=filled];',
            '  bgcolor="#1e1e1e";',
            '  fontcolor=white;',
            ''
        ]
        
        # 外部依赖用不同颜色
        for dep in self.get_external_dependencies():
            files = len(set(dep.imported_in))
            lines.append(f'  "{dep.name}" [fillcolor="#4CAF50", label="{dep.name}\\n({files} files)"];')
        
        # 标准库用不同颜色
        for dep in self.get_standard_dependencies():
            files = len(set(dep.imported_in))
            lines.append(f'  "{dep.name}" [fillcolor="#2196F3", label="{dep.name}\\n({files} files)"];')
        
        lines.append('}')
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="项目依赖分析器")
    parser.add_argument('path', nargs='?', default='.', help='项目路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--dot', action='store_true', help='生成DOT格式依赖图')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.path)
    report = analyzer.analyze()
    
    if args.json:
        output = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
    
    elif args.dot:
        dot_output = analyzer.generate_dot_graph()
        if args.output:
            with open(args.output, 'w') as f:
                f.write(dot_output)
        else:
            print(dot_output)
    
    else:
        analyzer.print_summary()


if __name__ == '__main__':
    main()
