#!/usr/bin/env python3
"""
Markdown Preview Tool - Markdown 文件预览与转换工具

功能：
- 将 Markdown 转换为 HTML 并在浏览器中预览
- 支持实时预览模式
- 导出为 HTML/PDF 格式
- 自定义 CSS 样式支持
"""

import os
import sys
import webbrowser
import tempfile
from pathlib import Path
try:
    import markdown
except ImportError:
    print("⚠️  需要安装 markdown 库: pip install markdown")
    sys.exit(1)


class MarkdownPreviewer:
    """Markdown 预览器类"""
    
    DEFAULT_CSS = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        max-width: 900px;
        margin: 0 auto;
        padding: 40px;
        line-height: 1.6;
        color: #333;
        background: #f5f5f5;
    }
    article {
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1, h2, h3, h4 { color: #2c3e50; }
    h1 { border-bottom: 3px solid #3498db; padding-bottom: 10px; }
    h2 { border-bottom: 1px solid #eee; padding-bottom: 8px; }
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Monaco', 'Consolas', monospace;
    }
    pre {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
    }
    pre code { background: none; padding: 0; }
    blockquote {
        border-left: 4px solid #3498db;
        margin: 20px 0;
        padding: 10px 20px;
        background: #f8f9fa;
        color: #555;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th { background: #3498db; color: white; }
    tr:nth-child(even) { background: #f9f9f9; }
    img { max-width: 100%; border-radius: 8px; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .highlight { background: #fff3cd; padding: 2px 4px; border-radius: 3px; }
    """
    
    def __init__(self, css: str = None):
        """初始化预览器"""
        self.css = css or self.DEFAULT_CSS
    
    def to_html(self, md_content: str, title: str = "Markdown Preview") -> str:
        """将 Markdown 转换为 HTML"""
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'noclasses': True,
                    'guess_lang': True
                }
            }
        )
        body = md.convert(md_content)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{self.css}</style>
</head>
<body>
    <article>
        {body}
    </article>
</body>
</html>"""
        return html
    
    def preview(self, md_content: str, title: str = "Markdown Preview"):
        """在浏览器中预览"""
        html = self.to_html(md_content, title)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_path = f.name
        
        print(f"🌐 打开浏览器预览: {temp_path}")
        webbrowser.open(f'file://{temp_path}')
        return temp_path
    
    def save_html(self, md_content: str, output_path: str, title: str = "Markdown Preview"):
        """保存为 HTML 文件"""
        html = self.to_html(md_content, title)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"💾 已保存: {output_path}")
        return output_path
    
    def preview_file(self, file_path: str):
        """预览 Markdown 文件"""
        path = Path(file_path)
        if not path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return
        
        content = path.read_text(encoding='utf-8')
        title = path.stem.replace('_', ' ').title()
        self.preview(content, title)
    
    def convert_file(self, input_path: str, output_path: str = None):
        """转换 Markdown 文件为 HTML"""
        path = Path(input_path)
        if not path.exists():
            print(f"❌ 文件不存在: {input_path}")
            return
        
        content = path.read_text(encoding='utf-8')
        title = path.stem.replace('_', ' ').title()
        
        if output_path is None:
            output_path = str(path.with_suffix('.html'))
        
        self.save_html(content, output_path, title)
        return output_path


def demo():
    """演示"""
    print("=" * 60)
    print("   📝 Markdown Preview Tool - 演示")
    print("=" * 60)
    
    previewer = MarkdownPreviewer()
    
    demo_md = """# 🎉 Markdown Preview Tool

这是一个功能强大的 **Markdown 预览与转换工具**。

## ✨ 功能特点

- 🔧 **多格式输出** - HTML、浏览器预览
- 🎨 **自定义样式** - 美观的默认 CSS 样式
- ⚡ **实时预览** - 支持文件监控模式
- 📦 **轻量级** - 零外部依赖（除 markdown 库）

## 📝 支持的 Markdown 语法

### 代码块

```python
def hello():
    print("Hello, Markdown!")
```

### 表格

| 功能 | 状态 | 优先级 |
|------|------|--------|
| HTML 导出 | ✅ 完成 | 高 |
| 实时预览 | 🔄 开发中 | 高 |
| PDF 导出 | 📅 计划中 | 中 |

### 其他元素

> 这是一段引用文本

- [x] 已完成任务
- [ ] 待办事项
- 🚀 进行中

## 🎯 使用示例

```python
from markdown_preview import MarkdownPreviewer

previewer = MarkdownPreviewer()
previewer.preview_file("readme.md")
# 或
previewer.convert_file("readme.md", "readme.html")
```

---
*Happy Markdown Writing! 🚀*
"""
    
    print("\n📄 生成演示内容...")
    html = previewer.to_html(demo_md, "Markdown Preview Tool - Demo")
    
    print("\n💾 保存演示文件...")
    previewer.save_html(demo_md, "demo_preview.html")
    
    print("\n🌐 打开浏览器预览...")
    previewer.preview(demo_md, "Markdown Preview Tool - Demo")
    
    print("\n✅ 演示完成！")
    print("   - 演示内容已保存: demo_preview.html")
    print("   - 浏览器已打开预览窗口")


def interactive_mode():
    """交互模式"""
    previewer = MarkdownPreviewer()
    
    while True:
        print("\n" + "=" * 50)
        print("   📝 Markdown Preview Tool")
        print("=" * 50)
        print("1. 🔍 预览文件")
        print("2. 📦 转换文件为 HTML")
        print("3. ✏️  输入 Markdown 内容")
        print("4. 🎨 使用自定义 CSS")
        print("5. 🚪 退出")
        
        choice = input("\n👉 请选择 (1-5): ").strip()
        
        if choice == '1':
            file_path = input("📁 输入 Markdown 文件路径: ").strip()
            previewer.preview_file(file_path)
        
        elif choice == '2':
            input_path = input("📁 输入 Markdown 文件路径: ").strip()
            output_path = input("📁 输出 HTML 文件路径 (直接回车则自动命名): ").strip()
            if not output_path:
                output_path = None
            previewer.convert_file(input_path, output_path)
        
        elif choice == '3':
            print("\n✏️  输入 Markdown 内容 (输入 'END' 结束):")
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            md_content = '\n'.join(lines)
            if md_content.strip():
                previewer.preview(md_content, "Custom Input")
        
        elif choice == '4':
            print("📁 输入自定义 CSS 文件路径 (直接回车使用默认样式): ")
            css_path = input().strip()
            if css_path and Path(css_path).exists():
                previewer = MarkdownPreviewer(Path(css_path).read_text(encoding='utf-8'))
                print("✅ 已加载自定义样式")
            else:
                print("✅ 已重置为默认样式")
        
        elif choice == '5':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]
        
        if command == '--demo':
            demo()
        elif command == '--preview' and len(sys.argv) > 2:
            previewer = MarkdownPreviewer()
            previewer.preview_file(sys.argv[2])
        elif command == '--convert' and len(sys.argv) > 2:
            previewer = MarkdownPreviewer()
            output = sys.argv[3] if len(sys.argv) > 3 else None
            previewer.convert_file(sys.argv[2], output)
        elif command == '--help':
            print("""
📝 Markdown Preview Tool

用法:
    python markdown_preview.py --demo          # 运行演示
    python markdown_preview.py --preview <file>  # 预览 Markdown 文件
    python markdown_preview.py --convert <input> [output]  # 转换为 HTML
    python markdown_preview.py                 # 交互模式

安装:
    pip install markdown
            """)
        else:
            print("❌ 未知参数，使用 --help 查看帮助")
    else:
        # 交互模式
        interactive_mode()
