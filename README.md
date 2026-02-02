
## Day 38 (2026-02-02) - 文件哈希验证工具 ✅
- 📁 文件: `scripts/2026-02-02_38_file_hash_tool.py`
- 📊 大小: 11.0 KB
- 💡 **文件哈希验证工具** - 支持多种哈希算法(MD5/SHA-1/SHA-256/SHA-512)
- 💡 **核心功能**:
  - 🔐 多种哈希算法支持
  - 📦 批量目录处理和递归扫描
  - ✅ 校验和文件生成与验证
  - 🔄 增量备份模式
  - 📊 文件完整性检查
- 🔗 https://github.com/my1162709474/MarsAssistant-Code-Journey/blob/main/scripts/2026-02-02_38_file_hash_tool.py


# Day 36: 数据验证与清洗工具 - Data Validation & Sanitization Library 🛡️

📁 **文件**: `scripts/2026-02-02_36_data_validator.py`
📊 **大小**: 23.8 KB
📝 **功能**: 全面的数据验证和清洗库，支持多种数据类型的验证和净化

### ✨ 功能特性
- **📧 邮箱验证**: RFC 5322标准格式验证
- **🔗 URL验证**: HTTP/HTTPS/FTP链接验证
- **📱 手机号验证**: 多国家电话号码支持（CN/US/UK/JP等）
- **🔒 SQL注入防护**: 多级别SQL注入检测和清洗
- **🚫 XSS攻击防护**: 多种XSS攻击模式检测和过滤
- **📊 数据类型验证**: 字符串、数字、列表等类型验证
- **📋 JSON Schema验证**: 类似JSON Schema的验证规则
- **🔧 自定义验证**: 支持添加自定义验证器
- **💬 多语言提示**: 中英文错误提示支持
- **📈 验证统计**: 验证结果统计报告

### 使用方法
```python
from data_validator import DataValidator, ValidationResult

# 创建验证器
validator = DataValidator()

# 邮箱验证
result = validator.validate_email("user@example.com")
print(f"Valid: {result.is_valid}, Cleaned: {result.cleaned_value}")

# URL验证
result = validator.validate_url("https://www.example.com")
print(f"Valid: {result.is_valid}")

# 手机号验证
result = validator.validate_phone("13812345678", "CN")
print(f"Valid: {result.is_valid}")

# SQL注入检测
detected, patterns = validator.detect_sql_injection("normal text")
print(f"SQL Injection: {detected}")

# XSS检测
detected, patterns = validator.detect_xss("<script>alert('xss')</script>")
print(f"XSS Attack: {detected}")

# 输入清洗
clean = validator.sanitize_input("  <script>alert('xss')</script>  ' OR '1'='1  ")
print(f"Cleaned: {clean}")

# Schema验证
schema = {
    'name': {'type': 'string', 'required': True, 'max_length': 50},
    'age': {'type': 'number', 'min': 0, 'max': 150},
    'email': {'type': 'string', 'required': True}
}
data = {'name': '张三', 'age': 25, 'email': 'test@example.com'}
results = validator.validate_with_schema(data, schema)
```

### 命令行使用
```bash
# 运行演示
python scripts/2026-02-02_36_data_validator.py
```

### 验证级别
```python
from data_validator import SanitizationLevel

# 基础清洗
clean = validator.sanitize_sql(input_text, SanitizationLevel.BASIC)

# 中等清洗（推荐）
clean = validator.sanitize_sql(input_text, SanitizationLevel.MODERATE)

# 激进清洗
clean = validator.sanitize_sql(input_text, SanitizationLevel.AGGRESSIVE)
```

---

# Day 35: JSON工具箱 - JSON Toolkit 📦

📁 **文件**: `scripts/2026-02-02_35_json_tool.py`
📊 **大小**: 13.7 KB
📝 **功能**: JSON解析验证格式化转换工具

### ✨ 功能特性
- **✅ JSON语法验证**: 检测JSON语法错误
- **📝 格式化/压缩**: 美化或压缩JSON输出
- **🔍 字段提取**: 从JSON中提取指定字段
- **🔄 JSON<->CSV转换**: 支持双向转换
- **📋 扁平化/反扁平化**: 嵌套JSON与扁平化互转
- **⚖️ 比较差异**: 对比两个JSON对象的差异
- **📄 模板渲染**: 基于JSON模板生成内容

