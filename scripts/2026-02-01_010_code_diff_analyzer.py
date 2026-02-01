#!/usr/bin/env python3
#""
代码差异分析器 - Code Diff Analyzer
===================================
功能：比较两个代码文件或文本的差异，高亮显示添加、删除和修改的行

使用方法：
    python code_diff_analyzer.py file1.py file2.py
    # 或者直接在代码中调用 compare_text(text1, text2)
"""

from typing import List, Tuple, Dict
import difflib
import hashlib


def read_file(filepath: str) -> str:
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"Error reading file: {e}"


def split_into_lines(text: str) -> List[str]:
    """将文本分割成行列表"""
    if not text:
        return []
    return text.splitlines(keepends=True)


def compute_line_hashes(lines: List[str]) -> Dict[str, List[int]]:
    """计算每行的哈希值，用于检测相似行"""
    hash_dict = {}
    for i, line in enumerate(lines):
        line_hash = hashlib.md5(line.encode()).hexdigest()[:8]
        if line_hash not in hash_dict:
            hash_dict[line_hash] = []
        hash_dict[line_hash].append(i)
    return hash_dict


def compare_text(text1: str, text2: str, 
                 show_context: int = 2) -> Dict:
    """
    比较两个文本的差异
    
    Returns:
        Dict包含: added_lines, deleted_lines, modified_lines, similarity
    """
    lines1 = split_into_lines(text1)
    lines2 = split_into_lines(text2)
    
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    
    result = {
        'added': [],
        'deleted': [],
        'modified': [],
        'unchanged': [],
        'similarity': round(matcher.ratio() * 100, 2),
        'stats': {
            'lines_added': 0,
            'lines_deleted': 0,
            'lines_modified': 0,
            'lines_unchanged': 0
        }
    }
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'insert':
            result['added'].extend(lines2[j1:j2])
            result['stats']['lines_added'] += (j2 - j1)
        elif tag == 'delete':
            result['deleted'].extend(lines1[i1:i2])
            result['stats']['lines_deleted'] += (i2 - i1)
        elif tag == 'replace':
            # 检测是否是真正的修改，还是删除+添加
            deleted = lines1[i1:i2]
            added = lines2[j1:j2]
            
            # 简单判断：行数相同且大部分相似才视为修改
            if len(deleted) == len(added):
                for d_line, a_line in zip(deleted, added):
                    if d_line.strip() == a_line.strip():
                        result['unchanged'].append(a_line)
                        result['stats']['lines_unchanged'] += 1
                    else:
                        result['modified'].append({
                            'before': d_line,
                            'after': a_line
                        })
                        result['stats']['lines_modified'] += 1
            else:
                result['deleted'].extend(deleted)
                result['added'].extend(added)
                result['stats']['lines_deleted'] += len(deleted)
                result['stats']['lines_added'] += len(added)
        elif tag == 'equal':
            result['unchanged'].extend(lines1[i1:i2])
            result['stats']['lines_unchanged'] += (i2 - i1)
    
    return result


def format_diff_report(diff_result: Dict, 
                       source_name: str = "Source 1", 
                       target_name: str = "Source 2") -> str:
    """生成格式化的差异报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("📊 代码差异分析报告 - Code Diff Report")
    lines.append("=" * 60)
    lines.append(f"\n比较: {source_name} vs {target_name}")
    lines.append(f"相似度: {diff_result['similarity']}%\n")
    
    lines.append("📈 统计信息:")
    lines.append(f"  ✅ 新增行数: {diff_result['stats']['lines_added']}")
    lines.append(f"  ❌ 删除行数: {diff_result['stats']['lines_deleted']}")
    lines.append(f"  🔄 修改行数: {diff_result['stats']['lines_modified']}")
    lines.append(f"  📝 未改动行数: {diff_result['stats']['lines_unchanged']}")
    lines.append("")
    
    if diff_result['added']:
        lines.append("🟢 新增的行 (Added):")
        for i, line in enumerate(diff_result['added'], 1):
            lines.append(f"  +{i:3d} | {line.rstrip()}")
        lines.append("")
    
    if diff_result['deleted']:
        lines.append("🔴 删除的行 (Deleted):")
        for i, line in enumerate(diff_result['deleted'], 1):
            lines.append(f"  -{i:3d} | {line.rstrip()}")
        lines.append("")
    
    if diff_result['modified']:
        lines.append("🟡 修改的行 (Modified):")
        for i, mod in enumerate(diff_result['modified'], 1):
            lines.append(f"  ~{i:3d} | 之前: {mod['before'].rstrip()}")
            lines.append(f"      | 现在: {mod['after'].rstrip()}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append(f"总体相似度: {'🟢 高' if diff_result['similarity'] > 80 else '🟡 中' if diff_result['similarity'] > 50 else '🔴 低'}")
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def create_unified_diff(text1: str, text2: str,
                        fromfile: str = "Original",
                        tofile: str = "Modified") -> str:
    """生成统一格式的差异输出 (类似 git diff)"""
    lines1 = split_into_lines(text1)
    lines2 = split_into_lines(text2)
    
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=fromfile,
        tofile=tofile,
        lineterm=''
    )
    
    return ''.join(diff)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 比较两个代码片段
    code_v1 = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
'''
    
    code_v2 = '''
def add(a, b):
    """返回两个数的和"""
    return a + b

def subtract(a, b):
    """返回两个数的差"""
    return a - b

def multiply(a, b):
    return a * b
'''
    
    print("🔍 示例1: 比较两个版本的函数库\n")
    result = compare_text(code_v1, code_v2)
    print(format_diff_report(result, "v1.py", "v2.py"))
    
    print("\n\n📝 统一格式差异 (unified diff):\n")
    print(create_unified_diff(code_v1, code_v2, "v1.py", "v2.py"))
    
    # 示例2: 比较文件
    # result = compare_text(read_file("old_version.py"), read_file("new_version.py"))
    # print(format_diff_report(result))
