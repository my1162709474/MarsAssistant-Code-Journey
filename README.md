这是一个实用的密码强度检测工具

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

## Day 20: 文件压缩解压工具

📁 **文件**: `scripts/2026-02-02_020_file_compressor.py`  
📝 **功能**: 支持ZIP/TAR.GZ/GZIP格式的压缩与解压工具

### ✨ 功能特性
- **ZIP格式**: 标准ZIP压缩，支持密码保护
- **TAR.GZ格式**: GNU zip压缩的tar归档  
- **GZIP格式**: 单文件gzip压缩
- **实用功能**: 压缩、解压、列出内容、查看信息

### 💻 使用示例
```bash
# 压缩文件夹为ZIP
python file_compressor.py compress ./my_folder -o backup.zip

# 解压ZIP文件
python file_compressor.py extract backup.zip

# 列出ZIP内容
python file_compressor.py list backup.zip
```
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

---

## Day 20: 正则表达式测试器

📁 **文件**: `scripts/2026-02-02_020_regex_tester.py`  
📝 **功能**: 交互式正则表达式测试工具，支持高亮显示匹配结果和模式解释

### ✨ 功能特性
- **交互测试**: 实时测试正则表达式匹配
- **高亮显示**: 用 🔶 标记匹配文本
- **捕获组信息**: 显示所有捕获组和命名组
- **批量测试**: 支持一次性测试多个字符串
- **模式解释**: 解释常见正则模式含义
- **预置用例**: 包含邮箱、手机号、URL等常用测试用例

### 💻 使用示例
```bash
# 交互模式
python regex_tester.py

# 快速测试
python regex_tester.py "\d+" "测试123文本456"

# 批量测试
python regex_tester.py --batch "^\w+@\w+\.\w+$" "test@example.com" "invalid"
```

### 🎨 交互示例
```
请输入正则表达式: \d+
请输入测试文本: 包含123数字456

==================================================
✅ 匹配成功!
📍 位置: 4 - 7
📝 匹配文本: '123'

🔢 捕获组 (0个):

🎨 高亮结果:
   包含🔶123🔶数字456
```

---

## Day 21: Markdown表格生成器 🛠️

🤖 **创建者**: OpenClaw

**文件**: `scripts/2026-02-02_021_markdown_table_generator.py`

**功能亮点**:
- 支持CSV和TSV格式输入
- 自动计算列宽并格式化
- 生成标准Markdown表格
- 支持命令行参数和文件输入
- 自动保存输出到文件

**使用示例**:
```python
# 命令行使用
python markdown_table_generator.py data.csv
python markdown_table_generator.py data.tsv --tsv

# 直接输入数据
python markdown_table_generator.py 'a,b,c\n1,2,3'
```

**输出示例**:
```markdown
| name   | age | city    |
|--------|-----|---------|
| Alice  | 25  | NewYork |
| Bob    | 30  | London  |
```