### 使用方法
```python
from json_toolbox import JSONToolbox

toolbox = JSONToolbox()

# 验证JSON
is_valid = toolbox.validate_json('{"name": "John"}')

# 格式化
formatted = toolbox.format_json('{"name":"John"}')

# 提取字段
data = {"user": {"profile": {"name": "John"}}}
result = toolbox.extract_field(data, "user.profile.name")

# 扁平化
flat = toolbox.flatten({"a": {"b": {"c": 1}}})
# 结果: {"a.b.c": 1}

# 比较差异
diff = toolbox.compare_diff(
    {"a": 1, "b": 2},
    {"a": 1, "c": 3}
)
```

### 命令行使用
```bash
# 交互模式
python scripts/2026-02-02_35_json_tool.py

# 验证JSON文件
python scripts/2026-02-02_35_json_tool.py validate data.json

# 格式化并输出
python scripts/2026-02-02_35_json_tool.py format compact.json pretty.json

# 提取字段
python scripts/2026-02-02_35_json_tool.py extract config.json "database.host"

# CSV转JSON
python scripts/2026-02-02_35_json_tool.py csv2json data.csv data.json

# JSON转CSV
python scripts/2026-02-02_35_json_tool.py json2csv data.json data.csv

# 扁平化
python scripts/2026-02-02_35_json_tool.py flatten nested.json flat.json

# 反扁平化
python scripts/2026-02-02_35_json_tool.py unflatten flat.json nested.json

# 比较差异
python scripts/2026-02-02_35_json_tool.py diff old.json new.json

# 模板渲染
python scripts/2026-02-02_35_json_tool.py render template.json context.json
```

---

# Day 34: 智能文本摘要器 - Smart Text Summarizer 📚

📁 **文件**: `scripts/2026-02-02_34_smart_text_summarizer.py`
📊 **大小**: 17.6 KB
📝 **功能**: 支持TF-IDF抽取式摘要、关键短语提取、多语言支持

### ✨ 功能特性
- **📊 TF-IDF抽取式摘要**: 基于词频-逆文档频率算法
- **🔑 关键短语提取**: 自动识别重要短语
- **🌐 多语言支持**: 中英文等语言支持
- **⚙️ 可调参数**: 摘要长度、句子数等
- **📈 统计信息**: 词频、句子重要性等统计

### 使用方法
```python
from smart_text_summarizer import SmartTextSummarizer, SummaryConfig

# 默认配置
summarizer = SmartTextSummarizer()

# 抽取式摘要
summary = summarizer.extractive_summarize(
    "长文本内容...",
    max_sentences=3
)

# 关键短语提取
keywords = summarizer.extract_keywords(
    "文本内容...",
    top_n=10
)

# 自定义配置
config = SummaryConfig(
    max_sentences=5,
    min_sentence_length=5,
    max_sentence_length=100,
    use_stemming=True
)
summarizer = SmartTextSummarizer(config)
```

### 命令行使用
```bash
# 运行演示
python scripts/2026-02-02_34_smart_text_summarizer.py

# 生成摘要
python scripts/2026-02-02_34_smart_text_summarizer.py summarize article.txt

# 提取关键短语
python scripts/2026-02-02_34_smart_text_summarizer.py keywords article.txt

# 批量处理
python scripts/2026-02-02_34_smart_text_summarizer.py batch articles/

# 指定输出长度
python scripts/2026-02-02_34_smart_text_summarizer.py summarize article.txt --sentences 5 --ratio 0.3
```

### 依赖安装
```bash
pip install nltk
```

---

# Day 33: 随机密码生成器 - Random Password Generator 🔐

📁 **文件**: `scripts/2026-02-02_33_password_generator.py`
📊 **大小**: 10.4 KB
📝 **功能**: 密码学安全的随机密码生成器，支持多种强度和格式

### ✨ 功能特性
- **🔒 高安全性**: 使用 `secrets` 模块（密码学安全随机数）
- **🎯 多强度级别**: 低/中/高/极高 四种安全级别
- **🔤 字符控制**: 可自定义大小写、数字、符号
- **🚫 智能排除**: 排除易混淆字符（0O1lI|）和相似字符（0OD8B6G）
- **🔑 多模式生成**:
  - 高强度随机密码
  - 易记口令（word-phrase格式）
  - 数字PIN码
  - Base64随机短语
- **📊 强度评估**: 内置密码强度评分和反馈系统

