#!/usr/bin/env python3
"""
AI Code Reviewer - 智能代码审查助手
分析代码质量、识别潜在问题并提供改进建议
"""

import ast
import re
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class Severity(Enum):
    """问题严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class CodeIssue:
    """代码问题"""
    line: int
    column: int
    severity: Severity
    message: str
    rule_id: str
    fix_suggestion: Optional[str] = None


@dataclass
class ReviewResult:
    """审查结果"""
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    score: float = 100.0
    summary: str = ""


class AI_code_reviewer:
    """AI代码审查助手"""
    
    # 代码质量规则
    RULES = {
        "R001": {
            "name": "Long Line",
            "message": "Line exceeds 100 characters",
            "severity": Severity.INFO,
            "check": lambda line: len(line) > 100
        },
        "R002": {
            "name": "Magic Number",
            "message": "Magic number detected, consider using named constant",
            "severity": Severity.SUGGESTION,
            "pattern": r'\b[2-9]|\b[1-9]\d{1,}'
        },
        "R003": {
            "name": "Print Statement",
            "message": "Avoid print statements in production code",
            "severity": Severity.WARNING,
            "pattern": r'^\s*print\('
        },
        "R004": {
            "name": "Hardcoded Path",
            "message": "Hardcoded path detected, consider using config",
            "severity": Severity.WARNING,
            "pattern": r'["\']/[a-zA-Z0-9_/-]+\.[a-z]+["\']'
        },
        "R005": {
            "name": "TODO Comment",
            "message": "TODO comment found, consider completing or creating issue",
            "severity": Severity.INFO,
            "pattern": r'#\s*TODO'
        }
    }
    
    def __init__(self, language: str = "python"):
        self.language = language
        self.issues: List[CodeIssue] = []
    
    def analyze_file(self, file_path: str) -> ReviewResult:
        """分析文件"""
        result = ReviewResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 运行基础检查
            self._check_line_issues(lines, result)
            
            # 如果是Python，进行AST分析
            if self.language == "python" and file_path.endswith('.py'):
                self._ast_analysis(content, result)
            
            # 计算指标
            self._calculate_metrics(lines, result)
            
            # 计算分数
            self._calculate_score(result)
            
            # 生成摘要
            self._generate_summary(result)
            
        except Exception as e:
            result.issues.append(CodeIssue(
                line=1, column=0,
                severity=Severity.ERROR,
                message=f"Analysis failed: {str(e)}",
                rule_id="R999"
            ))
        
        return result
    
    def _check_line_issues(self, lines: List[str], result: ReviewResult):
        """检查每行的问题"""
        for i, line in enumerate(lines, 1):
            for rule_id, rule in self.RULES.items():
                if "check" in rule and rule["check"](line):
                    result.issues.append(CodeIssue(
                        line=i,
                        column=0,
                        severity=rule["severity"],
                        message=rule["message"],
                        rule_id=rule_id
                    ))
                elif "pattern" in rule:
                    if re.search(rule["pattern"], line):
                        result.issues.append(CodeIssue(
                            line=i,
                            column=0,
                            severity=rule["severity"],
                            message=rule["message"],
                            rule_id=rule_id
                        ))
    
    def _ast_analysis(self, content: str, result: ReviewResult):
        """AST分析（Python）"""
        try:
            tree = ast.parse(content)
            
            # 检查深度过大的嵌套
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    if hasattr(node, 'body'):
                        depth = self._get_nesting_depth(node)
                        if depth > 4:
                            result.issues.append(CodeIssue(
                                line=node.lineno if hasattr(node, 'lineno') else 1,
                                column=node.col_offset if hasattr(node, 'col_offset') else 0,
                                severity=Severity.WARNING,
                                message=f"Deep nesting detected (depth={depth})",
                                rule_id="R100",
                                fix_suggestion="Consider refactoring into smaller functions"
                            ))
                
                # 检查过长的函数
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        func_length = node.end_lineno - node.lineno
                        if func_length > 50:
                            result.issues.append(CodeIssue(
                                line=node.lineno,
                                column=0,
                                severity=Severity.WARNING,
                                message=f"Function '{node.name}' is {func_length} lines long",
                                rule_id="R101",
                                fix_suggestion="Consider breaking into smaller functions"
                            ))
        except SyntaxError as e:
            result.issues.append(CodeIssue(
                line=e.lineno if hasattr(e, 'lineno') else 1,
                column=0,
                severity=Severity.ERROR,
                message=f"Syntax error: {e.msg}",
                rule_id="R999"
            ))
    
    def _get_nesting_depth(self, node) -> int:
        """获取嵌套深度"""
        depth = 0
        current = node
        while hasattr(current, 'parent'):
            current = current.parent
            depth += 1
        return depth
    
    def _calculate_metrics(self, lines: List[str], result: ReviewResult):
        """计算代码指标"""
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        blank_lines = len([l for l in lines if not l.strip()])
        
        result.metrics = {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": round(comment_lines / total_lines * 100, 2) if total_lines > 0 else 0,
            "issue_count": len(result.issues),
            "error_count": len([i for i in result.issues if i.severity == Severity.ERROR]),
            "warning_count": len([i for i in result.issues if i.severity == Severity.WARNING]),
            "suggestion_count": len([i for i in result.issues if i.severity == Severity.SUGGESTION])
        }
    
    def _calculate_score(self, result: ReviewResult):
        """计算代码质量分数"""
        score = 100.0
        
        for issue in result.issues:
            if issue.severity == Severity.ERROR:
                score -= 10
            elif issue.severity == Severity.WARNING:
                score -= 5
            elif issue.severity == Severity.SUGGESTION:
                score -= 2
            else:  # INFO
                score -= 1
        
        result.score = max(0, min(100, round(score, 1)))
    
    def _generate_summary(self, result: ReviewResult):
        """生成审查摘要"""
        metrics = result.metrics
        
        if result.score >= 90:
            quality = "Excellent"
        elif result.score >= 75:
            quality = "Good"
        elif result.score >= 60:
            quality = "Fair"
        else:
            quality = "Needs Improvement"
        
        result.summary = f"""
