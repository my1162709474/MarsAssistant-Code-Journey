#!/usr/bin/env python3
"""
Code Snippet Manager - 代码片段管理器
自动整理、搜索和管理代码片段
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional, List, Dict
import subprocess

class CodeSnippetManager:
    """管理代码片段的收集、整理和检索"""
    
    def __init__(self, snippets_dir: str = "snippets"):
        self.snippets_dir = snippets_dir
        self.index_file = "snippet_index.json"
        self._ensure_dirs()
        self._load_index()
    
    def _ensure_dirs(self):
        """创建必要的目录"""
        os.makedirs(self.snippets_dir, exist_ok=True)
    
    def _load_index(self):
        """加载索引文件"""
        index_path = os.path.join(self.snippets_dir, self.index_file)
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {"snippets": [], "tags": {}}
    
    def _save_index(self):
        """保存索引文件"""
        index_path = os.path.join(self.snippets_dir, self.index_file)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self, content: str) -> str:
        """生成代码片段的唯一ID"""
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def add_snippet(self, name: str, content: str, 
                   language: str = "", tags: List[str] = None,
                   description: str = "") -> Dict:
        """添加新的代码片段"""
        snippet_id = self._generate_id(content)
        filename = f"{snippet_id}_{name}.txt"
        filepath = os.path.join(self.snippets_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新索引
        snippet = {
            "id": snippet_id,
            "name": name,
            "filename": filename,
            "language": language,
            "tags": tags or [],
            "description": description,
            "created_at": datetime.now().isoformat(),
            "size": len(content)
        }
        
        self.index["snippets"].append(snippet)
        
        # 更新标签索引
        for tag in snippet["tags"]:
            if tag not in self.index["tags"]:
                self.index["tags"][tag] = []
            self.index["tags"][tag].append(snippet_id)
        
        self._save_index()
        return snippet
    
    def search(self, query: str) -> List[Dict]:
        """搜索代码片段"""
        results = []
        query_lower = query.lower()
        
        for snippet in self.index["snippets"]:
            # 搜索名称、描述、标签
            if (query_lower in snippet["name"].lower() or
                query_lower in snippet["description"].lower() or
                query_lower in snippet["language"].lower() or
                any(query_lower in tag for tag in snippet["tags"])):
                results.append(snippet)
        
        return results
    
    def list_by_tag(self, tag: str) -> List[Dict]:
        """按标签列出代码片段"""
        tag = tag.lower()
        snippet_ids = self.index["tags"].get(tag, [])
        
        return [s for s in self.index["snippets"] if s["id"] in snippet_ids]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_snippets": len(self.index["snippets"]),
            "total_tags": len(self.index["tags"]),
            "top_tags": sorted(
                [(tag, len(ids)) for tag, ids in self.index["tags"].items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "languages": list(set(s["language"] for s in self.index["snippets"] if s["language"]))
        }


# 示例使用
if __name__ == "__main__":
    manager = CodeSnippetManager()
    
    # 添加示例片段
    manager.add_snippet(
        name="快速排序",
        content="""
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
""",
        language="python",
        tags=["算法", "排序", "经典"],
        description="Python实现的快速排序算法"
    )
    
    manager.add_snippet(
        name="文件搜索",
        content="""
import os

def find_files(directory, extension=".py"):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                print(os.path.join(root, file))
""",
        language="python",
        tags=["文件", "搜索", "工具"],
        description="递归搜索指定扩展名的文件"
    )
    
    # 搜索示例
    print("搜索 '排序':")
    for s in manager.search("排序"):
        print(f"  - {s['name']} ({s['language']})")
    
    print("\n统计信息:")
    print(manager.get_stats())