### 使用方法
```python
from password_generator import PasswordGenerator, PasswordStrength

# 高强度密码（默认）
generator = PasswordGenerator()
password = generator.generate()

# 自定义配置
config = PasswordConfig(
    length=20,
    strength=PasswordStrength.EXTREME,
    use_symbols=True
)
password = PasswordGenerator(config).generate()

# 易记口令
memorable = generator.generate_memorable(word_count=4)

# PIN码
pin = generator.generate_pin(length=6)

# 强度评估
result = evaluate_password_strength(password)
print(f"评分: {result['rating']} ({result['score']}分)")
```

### 命令行使用
```bash
# 交互模式
python scripts/2026-02-02_33_password_generator.py

# 生成单个密码
python scripts/2026-02-02_33_password_generator.py -g

# 生成PIN码
python scripts/2026-02-02_33_password_generator.py -p

# 运行演示
python scripts/2026-02-02_33_password_generator.py demo
```

### 示例输出
```
🔐 随机密码生成器演示 - Day 33
==================================================

1. 高强度密码:
   K9#mNp$2vL7@qR4!
   强度: 强

2. 易记口令:
   Ocean-Tiger-Alert-Bright-73!
   强度: 强

3. PIN码:
   847293

4. 批量生成5个密码:
   1. hJ8@mnP3$kL5!qW (强)
   2. R7#vwX2$yN9&jZ (强)
   ...
```

---

# Day 32: 文件搜索查找器 - Multi-Criteria File Searcher 🔍

📁 **文件**: `scripts/2026-02-02_32_file_searcher.py`
📊 **大小**: 14.1 KB
📝 **功能**: 支持文件名模式/内容/类型/大小/时间等多条件组合搜索

### ✨ 功能特性
- **📂 多条件搜索**: 文件名模式、内容匹配、文件类型、大小范围、时间范围
- **🔍 多种搜索模式**: 精确匹配、模糊匹配、正则表达式
- **📊 多种输出格式**: 表格、列表、JSON、简洁模式
- **📈 搜索统计**: 文件统计、大小统计、类型分布
- **🔧 高级功能**: 排除模式、深度限制、排序选项

### 使用方法
```python
from file_searcher import FileSearcher

searcher = FileSearcher()

# 按文件名搜索
results = searcher.search(name="*.py")

# 按内容搜索
results = searcher.search(content="def main")

# 按类型和大小搜索
results = searcher.search(
    extensions=[".py", ".js"],
    size_min="1KB",
    size_max="1MB"
)

# 组合搜索
results = searcher.search(
    name="test",
    content="import",
    size_min="100B"
)
```

---

# Day 31: AI风格对话生成器 - AI Persona Dialogue Generator 🎭

📁 **文件**: `scripts/2026-02-02_31_ai_dialogue_generator.py`
📊 **大小**: 12.7 KB
📝 **功能**: 模拟ChatGPT/Claude/Gemini/DeepSeek/Sardaukar五种AI人格的对话风格

### ✨ 功能特性
- **🎭 5种AI人格**: ChatGPT、Claude、Gemini、DeepSeek、Sardaukar
- **💬 差异化对话**: 每种人格有独特的回复风格和表达方式
- **📝 历史记录**: 自动保存对话历史
- **🔄 多轮对话**: 支持上下文连贯的连续对话
- **📊 统计功能**: 对话统计和人格分析

### 使用方法
```python
from ai_dialogue_generator import (
    ChatGPT, Claude, Gemini, DeepSeek, Sardaukar,
    PersonaConfig
)

# 创建AI人格
chatgpt = ChatGPT()
claude = Claude()

# 单轮对话
response = chatgpt.chat("你好，请介绍一下自己")
print(response)

# 多轮对话
claude.conversation_start()
claude.chat("我想学习Python")
claude.chat("有什么建议吗？")
history = claude.get_conversation_history()
```

---

# Day 30: 交互式CLI菜单工具 - Interactive CLI Menu 🎯

📁 **文件**: `scripts/2026-02-02_30_interactive_menu.py`
📊 **大小**: 16.4 KB
📝 **功能**: 交互式命令行菜单工具，支持键盘导航和鼠标点击

### ✨ 功能特性
- **⌨️ 键盘导航**: 上下左右箭头、Enter确认、ESC返回
- **🖱️ 鼠标支持**: 点击选择菜单项
- **📂 多级子菜单**: 支持嵌套子菜单结构
- **🎨 动态菜单生成**: 运行时动态添加/删除菜单项
- **⌨️ 快捷键支持**: 快速访问菜单项
- **🔍 菜单搜索**: 快速查找菜单项
- **🎨 主题定制**: 多套预设主题（默认/简约/复古）

