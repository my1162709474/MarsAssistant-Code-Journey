import json
import os
from datetime import datetime

class PromptManager:
    """AI提示词管理器 - 帮助管理和优化AI提示"""
    
    def __init__(self, database_file='prompts_db.json'):
        self.database_file = database_file
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """加载提示词数据库"""
        if os.path.exists(self.database_file):
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_prompts(self):
        """保存提示词数据库"""
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(self.prompts, f, ensure_ascii=False, indent=2)
    
    def add_prompt(self, name: str, template: str, category: str = "默认"):
        """添加新提示词模板"""
        prompt_id = len(self.prompts) + 1
        self.prompts[prompt_id] = {
            "name": name,
            "template": template,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        self._save_prompts()
        return prompt_id
    
    def get_prompt(self, prompt_id: int) -> str:
        """获取并使用提示词（增加使用计数）"""
        if prompt_id in self.prompts:
            self.prompts[prompt_id]["usage_count"] += 1
            self._save_prompts()
            return self.prompts[prompt_id]["template"]
        return None
    
    def search_prompts(self, keyword: str) -> list:
        """搜索提示词"""
        results = []
        for pid, prompt in self.prompts.items():
            if keyword.lower() in prompt["name"].lower() or keyword.lower() in prompt["category"].lower():
                results.append((pid, prompt["name"]))
        return results
    
    def list_by_category(self, category: str) -> list:
        """按类别列出提示词"""
        return [(pid, p["name"]) for pid, p in self.prompts.items() if p["category"] == category]
    
    def get_stats(self) -> dict:
        """获取使用统计"""
        total_usage = sum(p["usage_count"] for p in self.prompts.values())
        categories = set(p["category"] for p in self.prompts.values())
        return {
            "total_prompts": len(self.prompts),
            "total_usage": total_usage,
            "categories": list(categories)
        }

# 预置常用AI提示词模板
DEFAULT_PROMPTS = [
    ("代码审查助手", 
     "请作为资深代码审查专家，分析以下代码：\n{code}\n请从以下方面给出建议：\n1. 潜在bug\n2. 性能优化\n3. 代码风格\n4. 安全性考虑",
     "编程"),
    
    ("技术文档生成",
     "为以下代码生成技术文档：\n```{language}\n{code}\n```\n请生成包含函数说明、参数说明、返回值说明的完整文档",
     "文档"),
    
    ("Bug修复专家",
     "我遇到了以下错误：\n{error}\n相关代码：\n{code}\n请分析问题原因并提供修复方案",
     "调试"),
    
    ("代码解释器",
     "请详细解释以下代码的功能和工作原理：\n{code}\n请逐行分析并解释关键逻辑",
     "学习"),
]

def init_default_prompts():
    """初始化默认提示词"""
    manager = PromptManager()
    for name, template, category in DEFAULT_PROMPTS:
        manager.add_prompt(name, template, category)
    print(f"已初始化 {len(DEFAULT_PROMPTS)} 个默认提示词模板")
    return manager

if __name__ == "__main__":
    # 初始化并展示统计
    manager = init_default_prompts()
    stats = manager.get_stats()
    print(f"\n📊 提示词库统计：")
    print(f"   总模板数: {stats['total_prompts']}")
    print(f"   类别: {', '.join(stats['categories'])}")
    print(f"\n💡 使用方法:")
    print(f"   manager = PromptManager()")
    print(f"   prompt = manager.get_prompt(1)  # 获取第一个模板")
    print(f"   results = manager.search_prompts('代码')  # 搜索提示词")
