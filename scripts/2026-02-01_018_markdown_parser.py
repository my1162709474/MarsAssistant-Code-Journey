#!/usr/bin/env python3
"""
智能Markdown解析器 - Day 18
提取Markdown中的标题、链接、代码块、表格等元素
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class MarkdownElement:
    """Markdown元素"""
    type: str
    content: str
    level: int = 0
    line_number: int = 0
    children: List['MarkdownElement'] = field(default_factory=list)


class MarkdownParser:
    """智能Markdown解析器"""
    
    # 标题正则
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    # 链接正则
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    # 图片正则
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    # 代码块正则
    CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n([\s\S]*?)```')
    # 行内代码正则
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    # 粗体正则
    BOLD_PATTERN = re.compile(r'\*\*([^*]+)\*\*')
    # 斜体正则
    ITALIC_PATTERN = re.compile(r'\*([^*]+)\*')
    # 删除线正则
    STRIKETHROUGH_PATTERN = re.compile(r'~~([^~]+)~~')
    # 表格正则
    TABLE_PATTERN = re.compile(r'\|(.+)\|\n\|[-:| ]+\|\n((?:\|.+\|\n?)*)')
    # 列表正则
    LIST_PATTERN = re.compile(r'^[\s]*[-*+]\s+(.+)$')
    # 有序列表正则
    ORDERED_LIST_PATTERN = re.compile(r'^[\s]*\d+\.\s+(.+)$')
    # 引用正则
    QUOTE_PATTERN = re.compile(r'^>\s*(.+)$')
    # 分隔线正则
    HR_PATTERN = re.compile(r'^[-*_]{3,}$')
    # 检查框正则
    CHECKBOX_PATTERN = re.compile(r'^[\s]*[-*+]\s+\[([ x])\]\s+(.+)$')
    
    def __init__(self, content: str = None):
        self.content = content or ""
        self.elements: List[MarkdownElement] = []
        self.toc: List[Dict] = []  # 目录
        self.stats: Dict[str, int] = {}
        
    def parse(self, content: str = None) -> 'MarkdownParser':
        """解析Markdown内容"""
        self.content = content or self.content
        lines = self.content.split('\n')
        self.elements = []
        self.toc = []
        self.stats = self._init_stats()
        
        in_code_block = False
        code_block_lang = ""
        code_block_content = []
        current_list = []
        in_quote = False
        
        for i, line in enumerate(lines):
            # 处理代码块
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_lang = line[3:].strip()
                    code_block_content = []
                else:
                    # 保存代码块
                    self._add_element(MarkdownElement(
                        type="code_block",
                        content='\n'.join(code_block_content),
                        level=0,
                        line_number=i - len(code_block_content)
                    ))
                    self.stats['code_blocks'] += 1
                    in_code_block = False
                continue
            
            if in_code_block:
                code_block_content.append(line)
                continue
            
            # 检查标题
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                self._add_element(MarkdownElement(
                    type="heading",
                    content=text.strip(),
                    level=level,
                    line_number=i
                ))
                self.toc.append({
                    'level': level,
                    'text': text.strip(),
                    'line': i + 1
                })
                self.stats[f'heading_{level}'] += 1
                continue
            
            # 检查引用
            quote_match = self.QUOTE_PATTERN.match(line)
            if quote_match:
                self._add_element(MarkdownElement(
                    type="quote",
                    content=quote_match.group(1).strip(),
                    line_number=i
                ))
                self.stats['quotes'] += 1
                continue
            
            # 检查分隔线
            if self.HR_PATTERN.match(line):
                self._add_element(MarkdownElement(
                    type="hr",
                    content=line,
                    line_number=i
                ))
                self.stats['horizontal_rules'] += 1
                continue
            
            # 检查表格
            table_match = self.TABLE_PATTERN.match(line + '\n')
            if table_match:
                # 解析表格
                table_data = self._parse_table(table_match.group(1), table_match.group(2))
                self._add_element(MarkdownElement(
                    type="table",
                    content=json.dumps(table_data, ensure_ascii=False),
                    line_number=i
                ))
                self.stats['tables'] += 1
                # 跳过表格行
                for _ in range(len(table_data.get('rows', []))):
                    if i + 1 < len(lines):
                        i += 1
                continue
            
            # 检查列表
            checkbox_match = self.CHECKBOX_PATTERN.match(line)
            if checkbox_match:
                is_checked = checkbox_match.group(1) == 'x'
                text = checkbox_match.group(2)
                self._add_element(MarkdownElement(
                    type="task",
                    content=text,
                    line_number=i
                ))
                self.stats['tasks'] += 1
                self.stats['tasks_checked' if is_checked else 'tasks_unchecked'] += 1
                continue
            
            list_match = self.LIST_PATTERN.match(line)
            if list_match:
                self._add_element(MarkdownElement(
                    type="list_item",
                    content=list_match.group(1),
                    line_number=i
                ))
                self.stats['list_items'] += 1
                continue
            
            ordered_match = self.ORDERED_LIST_PATTERN.match(line)
            if ordered_match:
                self._add_element(MarkdownElement(
                    type="ordered_list_item",
                    content=ordered_match.group(1),
                    line_number=i
                ))
                self.stats['ordered_list_items'] += 1
                continue
            
            # 跳过空行
            if line.strip():
                self._add_element(MarkdownElement(
                    type="paragraph",
                    content=line.strip(),
                    line_number=i
                ))
                self.stats['paragraphs'] += 1
        
        return self
    
    def _init_stats(self) -> Dict[str, int]:
        """初始化统计"""
        return {
            'headings': 0,
            'heading_1': 0,
            'heading_2': 0,
            'heading_3': 0,
            'heading_4': 0,
            'heading_5': 0,
            'heading_6': 0,
            'links': 0,
            'images': 0,
            'code_blocks': 0,
            'inline_codes': 0,
            'bold_texts': 0,
            'italic_texts': 0,
            'strikethroughs': 0,
            'tables': 0,
            'quotes': 0,
            'list_items': 0,
            'ordered_list_items': 0,
            'tasks': 0,
            'tasks_checked': 0,
            'tasks_unchecked': 0,
            'horizontal_rules': 0,
            'paragraphs': 0
        }
    
    def _add_element(self, element: MarkdownElement):
        """添加元素"""
        self.elements.append(element)
        self._update_stats(element)
    
    def _update_stats(self, element: MarkdownElement):
        """更新统计"""
        type_mapping = {
            'heading': 'headings',
            'code_block': 'code_blocks',
            'inline_code': 'inline_codes',
            'bold': 'bold_texts',
            'italic': 'italic_texts',
            'strikethrough': 'strikethroughs',
            'table': 'tables',
            'quote': 'quotes',
            'list_item': 'list_items',
            'ordered_list_item': 'ordered_list_items',
            'task': 'tasks',
            'hr': 'horizontal_rules',
            'paragraph': 'paragraphs'
        }
        if element.type in type_mapping:
            self.stats[type_mapping[element.type]] += 1
        
        # 统计链接和图片
        if element.type in ['paragraph', 'heading', 'list_item', 'quote']:
            self.stats['links'] += len(self.LINK_PATTERN.findall(element.content))
            self.stats['images'] += len(self.IMAGE_PATTERN.findall(element.content))
            self.stats['inline_codes'] += len(self.INLINE_CODE_PATTERN.findall(element.content))
            self.stats['bold_texts'] += len(self.BOLD_PATTERN.findall(element.content))
            self.stats['italic_texts'] += len(self.ITALIC_PATTERN.findall(element.content))
            self.stats['strikethroughs'] += len(self.STRIKETHROUGH_PATTERN.findall(element.content))
    
    def _parse_table(self, header: str, rows: str) -> Dict:
        """解析表格"""
        headers = [h.strip() for h in header.split('|') if h.strip()]
        table_rows = []
        for row in rows.strip().split('\n'):
            if row.strip():
                cells = [c.strip() for c in row.split('|')[1:-1]]
                table_rows.append(cells)
        return {'headers': headers, 'rows': table_rows}
    
    def extract_links(self) -> List[Dict[str, str]]:
        """提取所有链接"""
        links = []
        for element in self.elements:
            for match in self.LINK_PATTERN.finditer(element.content):
                links.append({
                    'text': match.group(1),
                    'url': match.group(2),
                    'type': 'link'
                })
            for match in self.IMAGE_PATTERN.finditer(element.content):
                links.append({
                    'text': match.group(1),
                    'url': match.group(2),
                    'type': 'image'
                })
        return links
    
    def extract_code_blocks(self) -> List[Dict[str, str]]:
        """提取所有代码块"""
        return [
            {
                'language': elem.content.split('\n')[0] if '\n' in elem.content else '',
                'code': elem.content,
                'line': elem.line_number
            }
            for elem in self.elements
            if elem.type == 'code_block'
        ]
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps({
            'elements': [asdict(e) for e in self.elements],
            'toc': self.toc,
            'stats': self.stats,
            'links': self.extract_links(),
            'code_blocks': self.extract_code_blocks()
        }, ensure_ascii=False, indent=2)
    
    def to_html(self) -> str:
        """转换为HTML"""
        html_parts = ['<div class="markdown">']
        
        for element in self.elements:
            if element.type == 'heading':
                html_parts.append(f'<h{element.level}>{element.content}</h{element.level}>')
            elif element.type == 'paragraph':
                html_parts.append(f'<p>{element.content}</p>')
            elif element.type == 'code_block':
                html_parts.append(f'<pre><code>{element.content}</code></pre>')
            elif element.type == 'list_item':
                html_parts.append(f'<li>{element.content}</li>')
            elif element.type == 'quote':
                html_parts.append(f'<blockquote>{element.content}</blockquote>')
            elif element.type == 'hr':
                html_parts.append('<hr/>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def get_summary(self) -> Dict:
        """获取摘要"""
        total_elements = len(self.elements)
        return {
            'total_elements': total_elements,
            'stats': self.stats,
            'toc_depth': max([t['level'] for t in self.toc], default=0),
            'link_count': len(self.extract_links()),
            'code_block_count': len(self.extract_code_blocks())
        }


def demo():
    """演示"""
    sample_md = """# Markdown Parser Demo

