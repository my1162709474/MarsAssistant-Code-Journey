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