📊 Code Review Summary
{'='*40}
File: {result.file_path}
Quality Score: {result.score}/100 ({quality})

📈 Metrics:
  • Total Lines: {metrics['total_lines']}
  • Code Lines: {metrics['code_lines']}
  • Comments: {metrics['comment_lines']} ({metrics['comment_ratio']}%)
  • Blank Lines: {metrics['blank_lines']}

🐛 Issues Found: {metrics['issue_count']}
  🔴 Errors: {metrics['error_count']}
  🟡 Warnings: {metrics['warning_count']}
  💡 Suggestions: {metrics['suggestion_count']}
{'='*40}
"""
    
    def review_directory(self, directory: str) -> List[ReviewResult]:
        """审查目录中的所有文件"""
        results = []
        
        path = Path(directory)
        for file_path in path.rglob(f"*.{self.language}"):
            result = self.analyze_file(str(file_path))
            results.append(result)
        
        return results
    
    def print_result(self, result: ReviewResult):
        """打印审查结果"""
        print(result.summary)
        
        if result.issues:
            print("\n🔍 Detailed Issues:")
            print("-" * 60)
            for issue in result.issues:
                severity_icon = {
                    Severity.ERROR: "🔴",
                    Severity.WARNING: "🟡",
                    Severity.INFO: "🔵",
                    Severity.SUGGESTION: "💡"
                }
                print(f"{severity_icon[issue.severity]} [{issue.rule_id}] Line {issue.line}: {issue.message}")
                if issue.fix_suggestion:
                    print(f"   💡 Suggestion: {issue.fix_suggestion}")
        else:
            print("\n✅ No issues found! Great code!")


def main():
    """主函数"""
    import sys
    
    # 默认审查当前目录
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    
    reviewer = AI_code_reviewer()
    
    if Path(target).is_file():
        result = reviewer.analyze_file(target)
        reviewer.print_result(result)
    elif Path(target).is_dir():
        results = reviewer.review_directory(target)
        
        print(f"\n📁 Reviewed {len(results)} files\n")
        
        # 按分数排序
        results.sort(key=lambda x: x.score)
        
        for result in results:
            print(f"📄 {result.file_path}: {result.score}/100")
            
            # 打印分数低于90的文件详情
            if result.score < 90:
                reviewer.print_result(result)
    else:
        print(f"Error: {target} not found")


if __name__ == "__main__":
    main()
