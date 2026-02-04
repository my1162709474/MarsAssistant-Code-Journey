"""Code Snippet Manager - 代码片段管理工具
功能：组织、搜索、管理代码片段
"""
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    BASH = "bash"
    OTHER = "other"


class SnippetManager:
    """代码片段管理器"""
    
    def __init__(self, storage_file: str = "snippets.json"):
        self.storage_file = storage_file
        self.snippets = self._load_snippets()
    
    def _load_snippets(self) -> List[Dict]:
        """加载片段"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_snippets(self):
        """保存片段"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.snippets, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, code: str) -> str:
        """生成片段ID"""
        content = code.strip() + datetime.now().isoformat()
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def add_snippet(
        self,
        code: str,
        title: str,
        language: Language = Language.PYTHON,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict:
        """添加代码片段"""
        snippet = {
            "id": self._generate_id(code),
            "title": title,
            "code": code.strip(),
            "language": language.value,
            "tags": tags or [],
            "description": description or "",
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "favorites": False
        }
        self.snippets.insert(0, snippet)
        self._save_snippets()
        return snippet
    
    def search_snippets(
        self,
        query: str = "",
        language: Optional[Language] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False
    ) -> List[Dict]:
        """搜索片段"""
        results = self.snippets
        
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.get('title', '').lower() or
                   query_lower in s.get('description', '').lower() or
                   query_lower in s.get('code', '').lower()
            ]
        
        if language:
            results = [s for s in results if s['language'] == language.value]
        
        if tags:
            results = [s for s in results if any(t in s.get('tags', []) for t in tags)]
        
        if favorites_only:
            results = [s for s in results if s.get('favorites', False)]
        
        return results
    
    def get_snippet(self, snippet_id: str) -> Optional[Dict]:
        """获取单个片段"""
        for snippet in self.snippets:
            if snippet['id'] == snippet_id:
                snippet['usage_count'] += 1
                self._save_snippets()
                return snippet
        return None
    
    def update_snippet(self, snippet_id: str, **kwargs) -> Optional[Dict]:
        """更新片段"""
        for snippet in self.snippets:
            if snippet['id'] == snippet_id:
                for key, value in kwargs.items():
                    if key in ['title', 'code', 'language', 'tags', 'description', 'favorites']:
                        snippet[key] = value
                snippet['updated_at'] = datetime.now().isoformat()
                self._save_snippets()
                return snippet
        return None
    
    def delete_snippet(self, snippet_id: str) -> bool:
        """删除片段"""
        for i, snippet in enumerate(self.snippets):
            if snippet['id'] == snippet_id:
                del self.snippets[i]
                self._save_snippets()
                return True
        return False
    
    def toggle_favorite(self, snippet_id: str) -> Optional[Dict]:
        """切换收藏"""
        return self.update_snippet(snippet_id, favorites=not self.get_snippet(snippet_id).get('favorites', False))
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.snippets)
        languages = {}
        total_usage = 0
        favorites = 0
        
        for s in self.snippets:
            lang = s['language']
            languages[lang] = languages.get(lang, 0) + 1
            total_usage += s.get('usage_count', 0)
            if s.get('favorites', False):
                favorites += 1
        
        return {
            "total_snippets": total,
            "by_language": languages,
            "total_usage": total_usage,
            "favorites_count": favorites
        }


# 便捷函数
def quick_save_python(code: str, title: str, tags: Optional[List[str]] = None):
    """快速保存Python片段"""
    manager = SnippetManager()
    return manager.add_snippet(code, title, Language.PYTHON, tags)


def quick_search_python(query: str) -> List[Dict]:
    """搜索Python片段"""
    manager = SnippetManager()
    return manager.search_snippets(query, Language.PYTHON)


if __name__ == "__main__":
    print("Code Snippet Manager - 代码片段管理器!")
