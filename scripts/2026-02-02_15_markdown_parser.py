#!/usr/bin/env python3
"""
Markdown文档解析器
支持解析标题、段落、列表、代码块、链接等元素
用于AI辅助文档分析和内容提取
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum


class ElementType(Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    BULLETED_LIST = "bulleted_list"
    NUMBERED_LIST = "numbered_list"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    BLOCKQUOTE = "blockquote"
    LINK = "link"
    IMAGE = "image"
    HORIZONTAL_RULE = "horizontal_rule"
    TABLE = "table"
    TEXT = "text"


@dataclass
class Element:
    type: ElementType
    content: str
    level: int = 1  # For headings
    children: Optional[List['Element']] = None
    
    def to_dict(self) -> dict:
        return {
            'type': self.type.value,
            'level': self.level,
            'content': self.content,
            'children': [c.to_dict() for c in self.children] if self.children else None
        }


class MarkdownParser:
    """Markdown文档解析器"""
    
    # 正则表达式模式
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w*)\n([\s\S]*?)\n```$')
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    BULLET_PATTERN = re.compile(r'^[\*\-\+]\s+(.+)$')
    NUMBERED_PATTERN = re.compile(r'^\d+\.\s+(.+)$')
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s*(.+)$')
    HR_PATTERN = re.compile(r'^[-*_]{3,}$')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    def __init__(self):
        self.elements: List[Element] = []
    
    def parse(self, text: str) -> List[Element]:
        """解析Markdown文本"""
        self.elements = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 跳过空行
            if not line.strip():
                i += 1
                continue
            
            # 标题
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                self.elements.append(Element(ElementType.HEADING, content, level))
                i += 1
                continue
            
            # 代码块
            code_match = self.CODE_BLOCK_PATTERN.match(line)
            if code_match:
                lang = code_match.group(1)
                code_content = code_match.group(2)
                # 收集多行代码块
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '```':
                        break
                    code_content += '\n' + lines[i]
                    i += 1
                self.elements.append(Element(ElementType.CODE_BLOCK, code_content.strip(), children=[Element(ElementType.TEXT, lang)]))
                i += 1
                continue
            
            # 引用块
            quote_match = self.BLOCKQUOTE_PATTERN.match(line)
            if quote_match:
                content = quote_match.group(1).strip()
                self.elements.append(Element(ElementType.BLOCKQUOTE, content))
                i += 1
                continue
            
            # 水平分割线
            if self.HR_PATTERN.match(line):
                self.elements.append(Element(ElementType.HORIZONTAL_RULE, '---'))
                i += 1
                continue
            
            # 列表项判断
            bullet_match = self.BULLET_PATTERN.match(line)
            numbered_match = self.NUMBERED_PATTERN.match(line)
            
            if bullet_match or numbered_match:
                list_type = ElementType.BULLETED_LIST if bullet_match else ElementType.NUMBERED_LIST
                content = (bullet_match or numbered_match).group(1).strip()
                self.elements.append(Element(ElementType.LIST_ITEM, content, children=[Element(ElementType.TEXT, list_type.value)]))
                i += 1
                continue
            
            # 段落
            self.elements.append(Element(ElementType.PARAGRAPH, line.strip()))
            i += 1
        
        return self.elements
    
    def extract_text(self) -> str:
        """提取纯文本内容"""
        texts = []
        for elem in self.elements:
            if elem.type == ElementType.CODE_BLOCK:
                texts.append(f"```{elem.content}```")
            elif elem.type == ElementType.HEADING:
                texts.append(f"{'#' * elem.level} {elem.content}")
            else:
                texts.append(elem.content)
        return '\n'.join(texts)
    
    def count_words(self) -> int:
        """统计单词数"""
        return len(self.extract_text().split())
    
    def get_structure(self) -> dict:
        """获取文档结构"""
        return {
            'total_elements': len(self.elements),
            'headings': sum(1 for e in self.elements if e.type == ElementType.HEADING),
            'paragraphs': sum(1 for e in self.elements if e.type == ElementType.PARAGRAPH),
            'code_blocks': sum(1 for e in self.elements if e.type == ElementType.CODE_BLOCK),
            'list_items': sum(1 for e in self.elements if e.type == ElementType.LIST_ITEM),
            'word_count': self.count_words()
        }


def demo():
    """演示"""
    sample_md = """# Markdown Parser Demo

这是一个演示文档。

## 主要功能

- 解析标题 (H1-H6)
- 解析代码块
- 解析列表
- 提取纯文本

## 代码示例

```python
def hello():
    print("Hello, World!")
```

> 这是一个引用块。

---
    
**链接示例**: [GitHub](https://github.com)
"""
    
    parser = MarkdownParser()
    elements = parser.parse(sample_md)
    
    print("=== 解析结果 ===")
    for elem in elements:
        print(f"[{elem.type.value}] {elem.content[:50]}...")
    
    print("\n=== 文档结构 ===")
    structure = parser.get_structure()
    for k, v in structure.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    demo()
