
### Day 28: CLI任务管理器和便签工具 (2026-02-02 11:56) ⭐ **最新**
  - 📁 文件: `scripts/2026-02-02_28_task_manager.py`
  - 📊 大小: 10.3 KB
  - 💡 命令行任务管理器，支持创建/列出/完成/删除任务
  - 💡 便签功能，支持多种颜色
  - 💡 任务优先级(high/medium/low)和标签分类
  - 💡 统计信息和进度跟踪
  - 🔗 https://github.com/my1162709474/MarsAssistant-Code-Journey/blob/main/scripts/2026-02-02_28_task_manager.py
# Day 27: 智能倒计时工具 - Event Countdown Timer 📅

📁 **文件**: `scripts/2026-02-02_27_countdown_timer.py`
📊 **大小**: 12.2 KB
📝 **功能**: 事件倒计时管理与时间计算工具

### ✨ 功能特性

- **🎯 事件管理**: 添加、删除、列出目标事件
- **⏰ 倒计时计算**: 支持多种时间格式显示
- **📅 日期支持**: 公历日期处理
- **🔄 循环事件**: 支持每年/每月/每周重复
- **🎨 多格式显示**:
  - 完整格式: 100天 5小时 30分 15秒
  - 简洁格式: 100d 5h 30m 15s
  - Emoji格式: ⏰ 100天5小时
  - 进度条格式: [████░░░░░░] 33%
- **💾 数据持久化**: 自动保存到JSON文件

### 使用方法

```python
from countdown_timer import CountdownTimer, DateType, DisplayFormat

# 创建计时器
timer = CountdownTimer()

# 添加事件
timer.add_event(
    "春节",
    "2027-02-17",
    DateType.GREGORIAN,
    "yearly",
    "中国传统节日"
)

# 获取倒计时
countdown = timer.get_event_countdown(event_id, DisplayFormat.FULL)
print(f"距离春节还有: {countdown}")

# 列出所有事件
print(timer.list_events(DisplayFormat.EMOJI))
```

### 示例输出

```
📅 事件倒计时

⏳ 春节: ⏰ 365天
⏳ 生日: ⏰ 41天
✅ 项目截止: 现在!

详细倒计时:
- 春节: 365天 2小时 15分 30秒
- 生日: 41天 6小时 45分 20秒
```

### 核心类说明

| 类名 | 说明 |
|------|------|
| `DateType` | 日期类型枚举 (GREGORIAN/LUNAR) |
| `DisplayFormat` | 显示格式枚举 |
| `CountdownTimer` | 倒计时管理器主类 |
| `LunarCalendar` | 农历日期处理工具 |

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
