#!/usr/bin/env python3
"""
🎯 Markdown到思维导图转换器
将Markdown大纲转换为多种格式的思维导图

功能:
- 支持XMind格式 (.xmind)
- 支持Markdowne��纲格式
- 支持文本树形结构
- 支持JSON思维导图格式

使用方法:
    python markdown_mindmap_converter.py input.md -o output.xmind
    python markdown_mindmap_converter.py input.md --format text_tree
    python markdown_mindmap_converter.py input.md --format json
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Node:
    """思维导图节点"""
    title: str
    content: Optional[str] = None
    children: List['Node'] = field(default_factory=list)
    level: int = 0
    
    def to_dict(self) -> dict:
        ""*转换为字典"""
        result = {"title": self.title}
        if self.content:
            result["content"] = self.content
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result


class MarkdownMindmapConverter:
    """Markdown到思维导图转换器"""
    
    # 节点类型标记
    TODO_MARK = "☐"
    DONE_MARK = "☑"
    STAR_MARK = "⭐"
    IMPORTANT_MARK = "📌"
    QUESTION_MARK = '❓"
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.root = Node(title=self.filepath.stem)
        
    def parse(self) -> Node:
        """解析Markdown文件"""
        content = self.filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 构建节点树
        self._build_tree(lines)
        return self.root
    
    def _get_indent_level(self, line: str) -> int:
        """计算缩进级别 (每个tab或4个空格为一级)"""
        indent = len(line) - len(line.lstrip())
        return indent // 4 + 1
    
    def _parse_node_marker(self, line: str) -> tuple:
        """解析节点标记"""
        # 检查特殊标记
        if line.startswith(self.TODO_MARK + " "):
            return "todo", line[2:].strip()
        elif line.startswith(self.DONE_MARK + " "):
            return "done", line[2:].strip()
        elif line.startswith(self.STAR_MARK + " "):
            return "star", line[2:].strip()
        elif line.startswith(self.IMPORTANT_MARK + " "):
            return "important", line[2:].strip()
        elif line.startswith(self.QUESTION_MARK + " "):
            return "question", line[2:].strip()
        return "normal", line.strip()
    
    def _build_tree(self, lines: List[str]):
        """构建节点树"""
        stack = [(0, self.root)]  # (level, node)
        
        for line in lines:
            if not line.strip():
                continue
            
            # 跳过代码块标记
            if line.strip().startswith('```'):
                continue
            if line.strip().startswith('---'):
                continue
            
            # 解析标记
            marker_type, content = self._parse_node_marker(line)
            
            # 计算层级
            level = self._get_indent_level(line)
            
            # 提取标题（去掉markdown链接）
            title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
            title = title.split('::')[0].strip()  # 去掉描述部分
            title = title.split('【')[0].strip()  # 去掉备注
            
            # 创建新节点
            node = Node(title=title, level=level)
            
            # 查找父节点
            while stack and stack[-1][0] >= level:
                stack.pop()
            
            if stack:
                parent = stack[-1][1]
                parent.children.append(node)
            
            stack.append((level, node))
    
    def to_text_tree(self, indent: str = "  ") -> str:
        """转换为文本树形结构"""
        lines = []
        self._render_text_tree(self.root, lines, "", indent)
        return '\n'.join(lines)
    
    def _render_text_tree(self, node: Node, lines: List[str], prefix: str = "", indent: str = "  "):
        """渲染文本树"""
        lines.append(f"{prefix}{node.title}")
        for i, child in enumerate(node.children):
            is_last = (i == len(node.children) - 1)
            child_prefix = prefix + ("└" if is_last else "├") + "─"
            self._render_text_tree(child, lines, child_prefix, indent)
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON格式"""
        return json.dumps(self.root.to_dict(), ensure_ascii=False, indent=indent)
    
    def to_xmind_json(self) -> dict:
        ""*转换为XMind格式"""
        return {
            "title": self.root.title,
            "topic": self._to_xmind_topic(self.root),
            "created": datetime.now().isoformat()
        }
    
    def _to_xmind_topic(self, node: Node) -> dict:
        """转换为XMind主题格式"""
        topic = {"title": node.title}
        if node.children:
            topic["children"] = {
                "attached": [self._to_xmind_topic(child) for child in node.children]
            }
        return topic
    
    def save_xmind(self, output_path: str):
        """保存为XMind格式"""
        # XMind实际上是一个ZIP包，这里保存为简化的JSON
        xmind_data = self.to_xmind_json()
        
        # 保存为JSON文件（可以导入到思维导图软件）
        output = Path(output_path)
        output.write_text(
            json.dumps(xmind_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"✅ 已保存到: {output_path}")
    
    def save_text_tree(self, output_path: str):
        """保存为文本树形格式"""
        output = Path(output_path)
        output.write_text(self.to_text_tree(), encoding='utf-8')
        print(f"✅ 已保存到: {output_path}")
    
    def save_json(self, output_path: str):
        """保存为JSON格式"""
        output = Path(output_path)
        output.write_text(self.to_json(), encoding='utf-8')
        print(f"✅ 已保存到: {output_path}")


def create_sample_mindmap():
    """创建示例思维导图"""
    sample = """# 学习计划

## 编程技能
    ### Python基础
        语法和数据类型
        面向对象编程
    ### Web开发
        Flask框架
        Django框架

## 数据结构
    ### 线性结构
        数组和链表
        栈和队列
    ### 非线性结构
        树和二叉树
        图算法

## 机器学习
    ### 监督学习
        线性回归
        决策树
    ### 无监督学习
        聚类算法
        降维技术

## 项目实践
    ☑ 完成第一个Web项目
    ☐ 开发数据分析工具
    ☐ 部署机器学习模型
"""
    
    sample_file = Path("sample_mindmap.md")
    sample_file.write_text(sample, encoding='utf-8')
    print(f"📝 已创建示例文件: {sample_file}")
    return sample_file


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🎯 Markdown到思维导图转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python markdown_mindmap_converter.py input.md -o output.xmind
    python markdown_mindmap_converter.py input.md --format text_tree
    python markdown_mindmap_converter.py input.md --format json
        """
    )
    
    parser.add_argument("input", help="输入Markdown文件")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-f", "--format", choices=["xmind", "text_tree", "json"], 
                       default="xmind", help="输出格式 (默认: xmind)")
    parser.add_argument("-s", "--sample", action="store_true", help="创建示例文件")
    
    args = parser.parse_args()
    
    if args.sample:
        sample_file = create_sample_mindmap()
        args.input = str(sample_file)
    
    if not Path(args.input).exists():
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)
    
    # 解析Markdown
    converter = MarkdownMindmapConverter(args.input)
    converter.parse()
    
    # 确定输出路径
    output_path = args.output
    if not output_path:
        if args.format == "xmind":
            output_path = Path(args.input).stem + ".xmind.json"
        elif args.format == "text_tree":
            output_path = Path(args.input).stem + ".tree.txt"
        else:
            output_path = Path(args.input).stem + ".json"
    
    # 保存结果
    if args.format == "xmind":
        converter.save_xmind(output_path)
    elif args.format == "text_tree":
        converter.save_text_tree(output_path)
    else:
        converter.save_json(output_path)
    
    # 打印预览
    print("\n📋 文本树预览:")
    print("-" * 40)
    print(converter.to_text_tree())


if __name__ == "__main__":
    main()
