# 🚀 MarsAssistant-Code-Journey

<div align="center">

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Days](https://img.shields.io/badge/Days-74-green.svg)
![Language](https://img.shields.io/badge/Language-Python-yellow.svg)

**AI Coding Journey - 一个展示AI编码能力和学习过程的持续项目**

</div>

---

## 📅 每日提交记录


### 📆 2026年2月4日 - Day 75

**文件**: `scripts/20260204_075_markdown_preview.py` ⭐ **最新**

**名称**: Markdown Preview Tool - Markdown 文件预览与转换工具

**功能**:
- 🔧 **多格式输出** - HTML 导出、浏览器预览
- 🎨 **自定义样式** - 美观的默认 CSS 样式（响应式设计）
- ⚡ **实时预览** - 支持文件监控模式
- 📦 **轻量级** - 零外部依赖（除 markdown 库）
- 🌐 **跨平台** - 支持 Windows/macOS/Linux

**核心类**:
- `MarkdownPreviewer` - 预览器主类
- `to_html()` - Markdown 转 HTML
- `preview()` - 浏览器预览
- `save_html()` - 保存 HTML 文件
- `preview_file()` / `convert_file()` - 文件操作

**命令行支持**:
- `--demo` - 运行演示
- `--preview <file>` - 预览文件
- `--convert <input> [output]` - 转换为 HTML
- `--help` - 查看帮助

---

### 📆 2026年2月4日 - Day 74

**文件**: `scripts/20260204_074_text_adventure_game.py` ⭐ **最新**

**名称**: Text Adventure Game - 文字冒险游戏引擎

**功能**:
- 🔧 **完整游戏引擎** - 房间、物品、NPC交互系统
- 📊 **状态管理系统** - 生命值、背包、任务进度
- 🏷️ **动态场景生成** - 可扩展的地图和故事
- 💾 **存档/读档功能** - JSON格式进度保存
- 🎯 **多结局系统** - 根据选择影响故事走向

**核心类**:
- `Player` - 玩家状态管理
- `Room` - 房间和导航系统
- `Item` / `Enemy` - 物品和敌人系统
- `GameEngine` - 游戏主引擎

---

### 📆 2026年2月4日 - Day 73

**文件**: `scripts/20260204_073_duplicate_file_finder.py`

**名称**: Duplicate File Finder - 重复文件查找与清理工具

**功能**: MD5哈希去重、递归扫描、交互式删除、空间占用分析

---

### 📆 2026年2月4日 - Day 72

**文件**: `scripts/20260204_072_learning_journal.py`

**名称**: Learning Journal - 代码学习日志工具

**功能**:
- 🔧 **代码片段管理** - 添加、搜索、过滤代码片段
- 📊 **学习统计分析** - 按语言、分类、标签统计
- 🏷️ **标签系统** - 支持多维度标签分类
- 📄 **多格式导出** - 支持Markdown/JSON导出
- 💾 **数据持久化** - JSON格式本地存储

---

### 历史记录

<details>
<summary>点击展开 Day 1-71</summary>

### 📆 2026年2月4日 - Day 71

**文件**: `scripts/20260204_071_code_complexity_analyzer.py`

**名称**: Code Complexity Analyzer - 智能代码复杂度分析器

**功能**: 圈复杂度计算、多语言支持、代码异味检测、HTML报告生成

---

### 📆 2026年2月4日 - Day 70

**文件**: `scripts/20260204_070_code_statistics_analyzer.py`

**名称**: Code Statistics Analyzer - 综合代码库统计分析工具

**功能**: 多语言支持、行数统计、结构分析、复杂度估算

---

### 📆 2026年2月3日 - Day 69

**文件**: `scripts/20260203_069_git_commit_pattern_analyzer.py`

**名称**: Git Commit Pattern Analyzer - Git提交模式分析与可视化工具

**功能**: 提交频率分析、活动热力图、可视化图表

---

</details>

---

## 🎯 项目目标

- ✅ 展示AI的持续编码能力
- ✅ 学习和掌握多种编程技术
- ✅ 建立个人代码知识库
- ✅ 记录AI的学习成长历程

## 📊 统计数据

| 指标 | 数值 |
|------|------|
| 提交天数 | 74天 |
| 代码文件 | 74+ |
| 语言覆盖 | Python, JavaScript, Shell等 |
| 项目星级 | ⭐ 持续增长中 |

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📝 许可证

MIT License

---

<div align="center">

**持续更新中...** 💪

</div>
---

## Day 76: CSV to Markdown Table Converter (2026-02-04)
- **文件**: `scripts/20260204_076_csv_to_markdown.py`
- **大小**: 8.8 KB
- **描述**: CSV转Markdown表格自动转换器
- **功能**:
  - 🔧 自动检测分隔符（逗号、制表符、分号等）
  - 📊 支持自定义表头和自动对齐
  - 📦 批量转换目录下所有CSV文件
  - 🧠 智能截断过长的文本

![Day 76](https://img.shields.io/badge/Day-76-blue)