#!/usr/bin/env python3
"""
智能代码相似度检测器
检测代码重复、相似片段、代码克隆
"""

import ast
import hashlib
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
import json


@dataclass
class CodeClone:
    """代码克隆"""
    file1: str
    file2: str
    type1: str  # file, function, block
    type2: str
    start1: int
    end1: int
    start2: int
    end2: int
    similarity: float
    lines1: int
    lines2: int
    code1: str = ""
    code2: str = ""


@dataclass
class TokenInfo:
    """Token信息"""
    type: str
    value: str
    line: int


class CodeSimilarityDetector:
    """代码相似度检测器"""
    
    def __init__(self, min_similarity: float = 0.7, min_lines: int = 5):
        self.min_similarity = min_similarity
        self.min_lines = min_lines
        self.normalized_cache: Dict[str, List[str]] = {}
        
        # 文件类型处理器
        self.parsers = {
            '.py': self._parse_python,
            '.js': self._parse_js,
            '.java': self._parse_java,
            '.cpp': self._parse_cpp,
            '.c': self._parse_cpp,
            '.go': self._parse_go,
            '.rs': self._parse_rust,
        }
    
    def _normalize_code(self, code: str) -> List[str]:
        """标准化代码（去除注释、空格、变量名等）"""
        cache_key = hashlib.md5(code.encode()).hexdigest()
        if cache_key in self.normalized_cache:
            return self.normalized_cache[cache_key]
        
        lines = code.strip().split('\n')
        normalized = []
        
        for line in lines:
            # 去除行内注释
            if '//' in line:
                line = line.split('//')[0]
            if '#' in line:
                line = line.split('#')[0]
            
            # 去除多余空白
            line = ' '.join(line.split())
            
            # 替换变量名（简单的单字母替换）
            line = re.sub(r'[a-zA-Z_]\w*', 'VAR', line)
            
            if line.strip():
                normalized.append(line)
        
        self.normalized_cache[cache_key] = normalized
        return normalized
    
    def _tokenize(self, code: str) -> List[TokenInfo]:
        """简单分词"""
        tokens = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 字符串
            strings = re.findall(r'["\'].*?["\']', line)
            for s in strings:
                tokens.append(TokenInfo('string', s, i))
                line = line.replace(s, 'STRING')
            
            # 数字
            numbers = re.findall(r'\b\d+\.?\d*\b', line)
            for n in numbers:
                tokens.append(TokenInfo('number', n, i))
                line = line.replace(n, 'NUM')
            
            # 标识符
            identifiers = re.findall(r'\b[a-zA-Z_]\w*\b', line)
            for ident in identifiers:
                if ident not in ['if', 'else', 'for', 'while', 'def', 'class', 'return', 
                                'import', 'from', 'var', 'let', 'const', 'function']:
                    tokens.append(TokenInfo('identifier', ident, i))
            
            # 关键词
            keywords = ['if', 'else', 'for', 'while', 'def', 'class', 'return', 'import',
                       'from', 'var', 'let', 'const', 'function', 'public', 'private']
            for kw in keywords:
                if re.search(r'\b' + kw + r'\b', line):
                    tokens.append(TokenInfo('keyword', kw, i))
        
        return tokens
    
    def _get_ngrams(self, lines: List[str], n: int = 3) -> Set[Tuple[str, ...]]:
        """获取n-gram特征"""
        ngrams = set()
        for i in range(len(lines) - n + 1):
            ngram = tuple(lines[i:i+n])
            ngrams.add(ngram)
        return ngrams
    
    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Jaccard相似度"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """计算两个代码块的相似度"""
        norm1 = self._normalize_code(code1)
        norm2 = self._normalize_code(code2)
        
        if len(norm1) < self.min_lines or len(norm2) < self.min_lines:
            return 0.0
        
        # 方法1: Jaccard相似度（基于n-gram）
        ngrams1 = self._get_ngrams(norm1)
        ngrams2 = self._get_ngrams(norm2)
        jaccard = self._jaccard_similarity(ngrams1, ngrams2)
        
        # 方法2: 长度相似度
        len_sim = 1 - abs(len(norm1) - len(norm2)) / max(len(norm1), len(norm2))
        
        # 综合相似度
        similarity = 0.6 * jaccard + 0.4 * len_sim
        
        return min(1.0, similarity)
    
    def _parse_python(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析Python代码，提取函数和代码块"""
        blocks = {'functions': [], 'classes': []}
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 获取函数代码
                    lines = content.split('\n')
                    start = node.lineno - 1
                    end = node.end_lineno if hasattr(node, 'end_lineno') else start + 10
                    code = '\n'.join(lines[start:end])
                    
                    blocks['functions'].append((node.lineno, end, code, node.name))
                
                elif isinstance(node, ast.ClassDef):
                    lines = content.split('\n')
                    start = node.lineno - 1
                    end = node.end_lineno if hasattr(node, 'end_lineno') else start + 20
                    code = '\n'.join(lines[start:end])
                    
                    blocks['classes'].append((node.lineno, end, code, node.name))
        
        except:
            pass
        
        return blocks
    
    def _parse_js(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析JavaScript代码"""
        blocks = {'functions': [], 'classes': []}
        
        # 提取函数
        func_pattern = r'(?:function\s+(\w+)\s*\([^)]*\)\s*\{|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{)'
        for match in re.finditer(func_pattern, content):
            name = match.group(1) or match.group(2)
            start = content[:match.start()].count('\n')
            
            # 找到对应的闭合括号
            brace_count = 0
            in_string = False
            end = match.start()
            for i, char in enumerate(content[match.start():], 1):
                if char in '"\'' and (i == 1 or content[match.start()+i-2] != '\\'):
                    in_string = not in_string
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = match.start() + i
                            break
            
            code = content[match.start():end]
            blocks['functions'].append((start, content[:end].count('\n'), code, name))
        
        return blocks
    
    def _parse_java(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析Java代码"""
        return self._parse_cpp(content)
    
    def _parse_cpp(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析C/C++代码"""
        blocks = {'functions': [], 'classes': []}
        
        # 提取函数
        func_pattern = r'(\w+)\s+\w+\s*\([^)]*\)\s*\{'
        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            start = content[:match.start()].count('\n')
            
            brace_count = 0
            for i, char in enumerate(content[match.start():], 1):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = match.start() + i
                        break
            
            code = content[match.start():end]
            blocks['functions'].append((start, content[:end].count('\n'), code, name))
        
        return blocks
    
    def _parse_go(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析Go代码"""
        return self._parse_cpp(content)
    
    def _parse_rust(self, content: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """解析Rust代码"""
        blocks = {'functions': [], 'classes': []}
        
        # 提取fn函数
        func_pattern = r'fn\s+(\w+)\s*\([^)]*\)\s*(?:->[^=]+\s*)?\{'
        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            start = content[:match.start()].count('\n')
            
            brace_count = 0
            for i, char in enumerate(content[match.start():], 1):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = match.start() + i
                        break
            
            code = content[match.start():end]
            blocks['functions'].append((start, content[:end].count('\n'), code, name))
        
        return blocks
    
    def _get_file_blocks(self, file_path: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """获取文件中的代码块"""
        ext = os.path.splitext(file_path)[1].lower()
        parser = self.parsers.get(ext, self._parse_python)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return parser(content)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {'functions': [], 'classes': []}
    
    def compare_files(self, file1: str, file2: str) -> List[CodeClone]:
        """比较两个文件"""
        clones = []
        
        blocks1 = self._get_file_blocks(file1)
        blocks2 = self._get_file_blocks(file2)
        
        # 比较函数
        for start1, end1, code1, name1 in blocks1.get('functions', []):
            for start2, end2, code2, name2 in blocks2.get('functions', []):
                similarity = self._calculate_similarity(code1, code2)
                
                if similarity >= self.min_similarity:
                    lines1 = code1.count('\n') + 1
                    lines2 = code2.count('\n') + 1
                    
                    clones.append(CodeClone(
                        file1=file1, file2=file2,
                        type1='function', type2='function',
                        start1=start1, end1=end1,
                        start2=start2, end2=end2,
                        similarity=similarity,
                        lines1=lines1, lines2=lines2,
                        code1=code1[:200], code2=code2[:200]
                    ))
        
        # 比较类
        for start1, end1, code1, name1 in blocks1.get('classes', []):
            for start2, end2, code2, name2 in blocks2.get('classes', []):
                similarity = self._calculate_similarity(code1, code2)
                
                if similarity >= self.min_similarity:
                    lines1 = code1.count('\n') + 1
                    lines2 = code2.count('\n') + 1
                    
                    clones.append(CodeClone(
                        file1=file1, file2=file2,
                        type1='class', type2='class',
                        start1=start1, end1=end1,
                        start2=start2, end2=end2,
                        similarity=similarity,
                        lines1=lines1, lines2=lines2,
                        code1=code1[:200], code2=code2[:200]
                    ))
        
        # 如果没有找到函数/类级别的相似，比较整个文件
        if not clones:
            try:
                with open(file1, 'r', encoding='utf-8') as f:
                    content1 = f.read()
                with open(file2, 'r', encoding='utf-8') as f:
                    content2 = f.read()
                
                similarity = self._calculate_similarity(content1, content2)
                
                if similarity >= self.min_similarity:
                    clones.append(CodeClone(
                        file1=file1, file2=file2,
                        type1='file', type2='file',
                        start1=1, end1=content1.count('\n'),
                        start2=1, end2=content2.count('\n'),
                        similarity=similarity,
                        lines1=content1.count('\n') + 1,
                        lines2=content2.count('\n') + 1
                    ))
            except Exception as e:
                print(f"Error comparing files: {e}")
        
        return clones
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> Dict[str, List[CodeClone]]:
        """扫描目录中的所有文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs']
        
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        
        clones_dict = {}
        total = len(files)
        
        for i, file1 in enumerate(files):
            print(f"Scanning {i+1}/{total}: {file1}")
            
            for file2 in files[i+1:]:
                clones = self.compare_files(file1, file2)
                
                if clones:
                    key = f"{os.path.basename(file1)} <-> {os.path.basename(file2)}"
                    clones_dict[key] = clones
        
        return clones_dict
    
    def detect_similarity(self, code1: str, code2: str) -> float:
        """检测两个代码块的相似度"""
        return self._calculate_similarity(code1, code2)


def print_clone_report(clones: List[CodeClone], title: str = "Code Clone Report"):
    """打印克隆报告"""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print(f"{'='*70}")
    
    if not clones:
        print("✅ 未检测到代码克隆")
        return
    
    # 按相似度排序
    clones.sort(key=lambda x: x.similarity, reverse=True)
    
    for i, clone in enumerate(clones, 1):
        similarity_pct = clone.similarity * 100
        emoji = "🔴" if clone.similarity > 0.9 else "🟡" if clone.similarity > 0.7 else "🟢"
        
        print(f"\n{i}. {emoji} 代码克隆 (相似度: {similarity_pct:.1f}%)")
        print(f"   📁 文件1: {clone.file1} ({clone.type1}, 行{clone.start1}-{clone.end1})")
        print(f"   📁 文件2: {clone.file2} ({clone.type2}, 行{clone.start2}-{clone.end2})")
        print(f"   📏 代码行数: {clone.lines1} vs {clone.lines2}")
        
        if clone.code1:
            print(f"\n   📝 代码片段1 (前200字符):")
            for line in clone.code1.split('\n')[:3]:
                print(f"      {line}")
        
        if clone.code2:
            print(f"\n   📝 代码片段2 (前200字符):")
            for line in clone.code2.split('\n')[:3]:
                print(f"      {line}")
    
    # 统计
    avg_similarity = sum(c.similarity for c in clones) / len(clones)
    high_similarity = sum(1 for c in clones if c.similarity > 0.9)
    medium_similarity = sum(1 for c in clones if 0.7 < c.similarity <= 0.9)
    
    print(f"\n{'='*70}")
    print(f"📊 统计:")
    print(f"   总克隆数: {len(clones)}")
    print(f"   高相似度 (>90%): {high_similarity}")
    print(f"   中相似度 (70-90%): {medium_similarity}")
    print(f"   平均相似度: {avg_similarity*100:.1f}%")
    print(f"{'='*70}")


def main():
    """主函数 - 示例用法"""
    print("🔍 智能代码相似度检测器")
    print("="*70)
    
    detector = CodeSimilarityDetector(min_similarity=0.7, min_lines=3)
    
    # 示例代码
    code1 = '''
def calculate_sum(numbers):
    result = 0
    for num in numbers:
        result = result + num
    return result
'''
    
    code2 = '''
def calculate_total(values):
    total = 0
    for val in values:
        total = total + val
    return total
'''
    
    code3 = '''
def calculate_average(numbers):
    sum_val = 0
    count = len(numbers)
    for num in numbers:
        sum_val = sum_val + num
    return sum_val / count if count > 0 else 0
'''
    
    print("\n📝 测试代码相似度:")
    print("-" * 50)
    
    sim1_2 = detector.detect_similarity(code1, code2)
    sim1_3 = detector.detect_similarity(code1, code3)
    sim2_3 = detector.detect_similarity(code2, code3)
    
    print(f"代码1 vs 代码2: {sim1_2*100:.1f}%")
    print(f"代码1 vs 代码3: {sim1_3*100:.1f}%")
    print(f"代码2 vs 代码3: {sim2_3*100:.1f}%")
    
    # 检测克隆
    print("\n\n📁 检测代码克隆:")
    print("-" * 50)
    
    clones = [
        CodeClone(
            file1="utils.py", file2="helpers.py",
            type1="function", type2="function",
            start1=10, end1=20, start2=5, end2=15,
            similarity=0.85, lines1=10, lines2=10,
            code1="def calculate_sum(numbers):...", code2="def calculate_total(values):..."
        ),
        CodeClone(
            file1="processor.py", file2="processor_v2.py",
            type1="function", type2="function",
            start1=50, end1=80, start2=100, end2=130,
            similarity=0.92, lines1=30, lines2=30,
            code1="def process_data(data):...", code2="def process_user_data(data):..."
        )
    ]
    
    print_clone_report(clones, "示例克隆检测结果")
    
    # 目录扫描示例
    print("\n\n💡 使用示例 - 扫描目录:")
    print("-" * 50)
    print("""
# 创建检测器
detector = CodeSimilarityDetector(min_similarity=0.7, min_lines=5)

# 扫描目录
clones = detector.scan_directory("/path/to/your/code")

# 打印报告
for key, clones in clones.items():
    print_clone_report(clones, key)
""")


if __name__ == "__main__":
    main()