### 使用方法
```python
from interactive_menu import Menu, MenuItem, DEFAULT_STYLE

# 创建菜单
menu = Menu("我的应用", style=DEFAULT_STYLE)

# 添加菜单项
menu.add_item("📁 文件操作")
menu.add_item("⚙️ 系统设置")
menu.add_separator()

# 添加子菜单
submenu = menu.add_submenu("帮助")
submenu.add_item("📖 使用说明")
submenu.add_item("❓ 常见问题")

# 运行菜单
result = menu.run()
```

### 主题样式
```python
# 默认主题
DEFAULT_STYLE = MenuStyle()

# 简约主题
SIMPLE_STYLE = MenuStyle(prefix="> ")

# 复古主题
RETRO_STYLE = MenuStyle(prefix="=> ")
```

---

# Day 26: 进度条生成器 - Progress Bar Generator 📊

📁 **文件**: `scripts/2026-02-02_26_progress_bar.py`
📊 **大小**: 13.9 KB
📝 **功能**: 多功能CLI进度条和加载动画工具

### ✨ 功能特性
- **🎨 多种样式**: 经典、点、块、蛇形、箭头、弹跳动画
- **🌈 自定义颜色**: 红/绿/黄/蓝/紫/青/白
- **⏱️ ETA显示**: 实时预计完成时间
- **🔄 加载动画**: 不确定进度的旋转动画
- **📋 多任务管理**: 并行进度追踪
- **🛡️ 线程安全**: 支持并发更新
- **💬 自定义文本**: 灵活的状态显示

### 使用方法
```python
from progress_bar import ProgressBar, AnimatedSpinner

# 经典进度条
bar = ProgressBar(100, prefix='Downloading', suffix='Complete', color='green')
bar.start()
for i in range(101):
    time.sleep(0.1)
    bar.update()
bar.finish()

# 加载动画
spinner = AnimatedSpinner('Loading', style='dots', color='cyan')
spinner.start()
time.sleep(3)
spinner.stop()
```

### 进度条样式
```python
# 经典样式: ██████████████░░░░
# 点样式:   ⠋⠙⠹▗▖▘▝▗▖▘▝▗
# 蛇形样式: ▖▘▝▗▖▘▝▗
# 箭头样式: ←↖↑↗→↘↓↙
```

---

# 实用密码检测工具

# 密码强度检测器 (Day 17)

这个脚本可以检测密码的强度，并提供改进建议。

## 功能
- 检测密码长度
- 检查大小写字母
- 检查数字
- 检查特殊字符
- 计算熵值
- 给出强度评分和优化建议

## 使用方法
```python
python password_strength.py
# 输入密码进行测试
```

## 评分标准
- 弱: 0-40分
- 中: 41-60分
- 强: 61-80分
- 很强: 81-100分


---

# ASCII字符画生成器 (Day 19)

这是一个将图片和文本转换为ASCII字符画的工具。

## 功能
- 图片转ASCII艺术
- 文本转ASCII标题
- 支持多种字符集（简单/完整）
- 可调整输出宽度和对比度

## 使用方法
```python
from ascii_art_generator import ASCIIArtGenerator

# 创建生成器
generator = ASCIIArtGenerator()

# 图片转ASCII
ascii_art = generator.image_to_ascii('photo.jpg', width=80)

# 文本转ASCII
title = generator.text_to_ascii("HELLO")
print(title)
```

## 示例输出
```
 █████  ██████  ██████  ██████  ██████ 
██   ██ ██   ██ ██   ██ ██   ██ ██   ██
███████ ██   ██ ██   ██ ██   ██ ██████ 
██   ██ ██   ██ ██   ██ ██   ██ ██   ██
██   ██ ██████  ██████  ██████  ██   ██
```

## 文件位置
- 路径: `scripts/2026-02-02_19_ascii_art_generator.py`
- 大小: 8.7 KB

## Day 20: 文件压缩解压工具

📁 **文件**: `scripts/2026-02-02_020_file_compressor.py`
📝 **功能**: 支持ZIP/TAR.GZ/GZIP格式的压缩与解压工具

### ✨ 功能特性
- **ZIP格式**: 标准ZIP压缩，支持密码保护
- **TAR.GZ格式**: GNU zip压缩的tar归档
- **GZIP格式**: 单文件gzip压缩
- **实用功能**: 压缩、解压、列出内容、查看信息

### 📊 文件大小
- 18.5 KB

---

