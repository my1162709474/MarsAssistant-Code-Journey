#!/usr/bin/env python3
"""
智能文档格式化工具
支持多种文档格式的智能转换、格式化和优化

功能:
- Markdown/HTML/纯文本互转
- 代码高亮格式化
- 表格美化
- 智能换行和排版
- 文档结构分析
- 格式化验证
"""

import re
import html
import json
import base64
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import hashlib


class FormatType(Enum):
    """文档格式类型"""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAINTEXT = "plaintext"
    RST = "rst"
    ASCIIDOC = "asciidoc"
    LATEX = "latex"


class TextAlignment(Enum):
    """文本对齐方式"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass
class TableConfig:
    """表格配置"""
    align: TextAlignment = TextAlignment.LEFT
    header_style: str = "bold"
    border_char: str = "|"
    border_style: str = "-"
    min_width: int = 3
    max_width: int = 50
    collapse_empty: bool = False


@dataclass
class DocumentInfo:
    """文档信息"""
    title: str = ""
    headings: List[Tuple[int, str]] = field(default_factory=list)
    word_count: int = 0
    char_count: int = 0
    line_count: int = 0
    code_blocks: int = 0
    tables: int = 0
    links: int = 0
    images: int = 0
    format_type: FormatType = FormatType.PLAINTEXT
    reading_time: int = 0  # 秒


class SmartDocumentFormatter:
    """智能文档格式化工具"""
    
    # 代码高亮配色
    CODE_THEME = {
        "keyword": "\033[94m",      # 蓝色
        "string": "\033[92m",       # 绿色
        "number": "\033[93m",       # 黄色
        "comment": "\033[90m",      # 灰色
        "function": "\033[95m",     # 紫色
        "reset": "\033[0m",         # 重置
    }
    
    # Markdown符号映射
    MARKDOWN_SYMBOLS = {
        "*": "•",
        "-": "–",
        "+": "►",
        ">": "▸",
        "#": "■",
    }
    
    def __init__(self):
        self.code_keywords = {
            "python": ["def", "class", "if", "elif", "else", "for", "while", 
                      "return", "import", "from", "as", "try", "except", 
                      "with", "yield", "lambda", "and", "or", "not", "in", "is"],
            "javascript": ["function", "const", "let", "var", "if", "else", 
                          "for", "while", "return", "import", "export", 
                          "class", "async", "await", "try", "catch"],
            "java": ["public", "private", "protected", "class", "interface",
                    "if", "else", "for", "while", "return", "import", "new"],
        }
        self.html_entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
    
    # ==================== 格式转换 ====================
    
    def markdown_to_html(self, text: str) -> str:
        """Markdown转HTML"""
        lines = text.split('\n')
        html_lines = []
        in_code_block = False
        code_language = ""
        in_list = False
        list_level = 0
        
        for line in lines:
            # 代码块检测
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_language = line[3:].strip()
                    html_lines.append(f'<pre><code class="language-{code_language}">')
                else:
                    in_code_block = False
                    html_lines.append('</code></pre>')
                continue
            
            if in_code_block:
                html_lines.append(self._escape_html(line))
                continue
            
            # 标题检测
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text_content = heading_match.group(2)
                html_lines.append(f'<h{level}>{self._escape_html(text_content)}</h{level}>')
                continue
            
            # 代码行检测
            if line.startswith('    ') or line.startswith('\t'):
                html_lines.append(f'<pre><code>{self._escape_html(line.strip())}</code></pre>')
                continue
            
            # 引用检测
            if line.startswith('>'):
                content = line[1:].lstrip(' >')
                html_lines.append(f'<blockquote>{self._escape_html(content)}</blockquote>')
                continue
            
            # 水平线
            if re.match(r'^[-*_]{3,}$', line.strip()):
                html_lines.append('<hr>')
                continue
            
            # 列表检测
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                content = list_match.group(3)
                
                current_level = indent // 2
                is_ordered = marker.replace('.', '').isdigit()
                
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                
                if is_ordered:
                    tag = 'ol'
                else:
                    tag = 'ul'
                
                html_lines.append(f'<li>{self._escape_html(content)}</li>')
                continue
            
            if in_list:
                in_list = False
            
            # 表格检测
            if '|' in line and line.strip().startswith('|'):
                if not line.strip().startswith('|---'):
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    cells = [f'<td>{self._escape_html(p)}</td>' for p in parts]
                    html_lines.append(f'<tr>{"".join(cells)}</tr>')
                continue
            
            # 段落
            if line.strip():
                # 处理行内格式
                content = self._escape_html(line)
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
                content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
                content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
                html_lines.append(f'<p>{content}</p>')
        
        return '\n'.join(html_lines)
    
    def html_to_markdown(self, html: str) -> str:
        """HTML转Markdown"""
        lines = html.split('\n')
        markdown_lines = []
        in_list = False
        list_type = None
        
        # 简单解析（生产环境建议使用专门的库如html2text）
        content = html
        content = re.sub(r'<h1[^>]*>(.+?)</h1>', r'# \1\n', content)
        content = re.sub(r'<h2[^>]*>(.+?)</h2>', r'## \1\n', content)
        content = re.sub(r'<h3[^>]*>(.+?)</h3>', r'### \1\n', content)
        content = re.sub(r'<h([4-6])[^>]*>(.+?)</h\1>', r'#### \2\n', content)
        content = re.sub(r'<strong[^>]*>(.+?)</strong>', r'**\1**', content)
        content = re.sub(r'<b[^>]*>(.+?)</b>', r'**\1**', content)
        content = re.sub(r'<em[^>]*>(.+?)</em>', r'*\1*', content)
        content = re.sub(r'<i[^>]*>(.+?)</i>', r'*\1*', content)
        content = re.sub(r'<code[^>]*>(.+?)</code>', r'`\1`', content)
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.+?)</a>', r'[\2](\1)', content)
        content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>', r'![\2](\1)', content)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<li[^>]*>(.+?)</li>', r'- \1\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        
        return content.strip()
    
    def plaintext_to_markdown(self, text: str, heading_level: int = 2) -> str:
        """纯文本转Markdown"""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                result.append('')
                continue
            
            # 检测是否为标题（全是大写或以特定模式开头）
            if stripped.isupper() and len(stripped) > 3:
                result.append(f'{"#" * heading_level} {stripped.title()}')
            elif re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:$', stripped):
                result.append(f'{"#" * (heading_level + 1)} {stripped.rstrip(":")}')
            elif re.match(r'^\d+[\.\)]\s+', stripped):
                result.append(stripped)
            elif stripped.startswith('- ') or stripped.startswith('* '):
                result.append(stripped)
            else:
                # 普通段落
                result.append(stripped)
        
        return '\n'.join(result)
    
    def markdown_to_plaintext(self, markdown: str) -> str:
        """Markdown转纯文本"""
        text = markdown
        
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # 移除行内代码
        text = re.sub(r'`[^`]+`', '', text)
        
        # 移除图片
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        
        # 移除链接（保留文字）
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 移除标题符号
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 移除引用符号
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # 移除列表符号
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # 移除水平线
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余空白
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    # ==================== 表格处理 ====================
    
    def format_table(self, data: List[List[str]], config: TableConfig = None) -> str:
        """格式化表格"""
        if not data:
            return ""
        
        config = config or TableConfig()
        
        # 计算列宽
        col_widths = []
        for col_idx in range(len(data[0])):
            max_width = max(len(str(row[col_idx])) for row in data)
            col_widths.append(min(max_width, config.max_width))
        
        # 构建表格
        lines = []
        
        # 表头
        header = data[0]
        separator = self._build_table_separator(col_widths, config)
        
        header_line = self._build_table_row(header, col_widths, config)
        lines.append(header_line)
        lines.append(separator)
        
        # 数据行
        for row in data[1:]:
            row_line = self._build_table_row(row, col_widths, config)
            lines.append(row_line)
        
        return '\n'.join(lines)
    
    def _build_table_separator(self, col_widths: List[int], config: TableConfig) -> str:
        """构建表格分隔线"""
        parts = []
        for width in col_widths:
            parts.append('-' * (width + 2))
        return f"+{'+'.join(parts)}+"
    
    def _build_table_row(self, row: List[str], col_widths: List[int], 
                        config: TableConfig) -> str:
        """构建表格行"""
        cells = []
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            cell_text = str(cell)[:width]
            padding = width - len(cell_text)
            
            if config.align == TextAlignment.CENTER:
                left_pad = padding // 2
                right_pad = padding - left_pad
                cells.append(f" {left_pad * ' '}{cell_text}{right_pad * ' '} ")
            elif config.align == TextAlignment.RIGHT:
                cells.append(f" {padding * ' '}{cell_text} ")
            else:
                cells.append(f" {cell_text}{padding * ' '} ")
        
        return f"|{''.join(cells)}|"
    
    def parse_markdown_table(self, table_text: str) -> List[List[str]]:
        """解析Markdown表格"""
        lines = [line for line in table_text.split('\n') 
                if '|' in line and not line.strip().startswith('|---')]
        
        if not lines:
            return []
        
        data = []
        for line in lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            data.append(cells)
        
        return data
    
    def table_to_markdown(self, data: List[List[str]], 
                         headers: List[str] = None) -> str:
        """表格转Markdown格式"""
        if not data:
            return ""
        
        if headers:
            data = [headers] + data
        
        # 计算列宽
        col_widths = []
        for col_idx in range(len(data[0])):
            max_width = max(len(str(row[col_idx])) for row in data)
            col_widths.append(max_width)
        
        lines = []
        
        # 构建分隔行
        separator_parts = []
        for width in col_widths:
            separator_parts.append('-' * (width + 2))
        separator = f"|{'|'.join(separator_parts)}|"
        
        # 表头
        header_line = self._build_markdown_row(data[0], col_widths)
        lines.append(header_line)
        lines.append(separator)
        
        # 数据行
        for row in data[1:]:
            row_line = self._build_markdown_row(row, col_widths)
            lines.append(row_line)
        
        return '\n'.join(lines)
    
    def _build_markdown_row(self, row: List[str], col_widths: List[int]) -> str:
        """构建Markdown表格行"""
        cells = []
        for cell, width in zip(row, col_widths):
            cell_text = str(cell)
            cells.append(f" {cell_text:<{width}} ")
        return f"|{'|'.join(cells)}|"
    
    # ==================== 代码高亮 ====================
    
    def highlight_code(self, code: str, language: str = "python") -> str:
        """代码高亮（终端颜色）"""
        highlighted = code
        
        # 基础转义
        highlighted = highlighted.replace('&', '&amp;')
        highlighted = highlighted.replace('<', '&lt;')
        highlighted = highlighted.replace('>', '&gt;')
        
        # 关键词高亮
        keywords = self.code_keywords.get(language.lower(), [])
        for keyword in keywords:
            pattern = r'\b(' + re.escape(keyword) + r')\b'
            highlighted = re.sub(pattern, 
                               f'{self.CODE_THEME["keyword"]}\\1{self.CODE_THEME["reset"]}',
                               highlighted)
        
        # 字符串高亮
        string_patterns = [
            r'"([^"\\]|\\.)*"',  # 双引号字符串
            r"'([^'\\]|\\.)*'",  # 单引号字符串
            r'`([^`\\]|\\.)*`',  # 反引号字符串
        ]
        for pattern in string_patterns:
            highlighted = re.sub(pattern, 
                               f'{self.CODE_THEME["string"]}\\g<0>{self.CODE_THEME["reset"]}',
                               highlighted)
        
        # 数字高亮
        highlighted = re.sub(r'\b(\d+\.?\d*)\b',
                           f'{self.CODE_THEME["number"]}\\1{self.CODE_THEME["reset"]}',
                           highlighted)
        
        # 注释高亮
        comment_patterns = {
            "python": r'#.*$',
            "javascript": r'//.*$|/\*[\s\S]*?\*/',
            "java": r'//.*$|/\*[\s\S]*?\*/',
        }
        pattern = comment_patterns.get(language.lower(), r'#.*$')
        highlighted = re.sub(pattern, 
                           f'{self.CODE_THEME["comment"]}\\g<0>{self.CODE_THEME["reset"]}',
                           highlighted, flags=re.MULTILINE)
        
        return highlighted
    
    def remove_ansi_codes(self, text: str) -> str:
        """移除ANSI转义码"""
        ansi_pattern = r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
        return re.sub(ansi_pattern, '', text)
    
    # ==================== 文档分析 ====================
    
    def analyze_document(self, text: str, format_type: FormatType = None) -> DocumentInfo:
        """分析文档结构"""
        info = DocumentInfo()
        info.format_type = format_type or self._detect_format(text)
        
        lines = text.split('\n')
        info.line_count = len(lines)
        info.char_count = len(text)
        
        # 统计词数
        words = re.findall(r'\b\w+\b', text)
        info.word_count = len(words)
        
        # 估计阅读时间（平均200词/分钟）
        info.reading_time = max(1, int(info.word_count / 200 * 60))
        
        # 提取标题
        title_match = re.search(r'^#{1}\s+(.+)$', text, re.MULTILINE)
        if title_match:
            info.title = title_match.group(1).strip()
        
        # 统计标题层级
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(heading_pattern, text, re.MULTILINE):
            level = len(match.group(1))
            heading_text = match.group(2)
            info.headings.append((level, heading_text))
        
        # 统计代码块
        info.code_blocks = len(re.findall(r'```[\s\S]*?```', text))
        
        # 统计表格
        info.tables = len(re.findall(r'\|[^\n]*\|', text))
        
        # 统计链接
        info.links = len(re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text))
        
        # 统计图片
        info.images = len(re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', text))
        
        return info
    
    def _detect_format(self, text: str) -> FormatType:
        """自动检测文档格式"""
        if re.search(r'<[a-z][^>]*>', text):
            return FormatType.HTML
        elif re.search(r'^#+|^[-*_]{3,}|`[^`]+`|\*\*[^*]+\*\*', text):
            return FormatType.MARKDOWN
        elif re.search(r'\.\.\s*$|^\s*[\w]+\s*::', text, re.MULTILINE):
            return FormatType.RST
        else:
            return FormatType.PLAINTEXT
    
    # ==================== 格式化优化 ====================
    
    def optimize_markdown(self, text: str, max_line_length: int = 80) -> str:
        """优化Markdown格式"""
        lines = text.split('\n')
        optimized = []
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过代码块和引用
            if stripped.startswith('```') or stripped.startswith('>') or stripped.startswith('    '):
                optimized.append(line)
                continue
            
            # 标题后添加空行
            if re.match(r'^#{1,6}\s+', stripped):
                optimized.append(line)
                if len(optimized) < len(lines):
                    next_line = lines[lines.index(line) + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        optimized.append('')
                continue
            
            # 列表项规范化
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                content = list_match.group(3)
                # 统一使用2空格缩进
                normalized_line = '  ' * (indent // 2) + marker + ' ' + content
                optimized.append(normalized_line)
                continue
            
            # 长文本换行（保留Markdown格式）
            if len(stripped) > max_line_length and '`' not in stripped[:20]:
                # 简单换行处理
                optimized.append(line)
            else:
                optimized.append(line)
        
        return '\n'.join(optimized)
    
    def beautify_whitespace(self, text: str) -> str:
        """美化空白字符"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        lines = text.split('\n')
        
        # 移除行尾空格
        lines = [line.rstrip() for line in lines]
        
        # 处理连续空行
        result = []
        empty_count = 0
        
        for line in lines:
            if not line.strip():
                empty_count += 1
                if empty_count <= 2:  # 最多保留2个空行
                    result.append('')
            else:
                empty_count = 0
                result.append(line)
        
        # 文件末尾最多保留一个空行
        while len(result) > 1 and not result[-1]:
            result.pop()
        
        return '\n'.join(result)
    
    def format_paragraph(self, text: str, width: int = 80, 
                        indent: str = "") -> str:
        """格式化段落"""
        # 移除多余空白
        text = ' '.join(text.split())
        
        if len(text) <= width:
            return indent + text
        
        # 简单换行
        words = text.split(' ')
        lines = []
        current_line = indent
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += ' ' + word if current_line != indent else word
            else:
                lines.append(current_line)
                current_line = indent + word
        
        if current_line:
            lines.append(current_line)
        
        return '\n'.join(lines)
    
    # ==================== 验证功能 ====================
    
    def validate_markdown(self, text: str) -> Tuple[bool, List[str]]:
        """验证Markdown格式"""
        issues = []
        
        # 检查标题层级跳跃
        headings = re.findall(r'^(#{1,6})\s+', text, re.MULTILINE)
        levels = [len(h) for h in headings]
        
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                issues.append(f"标题层级跳跃: 从H{levels[i-1]}跳到H{levels[i]}")
        
        # 检查代码块闭合
        code_opens = len(re.findall(r'^```', text, re.MULTILINE))
        if code_opens % 2 != 0:
            issues.append("存在未闭合的代码块")
        
        # 检查链接格式
        links = re.findall(r'\[([^\]]*)\]\(([^\)]*)\)', text)
        for link_text, url in links:
            if not url.startswith(('http://', 'https://', 'mailto:', '#', '/')):
                issues.append(f"链接URL格式可能不正确: {url}")
        
        # 检查图片Alt文本
        images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', text)
        for alt_text, url in images:
            if not alt_text.strip():
                issues.append("图片缺少Alt文本描述")
        
        return len(issues) == 0, issues
    
    # ==================== 工具方法 ====================
    
    def _escape_html(self, text: str) -> str:
        """HTML转义"""
        for char, entity in self.html_entities.items():
            text = text.replace(char, entity)
        return text
    
    def generate_document_hash(self, text: str) -> str:
        """生成文档哈希"""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    # ==================== 主接口 ====================
    
    def process(self, content: str, action: str = "format") -> Dict[str, Any]:
        """
        处理文档
        
        Args:
            content: 输入内容
            action: 操作类型
                - format: 格式化文档
                - convert: 格式转换
                - analyze: 分析文档
                - validate: 验证文档
                - highlight: 代码高亮
        """
        result = {
            "original_hash": self.generate_document_hash(content),
            "format": self._detect_format(content).value,
            "actions": [],
        }
        
        if action == "format":
            formatted = self.beautify_whitespace(content)
            result["content"] = formatted
            result["formatted_hash"] = self.generate_document_hash(formatted)
            result["actions"].append("beautify_whitespace")
            
            if self._detect_format(content) == FormatType.MARKDOWN:
                optimized = self.optimize_markdown(formatted)
                result["content"] = optimized
                result["actions"].append("optimize_markdown")
        
        elif action == "convert":
            source_format = self._detect_format(content)
            result["source_format"] = source_format.value
            
            if source_format == FormatType.MARKDOWN:
                result["html"] = self.markdown_to_html(content)
            elif source_format == FormatType.HTML:
                result["markdown"] = self.html_to_markdown(content)
        
        elif action == "analyze":
            info = self.analyze_document(content)
            result["info"] = {
                "title": info.title,
                "word_count": info.word_count,
                "char_count": info.char_count,
                "line_count": info.line_count,
                "headings": info.headings,
                "code_blocks": info.code_blocks,
                "tables": info.tables,
                "links": info.links,
                "reading_time_seconds": info.reading_time,
            }
        
        elif action == "validate":
            if self._detect_format(content) == FormatType.MARKDOWN:
                is_valid, issues = self.validate_markdown(content)
                result["is_valid"] = is_valid
                result["issues"] = issues
            else:
                result["is_valid"] = True
                result["issues"] = []
                result["message"] = "仅支持Markdown验证"
        
        elif action == "highlight":
            # 尝试提取代码块
            code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', content)
            if code_blocks:
                result["highlighted_blocks"] = []
                for lang, code in code_blocks:
                    highlighted = self.highlight_code(code, lang or "python")
                    result["highlighted_blocks"].append({
                        "language": lang or "python",
                        "highlighted": highlighted
                    })
        
        return result


