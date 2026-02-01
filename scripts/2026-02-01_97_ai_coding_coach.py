#!/usr/bin/env python3
"""
🤖 AI Coding Coach - 代码审查助手
Day 97: 智能代码分析与优化建议工具

功能：
- 代码复杂度分析
- 潜在问题检测
- 优化建议生成
- 代码风格评分
"""

import re
import ast
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CodeIssue:
    """代码问题"""
    line: int
    severity: str  # warning, error, suggestion
    message: str
    suggestion: str


class CodingCoach:
    """AI编程教练 - 代码分析工具"""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.score = 100
    
    def analyze_python(self, code: str) -> Dict:
        """分析Python代码"""
        self.issues = []
        self.score = 100
        
        lines = code.split('\n')
        
        # 基本检查
        self._check_line_length(lines)
        self._check_naming_conventions(code)
        self._check_comments(code)
        self._check_hardcoded_values(code)
        self._check_error_handling(code)
        self._check_duplication(code)
        
        # AST分析
        try:
            tree = ast.parse(code)
            self._ast_analysis(tree)
        except SyntaxError:
            self.issues.append(CodeIssue(
                line=1, severity='error',
                message='代码存在语法错误',
                suggestion='请检查括号、引号等是否匹配'
            ))
            self.score -= 20
        
        return {
            'score': max(0, self.score),
            'issues': [(i.line, i.severity, i.message, i.suggestion) 
                      for i in self.issues],
            'summary': self._generate_summary()
        }
    
    def _check_line_length(self, lines: List[str]):
        """检查行长度"""
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                self.issues.append(CodeIssue(
                    line=i, severity='suggestion',
                    message=f'行{i}过长 ({len(line)}字符)',
                    suggestion='建议将行长度控制在79字符以内'
                ))
                self.score -= 1
    
    def _check_naming_conventions(self, code: str):
        """检查命名规范"""
        # 检查大写下划线混合的变量名
        camel_case_vars = re.findall(r'\b[a-z]+[A-Z]\w*\b', code)
        if camel_case_vars:
            self.issues.append(CodeIssue(
                line=1, severity='suggestion',
                message='发现驼峰式命名',
                suggestion='Python推荐使用下划线分隔的小写字母(snake_case)'
            ))
            self.score -= 2
    
    def _check_comments(self, code: str):
        """检查注释质量"""
        comment_lines = len(re.findall(r'#.*$', code, re.MULTILINE))
        code_lines = len([l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')])
        
        if code_lines > 10 and comment_lines == 0:
            self.issues.append(CodeIssue(
                line=1, severity='warning',
                message='代码缺少注释',
                suggestion='建议为复杂逻辑添加注释说明'
            ))
            self.score -= 5
    
    def _check_hardcoded_values(self, code: str):
        """检查硬编码值"""
        # 检查魔法数字
        magic_numbers = re.findall(r'(?<![.\w])([2-9]|\d{2,})(?![.\d])', code)
        if len(magic_numbers) > 3:
            self.issues.append(CodeIssue(
                line=1, severity='suggestion',
                message='存在硬编码的数字',
                suggestion='建议使用有意义的常量替代魔法数字'
            ))
            self.score -= 2
    
    def _check_error_handling(self, code: str):
        """检查错误处理"""
        if 'except:' in code or 'except :' in code:
            self.issues.append(CodeIssue(
                line=1, severity='warning',
                message='使用裸except捕获所有异常',
                suggestion='建议指定具体的异常类型'
            ))
            self.score -= 5
    
    def _check_duplication(self, code: str):
        """检查代码重复"""
        lines = [l.strip() for l in code.split('\n') if l.strip()]
        unique_lines = set(lines)
        if len(lines) > 10 and (1 - len(unique_lines)/len(lines)) > 0.3:
            self.issues.append(CodeIssue(
                line=1, severity='suggestion',
                message='可能存在代码重复',
                suggestion='考虑将重复代码提取为函数'
            ))
            self.score -= 3
    
    def _ast_analysis(self, tree: ast.AST):
        """AST深度分析"""
        for node in ast.walk(tree):
            # 检查深层嵌套
            if isinstance(node, (ast.If, ast.For, ast.While)):
                if hasattr(node, 'body') and len(node.body) > 10:
                    self.issues.append(CodeIssue(
                        line=node.lineno if hasattr(node, 'lineno') else 1,
                        severity='warning',
                        message='代码块可能过于复杂',
                        suggestion='考虑拆分为多个小函数'
                    ))
                    self.score -= 3
    
    def _generate_summary(self) -> str:
        """生成分析总结"""
        if self.score >= 90:
            return "🌟 优秀！代码质量很高，继续保持！"
        elif self.score >= 70:
            return "👍 不错！有一些小问题需要改进。"
        elif self.score >= 50:
            return "⚠️ 中等，建议重点优化这些问题。"
        else:
            return "🚨 需要大幅改进，建议重新设计代码结构。"
    
    def give_advice(self, topic: str) -> str:
        """根据主题给出学习建议"""
        advice = {
            'algorithm': '📚 算法学习建议：\n'
                        '1. 先理解问题，再动手写代码\n'
                        '2. 从简单例子开始，画图辅助理解\n'
                        '3. 多练习经典题目：排序、搜索、动态规划\n'
                        '4. 学会分析时间空间复杂度',
            
            'debug': '🔧 调试技巧：\n'
                    '1. 使用print/logging打印关键变量\n'
                    '2. 学习使用pdb/ipdb调试器\n'
                    '3. 小黄鸭调试法：向他人解释代码\n'
                    '4. 编写单元测试验证每个函数',
            
            'design': '🏗️ 设计原则：\n'
                     '1. SOLID原则：单一职责、开放封闭等\n'
                     '2. KISS原则：保持简单\n'
                     '3. DRY原则：不要重复自己\n'
                     '4. 先设计后编码，画流程图'
        }
        return advice.get(topic.lower(), '💡 持续学习，多写代码，多读源码！')


def demo():
    """演示代码分析"""
    coach = CodingCoach()
    
    # 示例代码
    sample_code = '''
def calculate(a,b,c):
    result = a + b + c * 2 + 100
    return result

x=calculate(1,2,3)
y=calculate(4,5,6)
print(x,y)
'''
    
    print("=" * 60)
    print("🤖 AI Coding Coach - 代码审查演示")
    print("=" * 60)
    
    result = coach.analyze_python(sample_code)
    
    print(f"\n📊 代码质量评分: {result['score']}/100")
    print(f"\n📝 发现的问题:")
    
    for line, severity, msg, suggestion in result['issues']:
        icon = {'error': '❌', 'warning': '⚠️', 'suggestion': '💡'}[severity]
        print(f"  {icon} 第{line}行: {msg}")
        print(f"     → {suggestion}")
    
    print(f"\n💬 {result['summary']}")
    print("\n" + "=" * 60)
    print("📚 学习建议 - 算法主题:")
    print(coach.give_advice('algorithm'))
    print("=" * 60)


if __name__ == '__main__':
    demo()
