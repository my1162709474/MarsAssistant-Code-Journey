"""
Markdown转思维导图生成器
Day 4: 将Markdown结构转换为思维导图格式

功能：
1. 解析Markdown标题层级
2. 生成Mermaid思维导图格式
3. 支持输出到文件
4. 彩色主题支持
"""

import re
import sys
from typing import List, Dict


class MarkdownToMindmap:
    """Markdown转思维导图转换器"""
    
    # 主题配色方案
    THEMES = {
        "rainbow": {
            "1": "pink",
            "2": "gold", 
            "3": "lightgreen",
            "4": "skyblue",
            "5": "lavender"
        },
        "ocean": {
            "1": "darkblue",
            "2": "blue",
            "3": "teal",
            "4": "aquamarine",
            "5": "mintcream"
        },
        "sunset": {
            "1": "red",
            "2": "orange",
            "3": "gold",
            "4": "pink",
            "5": "lavender"
        }
    }
    
    def __init__(self, theme: str = "rainbow"):
        self.theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES["rainbow"])
    
    def parse_markdown(self, content: str) -> List[Dict]:
        """解析Markdown，提取标题层级"""
        lines = content.strip().split('\n')
        structure = []
        
        for line in lines:
            # 匹配ATX标题格式 (# ## ### 等)
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                structure.append({"level": level, "title": title})
            
            # 匹配无序列表 (- 或 * 或 +)
            list_match = re.match(r'^[\-\*\+]\s+(.+)$', line)
            if list_match:
                # 作为二级标题处理
                structure.append({"level": 2, "title": f"• {list_match.group(1).strip()}"})
        
        return structure
    
    def generate_mermaid(self, structure: List[Dict]) -> str:
        """生成Mermaid思维导图代码"""
        if not structure:
            return ""
        
        lines = ["mindmap"]
        
        for item in structure:
            level = min(item["level"], 5)  # 最多5层
            color = self.colors.get(str(level), "default")
            title = item["title"].replace('"', '\\"')
            indent = "  " * (level - 1)
            lines.append(f'{indent}  ({color})"{title}"')
        
        return '\n'.join(lines)
    
    def convert(self, markdown_content: str) -> str:
        """完整转换流程"""
        structure = self.parse_markdown(markdown_content)
        return self.generate_mermaid(structure)


def demo():
    """演示"""
    sample_markdown = """
# Python学习笔记

## 基础语法
- 变量和数据类型
- 运算符
- 条件语句

## 数据结构
### 列表
### 字典
### 元组

## 函数
### 参数类型
### 返回值
### 匿名函数

## 面向对象
### 类和对象
### 继承
### 多态
"""
    
    converter = MarkdownToMindmap(theme="ocean")
    mindmap = converter.convert(sample_markdown)
    
    print("=" * 50)
    print("📚 Markdown转思维导图 - 演示")
    print("=" * 50)
    print("\n原始Markdown:")
    print(sample_markdown)
    print("\n生成的Mermaid思维导图:")
    print(mindmap)
    print("\n" + "=" * 50)
    print("💡 使用方法：")
    print("   converter = MarkdownToMindmap(theme='sunset')")
    print("   mindmap = converter.convert(your_markdown)")
    print("=" * 50)


if __name__ == "__main__":
    demo()