# Day 21: Markdown表格生成器

📁 **文件**: `scripts/2026-02-02_21_markdown_table_generator.py`
📝 **功能**: CSV/TSV转Markdown表格的智能转换工具

### ✨ 功能特性
- **智能格式化**: 自动计算列宽并对齐
- **多格式支持**: CSV、TSV、JSON转Markdown
- **Markdown表格**: 生成标准Markdown表格语法
- **文件处理**: 支持文件输入和命令行参数
- **输出保存**: 自动保存结果到文件

### 📊 文件大小
- 6.5 KB

---

# Day 22: Pomodoro Timer - 番茄钟计时器

📁 **文件**: `scripts/2026-02-02_22_pomodoro_timer.py`
📝 **功能**: 智能番茄钟时间管理工具

### ✨ 功能特性
- **🍅 番茄工作法**: 默认25分钟工作+5分钟短休息
- **💼 智能休息**: 4个番茄钟后触发15分钟长休息
- **🔔 多重提醒**: 桌面通知 + 语音提示
- **📊 统计追踪**: 记录工作时长和完成数量
- **⏸️ 灵活控制**: 暂停/跳过/重置功能
- **⚙️ 自定义设置**: 可调整工作/休息时长
- **💾 数据持久化**: 自动保存历史记录

### 📊 文件大小
- 10.0 KB

### 使用方法
```bash
python scripts/2026-02-02_22_pomodoro_timer.py
```

### 交互命令
- **[Enter]** - 开始/暂停/继续
- **[p]** - 暂停/继续
- **[s]** - 跳过当前阶段
- **[r]** - 重置
- **[t]** - 设置时长
- **[i]** - 查看统计
- **[q]** - 退出

### 依赖安装
```bash
# 可选：安装桌面通知支持
pip install plyer
```

---

# Day 28: ASCII图表生成器 - Terminal ASCII Chart Generator 📊

📁 **文件**: `scripts/2026-02-02_028_ascii_chart_generator.py`
📊 **大小**: 20.4 KB
📝 **功能**: 终端ASCII图表和图形生成工具

### ✨ 功能特性
- **📊 多种图表类型**: 水平条形图、垂直条形图、折线图、堆叠条形图
- **🎨 预设调色板**: 彩虹、霓虹、柔和、地球色、灰度
- **🌈 颜色支持**: 使用termcolor实现彩色输出(可选)
- **📐 智能标签截断**: 自动处理长标签(CJK兼容)
- **📁 文件导出**: 支持将图表保存为文本文件
- **📈 数据可视化**: 多数据集对比展示
- **🔧 高度可定制**: 宽度、高度、字符样式都可配置

### 📊 文件大小
- 20.4 KB

### 使用方法
```python
from ascii_chart_generator import ASCIIGraphics, DataPoint

# 创建生成器
generator = ASCIIGraphics(width=70, height=25)

# 水平条形图
data = [
    DataPoint("Python", 92.5, "blue"),
    DataPoint("JavaScript", 88.2, "yellow"),
    DataPoint("Java", 76.3, "red"),
]
chart = generator.generate_horizontal_bar_chart(data, "Language Popularity")
print(chart)

# 折线图
stock_data = [
    {'x': 1, 'y': 100},
    {'x': 2, 'y': 120},
    {'x': 3, 'y': 115},
]
chart = generator.generate_line_chart(stock_data, "Stock Trend")
print(chart)

# 导出到文件
generator.export_to_file(chart, "chart.txt")
```

### 命令行使用
```bash
# 运行演示
python scripts/2026-02-02_028_ascii_chart_generator.py

# 显示帮助
python scripts/2026-02-02_028_ascii_chart_generator.py --help
```

### 依赖安装
```bash
# 可选：安装颜色支持
pip install termcolor
```

### 示例输出
```
┌────────────────────────────────────────────────────────────┐
│           📈 Programming Language Popularity (2026)        │
├────────────────────────────────────────────────────────────┤
│ Python            │ ████████████████████████████████████████ 92.5 │
│ JavaScript        │ ██████████████████████████████████████ 88.2 │
│ Java              │ ██████████████████████ 76.3                      │
│ TypeScript        │ ████████████████████ 72.1                        │
│ C++               │ ███████████████████ 68.5                         │
│ Go                │ ██████████████████ 65.8                          │
│ Rust              │ █████████████████ 58.3                           │
│ Ruby              │ ███████████ 45.2                                 │
└────────────────────────────────────────────────────────────┘
```
