"""
AI学习笔记生成器
从代码、文档或文本中提取关键概念，生成结构化学习笔记
"""

import re
import json
from typing import List, Dict, Tuple
from collections import Counter


class AINotesGenerator:
    """AI驱动的学习笔记生成器"""
    
    def __init__(self):
        self.keywords = self._load_keywords()
        self.patterns = self._load_patterns()
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """加载各类编程概念关键词"""
        return {
            "数据结构": ["list", "dict", "set", "tuple", "stack", "queue", "heap", 
                        "tree", "graph", "hash", "linked", "array", "matrix"],
            "算法": ["sort", "search", "recursive", "dynamic", "greedy", "binary",
                    " DFS", "BFS", "dijkstra", "backtrack", "divide", "conquer"],
            "编程概念": ["function", "class", "method", "inheritance", "polymorphism",
                       "encapsulation", "decorator", "generator", "iterator", "closure"],
            "设计模式": ["singleton", "factory", "observer", "strategy", "adapter",
                       "decorator", "proxy", "template", "command", "state"],
            "AI相关": ["neural", "network", "transformer", "attention", "embedding",
                      "token", "prompt", "fine-tune", "inference", "training"]
        }
    
    def _load_patterns(self) -> List[Tuple[str, str]]:
        """加载注释和文档模式"""
        return [
            (r'#\s*(TODO|FIXME|NOTE|HACK|XXX)\s*:?\s*(.*)', '标记'),
            (r'"""(.*?)"""', '文档字符串'),
            (r'\'\'\'(.*?)\'\'\'', '文档字符串'),
            (r'def\s+(\w+)\s*\((.*?)\)', '函数定义'),
            (r'class\s+(\w+)', '类定义'),
            (r'#\s*(.+)$', '注释'),
        ]
    
    def extract_concepts(self, text: str) -> Dict[str, List[str]]:
        """从文本中提取概念"""
        concepts = {category: [] for category in self.keywords}
        text_lower = text.lower()
        
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if keyword not in concepts[category]:
                        concepts[category].append(keyword)
        
        return {k: v for k, v in concepts.items() if v}
    
    def extract_code_elements(self, code: str) -> Dict:
        """提取代码元素"""
        elements = {
            "functions": [],
            "classes": [],
            "imports": [],
            "comments": []
        }
        
        # 提取函数
        for match in re.finditer(r'def\s+(\w+)\s*\((.*?)\):', code):
            elements["functions"].append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()]
            })
        
        # 提取类
        for match in re.finditer(r'class\s+(\w+)', code):
            elements["classes"].append(match.group(1))
        
        # 提取导入
        for match in re.finditer(r'^\s*(?:from|import)\s+(\w+)', code, re.MULTILINE):
            if match.group(1) not in elements["imports"]:
                elements["imports"].append(match.group(1))
        
        # 提取注释
        for match in re.finditer(r'#\s*(.+)$', code, re.MULTILINE):
            elements["comments"].append(match.group(1))
        
        return elements
    
    def calculate_complexity(self, code: str) -> Dict:
        """计算代码复杂度指标"""
        lines = code.split('\n')
        non_empty = [l for l in lines if l.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len(non_empty),
            "cyclomatic": 1,  # 基础复杂度
            "functions": 0,
            "classes": 0,
            "comment_ratio": 0
        }
        
        code_text = '\n'.join(lines)
        metrics["functions"] = code_text.count('def ')
        metrics["classes"] = code_text.count('class ')
        
        # 简单的圈复杂度估算
        for keyword in ['if ', 'elif ', 'for ', 'while ', 'and ', 'or ', 'except ']:
            metrics["cyclomatic"] += code_text.count(keyword)
        
        comment_count = len(re.findall(r'#', code))
        metrics["comment_ratio"] = round(comment_count / max(len(non_empty), 1), 2)
        
        return metrics
    
    def generate_summary(self, text: str) -> str:
        """生成文本摘要"""
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "无法生成摘要"
        
        # 找出关键词频率最高的句子
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                    'can', 'this', 'that', 'these', 'those', 'it', 'its'}
        word_freq = Counter(w for w in words if w not in stopwords and len(w) > 2)
        
        if not word_freq:
            return sentences[0] if sentences else ""
        
        scored = []
        for i, sentence in enumerate(sentences):
            score = sum(word_freq.get(w.lower(), 0) for w in sentence.split())
            scored.append((score, i, sentence))
        
        scored.sort(reverse=True)
        top_sentences = sorted(scored[:3], key=lambda x: x[1])
        
        return ' '.join(s[2] for s in top_sentences)
    
    def generate_notes(self, content: str, title: str = "学习笔记") -> Dict:
        """生成完整的学习笔记"""
        notes = {
            "title": title,
            "summary": self.generate_summary(content),
            "concepts": self.extract_concepts(content),
            "code_elements": self.extract_code_elements(content),
            "complexity": self.calculate_complexity(content) if content.count('\n') > 1 else {},
            "key_takeaways": [],
            "generated_at": self._timestamp()
        }
        
        # 生成要点
        concepts = notes["concepts"]
        if concepts:
            notes["key_takeaways"] = [
                f"学习重点：{', '.join(v)}" for v in concepts.values()
            ][:5]
        
        return notes
    
    def _timestamp(self) -> str:
        """生成时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_markdown(self, notes: Dict) -> str:
        """导出为Markdown格式"""
        md = [f"# {notes['title']}\n"]
        md.append(f"> 生成时间：{notes['generated_at']}\n")
        
        md.append("\n## 📋 摘要\n")
        md.append(f"{notes['summary']}\n")
        
        if notes['concepts']:
            md.append("\n## 🧠 核心概念\n")
            for category, items in notes['concepts'].items():
                md.append(f"### {category}\n")
                md.append(f"- " + "\n- ".join(items) + "\n")
        
        if notes['code_elements']['functions']:
            md.append("\n## 🔧 函数\n")
            for func in notes['code_elements']['functions']:
                params = ', '.join(func['params']) if func['params'] else '无参数'
                md.append(f"- `{func['name']}({params})`\n")
        
        if notes['code_elements']['classes']:
            md.append("\n## 📦 类\n")
            for cls in notes['code_elements']['classes']:
                md.append(f"- `{cls}`\n")
        
        if notes['complexity']:
            md.append("\n## 📊 代码指标\n")
            md.append(f"- 代码行数：{notes['complexity'].get('code_lines', 'N/A')}\n")
            md.append(f"- 函数数量：{notes['complexity'].get('functions', 'N/A')}\n")
            md.append(f"- 圈复杂度：{notes['complexity'].get('cyclomatic', 'N/A')}\n")
        
        if notes['key_takeaways']:
            md.append("\n## 💡 关键要点\n")
            for take in notes['key_takeaways']:
                md.append(f"- {take}\n")
        
        return '\n'.join(md)
    
    def export_json(self, notes: Dict) -> str:
        """导出为JSON格式"""
        return json.dumps(notes, ensure_ascii=False, indent=2)


def demo():
    """演示"""
    generator = AINotesGenerator()
    
    # 示例代码
    sample_code = '''
"""
这是一个示例模块，演示学习笔记生成器的功能
"""
import json
from datetime import datetime

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        self.data = []
    
    def load_data(self, filename: str) -> bool:
        """加载数据文件"""
        try:
            with open(filename, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception:
            return False
    
    def analyze(self) -> Dict:
        """分析数据"""
        return {
            "count": len(self.data),
            "avg": sum(self.data) / len(self.data) if self.data else 0
        }

def quick_sort(arr: List[int]) -> List[int]:
    """快速排序算法"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    
    return quick_sort(left) + [pivot] + quick_sort(right)
    '''
    
    # 生成笔记
    notes = generator.generate_notes(sample_code, "排序与数据结构示例")
    
    # 输出Markdown
    print("=" * 50)
    print("Markdown格式笔记：")
    print("=" * 50)
    print(generator.export_markdown(notes))
    
    print("\n" + "=" * 50)
    print("JSON格式笔记：")
    print("=" * 50)
    print(generator.export_json(notes))


if __name__ == "__main__":
    demo()
