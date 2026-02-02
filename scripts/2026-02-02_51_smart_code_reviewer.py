#!/usr/bin/env python3
"""
智能代码审查工具 - Day 51
自动分析代码质量、检测问题、提供改进建议

功能:
- 代码复杂度分析
- 常见代码问题检测
- 最佳实践建议
- 代码风格检查
- 性能问题识别
"""

import re
import ast
import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from collections import Counter


class Severity(Enum):
    """问题严重级别"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass
class Issue:
    """代码问题"""
    line: int
    column: int
    severity: Severity
    category: str
    message: str
    suggestion: str


class CodeAnalyzer:
    """代码分析器基类"""
    
    def __init__(self):
        self.issues: List[Issue] = []
    
    def analyze(self, code: str, filepath: str) -> List[Issue]:
        raise NotImplementedError


class PythonAnalyzer(CodeAnalyzer):
    """Python代码分析器"""
    
    def __init__(self):
        super().__init__()
        self.issues = []
        self.complexity_scores = {}
    
    def analyze(self, code: str, filepath: str) -> Dict:
        """完整分析Python代码"""
        self.issues = []
        self.complexity_scores = {}
        
        lines = code.split('\n')
        
        # 各种检测
        self._check_basic_issues(code, lines)
        self._check_complexity(code, lines)
        self._check_best_practices(code, lines)
        self._check_security_issues(code, lines)
        self._check_performance(code, lines)
        self._check_style_issues(code, lines)
        
        # 计算总体评分
        score = self._calculate_score()
        
        return {
            'filepath': filepath,
            'language': 'Python',
            'total_lines': len(lines),
            'issues_count': {
                'critical': len([i for i in self.issues if i.severity == Severity.CRITICAL]),
                'warning': len([i for i in self.issues if i.severity == Severity.WARNING]),
                'info': len([i for i in self.issues if i.severity == Severity.INFO]),
                'style': len([i for i in self.issues if i.severity == Severity.STYLE]),
            },
            'total_issues': len(self.issues),
            'complexity_score': self.complexity_scores,
            'quality_score': score,
            'issues': [(i.line, i.severity.value, i.category, i.message, i.suggestion) 
                      for i in self.issues],
            'suggestions': self._generate_suggestions()
        }
    
    def _check_basic_issues(self, code: str, lines: List[str]):
        """检查基本问题"""
        # 检测TODO/FIXME
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                self.issues.append(Issue(
                    line=i, column=line.find('TODO')+1 if 'TODO' in line else line.find('FIXME')+1,
                    severity=Severity.INFO, category='maintainability',
                    message='发现TODO/FIXME注释',
                    suggestion='完成注释中描述的任务，或添加更详细说明'
                ))
        
        # 检测过长行
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(Issue(
                    line=i, column=121, severity=Severity.STYLE, category='readability',
                    message=f'行过长 ({len(line)} 字符)',
                    suggestion='建议将行长度控制在120字符以内'
                ))
        
        # 检测尾随空格
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\t '):
                self.issues.append(Issue(
                    line=i, column=len(line.rstrip())+1, severity=Severity.STYLE, category='formatting',
                    message='存在尾随空格',
                    suggestion='移除尾随空格以保持代码整洁'
                ))
    
    def _check_complexity(self, code: str, lines: List[str]):
        """检查代码复杂度"""
        # 统计函数
        functions = re.findall(r'^\s*def\s+(\w+)', code, re.MULTILINE)
        classes = re.findall(r'^\s*class\s+(\w+)', code, re.MULTILINE)
        
        self.complexity_scores['functions_count'] = len(functions)
        self.complexity_scores['classes_count'] = len(classes)
        
        # 检测嵌套深度
        max_indent = 0
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        self.complexity_scores['max_indentation'] = max_indent
        if max_indent > 80:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.WARNING, category='complexity',
                message=f'最大缩进深度: {max_indent}字符',
                suggestion='考虑重构以减少嵌套深度，提高代码可读性'
            ))
        
        # 检测长函数
        current_func_lines = 0
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*def\s+', line):
                if current_func_lines > 50:
                    self.issues.append(Issue(
                        line=i - current_func_lines, column=1, severity=Severity.WARNING,
                        category='complexity', message=f'前一个函数过长 ({current_func_lines}行)',
                        suggestion='建议将函数拆分，每个函数只做一件事'
                    ))
                current_func_lines = 0
            elif line.strip() and not line.strip().startswith('#'):
                current_func_lines += 1
    
    def _check_best_practices(self, code: str, lines: List[str]):
        """检查最佳实践"""
        # 检测硬编码密码/密钥
        patterns = [
            (r'password\s*=\s*["\'][^"\']{4,}["\']', '密码硬编码'),
            (r'api_key\s*=\s*["\'][^"\']{8,}["\']', 'API密钥硬编码'),
            (r'secret\s*=\s*["\'][^"\']{8,}["\']', '密钥硬编码'),
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                self.issues.append(Issue(
                    line=code.count('\n', 0, code.find(match)) + 1, column=1,
                    severity=Severity.CRITICAL, category='security',
                    message=f'发现{name}',
                    suggestion='使用环境变量或配置文件存储敏感信息'
                ))
        
        # 检测使用eval/exec
        if 'eval(' in code:
            self.issues.append(Issue(
                line=code.count('\n', 0, code.find('eval(')) + 1, column=1,
                severity=Severity.CRITICAL, category='security',
                message='使用eval()函数存在安全风险',
                suggestion='避免使用eval，考虑更安全的替代方案'
            ))
        
        # 检测pickle反序列化
        if 'pickle.load' in code:
            self.issues.append(Issue(
                line=code.count('\n', 0, code.find('pickle.load')) + 1, column=1,
                severity=Severity.WARNING, category='security',
                message='使用pickle.load存在反序列化风险',
                suggestion='仅从可信来源加载pickle数据，考虑使用JSON等替代'
            ))
        
        # 检测print调试语句
        print_count = len(re.findall(r'^\s*print\(', code, re.MULTILINE))
        if print_count > 0:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.INFO, category='debugging',
                message=f'发现{print_count}处print调试语句',
                suggestion='使用日志模块代替print，或在发布前移除'
            ))
    
    def _check_security_issues(self, code: str, lines: List[str]):
        """检查安全问题"""
        # 检测SQL注入风险
        sql_patterns = [
            r'sql\s*=\s*f["\'].*\{.*\}.*["\']',
            r'".*%.*".*%(s|d)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.issues.append(Issue(
                    line=code.count('\n', 0, code.find(pattern)) + 1, column=1,
                    severity=Severity.CRITICAL, category='security',
                    message='可能存在SQL注入风险',
                    suggestion='使用参数化查询或ORM防止SQL注入'
                ))
        
        # 检测命令注入
        if 'os.system' in code or 'subprocess' in code:
            # 检查是否有未验证的用户输入
            if re.search(r'subprocess.*shell\s*=\s*True', code, re.IGNORECASE):
                self.issues.append(Issue(
                    line=code.count('\n', 0, code.find('shell=True')) + 1, column=1,
                    severity=Severity.WARNING, category='security',
                    message='使用shell=True存在命令注入风险',
                    suggestion='尽量使用shell=False，或严格验证输入'
                ))
        
        # 检测XML外部实体
        if 'xml.etree' in code or 'lxml' in code:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.INFO, category='security',
                message='处理XML时注意XXE攻击',
                suggestion='禁用XML外部实体解析'
            ))
    
    def _check_performance(self, code: str, lines: List[str]):
        """检查性能问题"""
        # 检测循环中使用+
        if re.search(r'for.*:\s*$', code, re.MULTILINE):
            # 检查是否有字符串拼接
            if re.search(r'\+\s*["\']', code):
                self.issues.append(Issue(
                    line=1, column=1, severity=Severity.WARNING, category='performance',
                    message='循环中频繁使用字符串拼接',
                    suggestion='使用列表追加后join，或使用f-string'
                ))
        
        # 检测重复代码块
        lines_set = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        if len(lines_set) > 10:
            counter = Counter(lines_set)
            for line, count in counter.items():
                if count > 3:
                    line_num = next((i+1 for i, l in enumerate(lines) if l.strip() == line), 1)
                    self.issues.append(Issue(
                        line=line_num, column=1, severity=Severity.WARNING,
                        category='maintainability', message='发现重复代码块',
                        suggestion='考虑提取为函数以提高代码复用性'
                    ))
                    break
        
        # 检测不使用生成器
        if re.search(r'\[.*for.* in.*\]', code) and 'range(' in code:
            # 可能是大列表推导
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.INFO, category='performance',
                message='使用列表推导式处理大数据可能占用大量内存',
                suggestion='对于大数据集，考虑使用生成器表达式'
            ))
    
    def _check_style_issues(self, code: str, lines: List[str]):
        """检查代码风格"""
        # 检测不使用类型注解
        functions = re.findall(r'^\s*def\s+(\w+)\([^)]*\)', code, re.MULTILINE)
        typed_functions = re.findall(r'^\s*def\s+(\w+)\([^)]*:\s*\w+', code, re.MULTILINE)
        
        if functions and len(typed_functions) < len(functions) * 0.5:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.STYLE, category='type-hints',
                message='大多数函数未使用类型注解',
                suggestion='添加类型注解提高代码可维护性和IDE支持'
            ))
        
        # 检测变量命名
        var_patterns = re.findall(r'^\s*([a-z][a-z0-9_]*)\s*=\s*', code, re.MULTILINE)
        bad_names = [v for v in var_patterns if len(v) < 2 and v not in ['i', 'j', 'k', 'x', 'y', 'v']]
        if bad_names:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.STYLE, category='naming',
                message=f'发现{bad_names}等过于简短的变量名',
                suggestion='使用有意义的变量名提高代码可读性'
            ))
        
        # 检测缺少文档字符串
        functions_with_doc = re.findall(r'def\s+\w+[^:]*:(.*?)"""', code, re.DOTALL)
        all_functions = re.findall(r'^\s*def\s+(\w+)', code, re.MULTILINE)
        if all_functions and len(functions_with_doc) < len(all_functions) * 0.3:
            self.issues.append(Issue(
                line=1, column=1, severity=Severity.STYLE, category='documentation',
                message='大多数函数缺少文档字符串',
                suggestion='为函数和类添加docstring说明用途和参数'
            ))
    
    def _calculate_score(self) -> int:
        """计算代码质量评分 (0-100)"""
        score = 100
        
        for issue in self.issues:
            if issue.severity == Severity.CRITICAL:
                score -= 15
            elif issue.severity == Severity.WARNING:
                score -= 8
            elif issue.severity == Severity.INFO:
                score -= 3
            elif issue.severity == Severity.STYLE:
                score -= 1
        
        # 复杂度惩罚
        if self.complexity_scores.get('max_indentation', 0) > 60:
            score -= 5
        
        return max(0, min(100, score))
    
    def _generate_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        critical_count = len([i for i in self.issues if i.severity == Severity.CRITICAL])
        if critical_count > 0:
            suggestions.append(f'⚠️ 优先修复{critical_count}个严重问题')
        
        warning_count = len([i for i in self.issues if i.severity == Severity.WARNING])
        if warning_count > 0:
            suggestions.append(f'📝 处理{warning_count}个警告以提高代码质量')
        
        if self.complexity_scores.get('max_indentation', 0) > 60:
            suggestions.append('🔄 考虑重构减少代码嵌套深度')
        
        if len([i for i in self.issues if i.category == 'documentation']) > 2:
            suggestions.append('📚 添加更多文档字符串')
        
        return suggestions