# ==================== 演示 ====================

def demo():
    """演示"""
    formatter = SmartDocumentFormatter()
    
    print("=" * 60)
    print("智能文档格式化工具 - 演示")
    print("=" * 60)
    
    # 1. Markdown转HTML
    print("\n1. Markdown 转 HTML:")
    markdown_text = """# 标题1

这是一个**粗体**和*斜体*文本。

## 代码示例

```python
def hello():
    print("Hello, World!")
```

## 列表

- 项目1
- 项目2
- 项目3
"""
    
    html_result = formatter.markdown_to_html(markdown_text)
    print(html_result)
    
    # 2. 表格格式化
    print("\n\n2. 表格格式化:")
    table_data = [
        ["功能", "描述", "状态"],
        ["Markdown转HTML", "支持完整语法", "✅"],
        ["表格处理", "多种格式支持", "✅"],
        ["代码高亮", "多语言支持", "✅"],
    ]
    
    config = TableConfig(align=TextAlignment.CENTER)
    formatted_table = formatter.format_table(table_data, config)
    print(formatted_table)
    
    # 3. 文档分析
    print("\n\n3. 文档分析:")
    info = formatter.analyze_document(markdown_text)
    print(f"标题: {info.title}")
    print(f"词数: {info.word_count}")
    print(f"字符数: {info.char_count}")
    print(f"代码块数: {info.code_blocks}")
    print(f"预计阅读时间: {info.reading_time}秒")
    
    # 4. 格式验证
    print("\n\n4. 格式验证:")
    is_valid, issues = formatter.validate_markdown(markdown_text)
    print(f"验证通过: {is_valid}")
    if issues:
        print(f"问题: {issues}")
    
    # 5. 完整处理
    print("\n\n5. 完整处理示例:")
    result = formatter.process(markdown_text, action="format")
    print(f"原始哈希: {result['original_hash']}")
    print(f"格式化后哈希: {result['formatted_hash']}")
    print(f"执行操作: {result['actions']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
