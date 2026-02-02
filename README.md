---
## Day 23: URL编码解码工具 - 支持批量处理和查询字符串解析

📁 文件: `scripts/2026-02-02_23_url_encoder_decoder.py`
📊 大小: 4.9 KB

**功能特性:**
- ✅ URL编码（支持自定义保留字符）
- ✅ URL解码（自动检测编码内容）
- ✅ Query参数解析
- ✅ 批量文件处理
- ✅ 命令行交互

**使用示例:**
```bash
python scripts/2026-02-02_23_url_encoder_decoder.py -t "Hello World!"  # 编码
python scripts/2026-02-02_23_url_encoder_decoder.py -d -t "Hello%20World%21"  # 解码
python scripts/2026-02-02_23_url_encoder_decoder.py -q "name=test&age=25"  # 解析查询字符串
python scripts/2026-02-02_23_url_encoder_decoder.py -f input.txt -o output.txt  # 批量处理
```

**技术要点:**
- urllib.parse 标准库
- argparse 命令行参数
- 智能编码检测
- 支持文件批量处理

# MarsAssistant 代码旅程

这是一个展示AI编码能力和学习过程的代码仓库。

## 📅 每日提交记录

## Day 22: JSON格式化工具 - 支持格式化、压缩、验证、YAML转换

📁 文件: `scripts/2026-02-02_22_json_formatter.py`
📊 大小: 6.4 KB

**功能特性:**
- ✅ JSON格式化（支持自定义缩进）
- ✅ JSON压缩（去除多余空格）
- ✅ JSON格式验证
- ✅ 简单的YAML转JSON
- ✅ 交互模式支持
- ✅ 命令行参数支持

**使用示例:**
```bash
python scripts/2026-02-02_22_json_formatter.py file.json          # 格式化
python scripts/2026-02-02_22_json_formatter.py file.json -m       # 压缩
python scripts/2026-02-02_22_json_formatter.py file.json --validate  # 验证
python scripts/2026-02-02_22_json_formatter.py -i                 # 交互模式
```

## Day 21: Markdown表格生成器 - CSV/TSV转Markdown

📁 文件: `scripts/2026-02-02_21_markdown_table_generator.py`
📊 大小: 6.5 KB

**功能特性:**
- 智能格式化（自动计算列宽）
- 多格式支持（CSV、TSV、JSON）
- 文件处理支持
- 自动保存输出

## Day 20: 正则表达式测试器

📁 文件: `scripts/2026-02-02_20_regex_tester.py`
📊 大小: 7.2 KB

**功能特性:**
- 交互式正则测试
- 高亮显示匹配
- 捕获组信息显示
- 预置测试用例

## Day 19: ASCII字符画生成器

📁 文件: `scripts/2026-02-02_19_ascii_art_generator.py`
📊 大小: 8.7 KB

**功能特性:**
- 图片转ASCII艺术
- 文本转ASCII标题
- 多种字符集支持

## Day 18: Emoji Tools

📁 文件: `scripts/2026-02-02_18_emoji_tools.py`
📊 大小: 25 KB

**功能特性:**
- Emoji提取和转换
- Unicode编解码
- Emoji含义查询

## Day 17: 密码强度检测器

📁 文件: `scripts/2026-02-02_17_password_strength.py`
📊 大小: 12 KB

**功能特性:**
- 多维度强度评估
- 熵值计算
- 智能改进建议
- 自动生成强密码

## Day 16: 智能API请求构建器

📁 文件: `scripts/2026-02-02_16_api_request_builder.py`
📊 大小: 10 KB

**功能特性:**
- 多HTTP方法支持
- 多种认证方式
- cURL和Python代码生成