class GeneralAnalyzer:
    """通用代码分析器（适用于其他语言）"""
    
    @staticmethod
    def analyze(code: str, filepath: str) -> Dict:
        """基础分析适用于任何代码"""
        lines = code.split('\n')
        
        issues = []
        
        # 基本检查
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'line': i, 'severity': 'style',
                    'message': f'行过长 ({len(line)} 字符)'
                })
            
            if line.rstrip() != line.rstrip('\t '):
                issues.append({
                    'line': i, 'severity': 'style',
                    'message': '存在尾随空格'
                })
            
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                issues.append({
                    'line': i, 'severity': 'info',
                    'message': '发现TODO/FIXME注释'
                })
        
        ext = os.path.splitext(filepath)[1].lower()
        language_map = {
            '.js': 'JavaScript', '.ts': 'TypeScript',
            '.py': 'Python', '.java': 'Java',
            '.go': 'Go', '.rs': 'Rust',
            '.cpp': 'C++', '.c': 'C',
            '.rb': 'Ruby', '.php': 'PHP'
        }
        
        return {
            'filepath': filepath,
            'language': language_map.get(ext, 'Unknown'),
            'total_lines': len(lines),
            'total_issues': len(issues),
            'issues': issues,
            'quality_score': max(0, 100 - len(issues) * 2)
        }