这是一个**智能**Markdown解析器，支持解析：

## 功能特性

- 标题解析（1-6级）
- 链接提取：[GitHub](https://github.com)
- 图片：![Logo](logo.png)
- 代码块：
```python
def hello():
    print("Hello World!")
```
- 表格：

| 名称 | 描述 |
|------|------|
| 项目1 | 内容1 |
| 项目2 | 内容2 |

## 待办事项

- [x] 已完成任务
- [ ] 待办任务

> 这是一段引用文本。

---
"""
    
    parser = MarkdownParser(sample_md)
    parser.parse()
    
    print("=== Markdown解析结果 ===\n")
    print("📊 统计信息:")
    for key, value in parser.stats.items():
        if value > 0:
            print(f"  {key}: {value}")
    
    print("\n📑 目录:")
    for item in parser.toc:
        indent = "  " * (item['level'] - 1)
        print(f"{indent}• {item['text']} (第{item['line']}行)")
    
    print("\n🔗 链接:")
    for link in parser.extract_links():
        print(f"  [{link['type']}] {link['text']}: {link['url']}")
    
    print("\n💻 代码块:")
    for cb in parser.extract_code_blocks():
        print(f"  语言: {cb['language'] or 'text'}, 行: {cb['line']}")


if __name__ == "__main__":
    demo()