def analyze_file(filepath: str) -> Dict:
    """分析单个文件"""
    if not os.path.exists(filepath):
        return {'error': f'文件不存在: {filepath}'}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.py':
        analyzer = PythonAnalyzer()
        return analyzer.analyze(code, filepath)
    else:
        return GeneralAnalyzer.analyze(code, filepath)


def analyze_directory(dir_path: str, extensions: List[str] = None) -> Dict:
    """分析整个目录"""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.rb', '.php']
    
    results = {
        'directory': dir_path,
        'files_analyzed': 0,
        'total_issues': 0,
        'avg_quality_score': 0,
        'file_results': []
    }
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                filepath = os.path.join(root, file)
                result = analyze_file(filepath)
                if 'error' not in result:
                    results['files_analyzed'] += 1
                    results['total_issues'] += result.get('total_issues', 0)
                    results['file_results'].append(result)
    
    if results['file_results']:
        scores = [f.get('quality_score', 0) for f in results['file_results']]
        results['avg_quality_score'] = sum(scores) / len(scores)
    
    return results


def print_report(report: Dict, verbose: bool = False):
    """打印分析报告"""
    print('=' * 60)
    print('📊 代码审查报告')
    print('=' * 60)
    
    if 'error' in report:
        print(f'❌ 错误: {report["error"]}')
        return
    
    print(f'📁 文件: {report.get("filepath", "Unknown")}')
    print(f'🌐 语言: {report.get("language", "Unknown")}')
    print(f'📏 总行数: {report.get("total_lines", 0)}')
    
    if 'issues_count' in report:
        counts = report['issues_count']
        print(f'\n🔴 严重问题: {counts.get("critical", 0)}')
        print(f'🟡 警告: {counts.get("warning", 0)}')
        print(f'🔵 信息: {counts.get("info", 0)}')
        print(f'🟢 样式: {counts.get("style", 0)}')
    
    print(f'\n📈 质量评分: {report.get("quality_score", 0)}/100')
    
    if verbose:
        print(f'\n📋 详细问题:')
        for issue in report.get('issues', []):
            if len(issue) >= 5:
                print(f'  Line {issue[0]}: [{issue[1].upper()}] {issue[3]}')
                print(f'    → {issue[4]}')
    
    if 'suggestions' in report:
        print(f'\n💡 建议:')
        for suggestion in report['suggestions']:
            print(f'  {suggestion}')
    
    print('=' * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能代码审查工具')
    parser.add_argument('path', nargs='?', help='文件或目录路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归分析目录')
    parser.add_argument('-e', '--extensions', help='文件扩展名（逗号分隔）')
    
    args = parser.parse_args()
    
    if not args.path:
        args.path = '.'
    
    extensions = None
    if args.extensions:
        extensions = [f'.{ext.strip()}' for ext in args.extensions.split(',')]
    
    if os.path.isfile(args.path):
        report = analyze_file(args.path)
        print_report(report, args.verbose)
    elif os.path.isdir(args.path) and args.recursive:
        report = analyze_directory(args.path, extensions)
        print(f'\n📁 分析目录: {report["directory"]}')
        print(f'📄 分析文件数: {report["files_analyzed"]}')
        print(f'🐛 总问题数: {report["total_issues"]}')
        print(f'📈 平均质量评分: {report["avg_quality_score"]:.1f}/100')
        
        if args.verbose:
            print(f'\n📋 各文件详情:')
            for result in report['file_results'][:10]:  # 只显示前10个
                print(f'  {result["filepath"]}: {result.get("quality_score", 0)}/100 ({result.get("total_issues", 0)}问题)')
    else:
        print('❌ 请指定有效文件路径，或使用 -r 选项分析目录')
        parser.print_help()


if __name__ == '__main__':
    main()
