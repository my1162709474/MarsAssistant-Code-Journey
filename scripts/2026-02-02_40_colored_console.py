#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 彩色终端输出工具 - Colored Console Output Utility
=====================================================
功能丰富的CLI彩色输出和格式化工具，支持日志、表格、进度等多种场景。

作者: MarsAssistant-Code-Journey
日期: 2026-02-02
版本: 1.0.0
"""

import sys
import time
import datetime
import os
from enum import Enum
from typing import Optional, Union, List, Dict, Any
from dataclasses import dataclass

# 尝试导入颜色库，如果不可用则使用ANSI转义码
try:
    from termcolor import colored as _colored_termcolor, COLORS as _TERM_COLORS
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False


# ============================================
# 基础颜色定义
# ============================================

class Colors:
    """终端颜色常量"""
    # 基础颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 高亮颜色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    @staticmethod
    def colored(text: str, color: str = None, on_color: str = None, 
                attrs: List[str] = None) -> str:
        """使用termcolor或ANSI转义码着色"""
        if HAS_TERMCOLOR and color:
            color_map = {
                'black': 'grey', 'grey': 'grey', 'gray': 'grey',
                'bright_black': 'grey', 'bright_grey': 'grey',
            }
            c = color_map.get(color, color)
            attrs_map = {
                'bold': ['bold'], 'dim': ['dim'], 'italic': ['italic'],
                'underline': ['underline'], 'blink': ['blink'],
                'reverse': ['reverse'], 'hidden': ['hidden']
            }
            attrs_list = attrs_map.get(color, []) if not attrs else attrs
            try:
                return _colored_termcolor(text, c, on_color=on_color, attrs=attrs_list)
            except:
                pass
        
        # 回退到ANSI转义码
        code = ''
        if color:
            color_codes = {
                'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
                'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37',
                'bright_black': '90', 'bright_red': '91', 'bright_green': '92',
                'bright_yellow': '93', 'bright_blue': '94', 'bright_magenta': '95',
                'bright_cyan': '96', 'bright_white': '97',
            }
            code += '\033[' + color_codes.get(color, '37') + 'm'
        
        if on_color:
            bg_codes = {
                'black': '40', 'red': '41', 'green': '42', 'yellow': '43',
                'blue': '44', 'magenta': '45', 'cyan': '46', 'white': '47',
            }
            code += '\033[' + bg_codes.get(on_color, '40') + 'm'
        
        if attrs:
            attr_codes = {
                'bold': '1', 'dim': '2', 'italic': '3', 'underline': '4',
                'blink': '5', 'reverse': '7', 'hidden': '8'
            }
            for attr in attrs:
                if attr in attr_codes:
                    code += '\033[' + attr_codes[attr] + 'm'
        
        return code + text + Colors.RESET
    
    @staticmethod
    def strip(text: str) -> str:
        """移除所有ANSI转义码"""
        import re
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)


# ============================================
# 日志级别
# ============================================

class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# ============================================
# 状态图标
# ============================================

class StatusIcons:
    """状态图标集合"""
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    QUESTION = '❓'
    IDEA = '💡'
    FIRE = '🔥'
    STAR = '⭐'
    GEAR = '⚙️'
    CLOCK = '⏰'
    CHECK = '✔️'
    CROSS = '✖️'
    ARROW_RIGHT = '→'
    ARROW_LEFT = '←'
    ARROW_UP = '↑'
    ARROW_DOWN = '↓'
    LOADING = '⟳'
    PENDING = '⏳'
    LOCK = '🔒'
    UNLOCK = '🔓'
    KEY = '🔑'
    SEARCH = '🔍'
    BELL = '🔔'
    MAIL = '📧'
    FILE = '📄'
    FOLDER = '📁'
    BOOK = '📚'
    WRENCH = '🔧'
    HAMMER = '🔨'
    LIGHTNING = '⚡'
    ROBOT = '🤖'
    ROCKET = '🚀'
    TROPHY = '🏆'
    TARGET = '🎯'
    HEART = '❤️'
    THUMBS_UP = '👍'
    THUMBS_DOWN = '👎'
    PARTY = '🎉'
    GIFT = '🎁'
    MUSIC = '🎵'
    FILM = '🎬'
    CAMERA = '📷'
    PHONE = '📱'
    COMPUTER = '💻'
    BUG = '🐛'
    BEAKER = '🧪'
    WRENCH_ADJUSTABLE = '🔧'
    ELECTRIC_PLUG = '🔌'
    BATTERY = '🔋'
    BULB = '💡'
    CANDLE = '🕯️'
    GEARS = '⚙️'
    CHAIN = '🔗'


# ============================================
# 配置类
# ============================================

@dataclass
class ConsoleConfig:
    """控制台输出配置"""
    show_timestamp: bool = True
    show_level: bool = True
    use_icons: bool = True
    colors: Dict[LogLevel, str] = None
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    width: int = 80
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                LogLevel.DEBUG: 'bright_black',
                LogLevel.INFO: 'blue',
                LogLevel.SUCCESS: 'green',
                LogLevel.WARNING: 'yellow',
                LogLevel.ERROR: 'red',
                LogLevel.CRITICAL: 'bright_red',
            }


# ============================================
# 彩色控制台类
# ============================================

class ColoredConsole:
    """彩色终端输出工具类"""
    
    # 默认配置
    DEFAULT_CONFIG = ConsoleConfig()
    
    def __init__(self, config: Optional[ConsoleConfig] = None):
        """初始化控制台工具
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or self.DEFAULT_CONFIG
        self._indent_level = 0
        self._indent_char = '    '  # 4个空格
    
    def _format_timestamp(self) -> str:
        """格式化时间戳"""
        if self.config.show_timestamp:
            return datetime.datetime.now().strftime(self.config.timestamp_format) + ' '
        return ''
    
    def _format_level(self, level: LogLevel) -> str:
        """获取级别字符串"""
        if self.config.show_level:
            level_names = {
                LogLevel.DEBUG: 'DEBUG',
                LogLevel.INFO: 'INFO',
                LogLevel.SUCCESS: 'SUCCESS',
                LogLevel.WARNING: 'WARNING',
                LogLevel.ERROR: 'ERROR',
                LogLevel.CRITICAl: 'CRITICAL',
            }
            return f"[{level_names.get(level, 'UNKNOWN')}] "
        return ''
    
    def _get_icon(self, level: LogLevel) -> str:
        """获取对应级别的图标"""
        if self.config.use_icons:
            icons = {
                LogLevel.DEBUG: StatusIcons.GEAR,
                LogLevel.INFO: StatusIcons.INFO,
                LogLevel.SUCCESS: StatusIcons.SUCCESS,
                LogLevel.WARNING: StatusIcons.WARNING,
                LogLevel.ERROR: StatusIcons.ERROR,
                LogLevel.CRITICAL: StatusIcons.FIRE,
            }
            return icons.get(level, '') + ' '
        return ''
    
    def _indent(self, text: str) -> str:
        """缩进文本"""
        if self._indent_level > 0:
            indent = self._indent_char * self._indent_level
            return '\n'.join([indent + line for line in text.split('\n')])
        return text
    
    # ==================== 基础输出方法 ====================
    
    def print(self, *args, color: str = None, bold: bool = False, 
              newline: bool = True, **kwargs) -> None:
        """自定义颜色打印
        
        Args:
            *args: 要打印的内容
            color: 颜色名称
            bold: 是否加粗
            newline: 是否换行
            **kwargs: 其他传递给print的参数
        """
        attrs = ['bold'] if bold else None
        parts = []
        for arg in args:
            if isinstance(arg, str):
                parts.append(Colors.colored(arg, color, attrs=attrs))
            else:
                parts.append(str(arg))
        
        text = ' '.join(parts)
        if self._indent_level > 0:
            text = self._indent(text)
        
        print(text, **kwargs, end='\n' if newline else '')
        sys.stdout.flush()
    
    def print_header(self, text: str, char: str = '=', 
                     color: str = 'cyan', bold: bool = True) -> None:
        """打印标题栏
        
        Args:
            text: 标题文本
            char: 分隔符字符
            color: 颜色
            bold: 是否加粗
        """
        width = self.config.width
        half = (width - len(text) - 2) // 2
        line = char * half + ' ' + text + ' ' + char * (width - len(text) - 2 - half)
        self.print(line, color=color, bold=bold)
    
    def print_section(self, title: str, content: str = '', 
                      color: str = 'blue', border_char: str = '─') -> None:
        """打印区块
        
        Args:
            title: 区块标题
            content: 区块内容
            color: 标题颜色
            border_char: 边框字符
        """
        width = self.config.width
        self.print('┌' + border_char * (width - 2) + '┐')
        self.print('│ ' + title.upper().center(width - 4) + ' │', color=color, bold=True)
        self.print('├' + border_char * (width - 2) + '┤')
        if content:
            for line in content.split('\n'):
                self.print('│ ' + line.ljust(width - 4) + ' │')
        self.print('└' + border_char * (width - 2) + '┘')
    
    def print_divider(self, char: str = '─', color: str = None) -> None:
        """打印分隔线"""
        line = char * self.config.width
        self.print(line, color=color)
    
    def print_empty(self, count: int = 1) -> None:
        """打印空行"""
        for _ in range(count):
            print()
    
    # ==================== 日志输出方法 ====================
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO,
            icon: str = None) -> None:
        """输出日志
        
        Args:
            message: 日志消息
            level: 日志级别
            icon: 自定义图标
        """
        timestamp = self._format_timestamp()
        level_str = self._format_level(level)
        icon_str = icon or self._get_icon(level)
        color = self.config.colors.get(level, 'white')
        
        full_message = f"{timestamp}{level_str}{icon_str}{message}"
        self.print(full_message, color=color)
    
    def debug(self, message: str) -> None:
        """调试日志"""
        self.log(message, LogLevel.DEBUG)
    
    def info(self, message: str) -> None:
        """信息日志"""
        self.log(message, LogLevel.INFO)
    
    def success(self, message: str) -> None:
        """成功日志"""
        self.log(message, LogLevel.SUCCESS)
    
    def warning(self, message: str) -> None:
        """警告日志"""
        self.log(message, LogLevel.WARNING)
    
    def error(self, message: str) -> None:
        """错误日志"""
        self.log(message, LogLevel.ERROR)
    
    def critical(self, message: str) -> None:
        """严重错误日志"""
        self.log(message, LogLevel.CRITICAL)
    
    # ==================== 格式化输出方法 ====================
    
    def print_key_value(self, key: str, value: Any, 
                        key_color: str = 'cyan', value_color: str = 'white') -> None:
        """打印键值对
        
        Args:
            key: 键
            value: 值
            key_color: 键的颜色
            value_color: 值的颜色
        """
        separator = ': '
        self.print(key, color=key_color, bold=True, newline=False)
        self.print(separator, newline=False)
        self.print(str(value), color=value_color)
    
    def print_list(self, items: List[str], bullet: str = '•', 
                   bullet_color: str = 'yellow', item_color: str = None) -> None:
        """打印列表
        
        Args:
            items: 列表项
            bullet: 项目符号
            bullet_color: 项目符号颜色
            item_color: 项文本颜色
        """
        for item in items:
            self.print(f"{bullet} ", color=bullet_color, bold=True, newline=False)
            self.print(item, color=item_color)
    
    def print_numbered_list(self, items: List[str], 
                            number_color: str = 'cyan', item_color: str = None,
                            start: int = 1) -> None:
        """打印编号列表
        
        Args:
            items: 列表项
            number_color: 编号颜色
            item_color: 项文本颜色
            start: 起始编号
        """
        for i, item in enumerate(items, start):
            self.print(f"{i}. ", color=number_color, bold=True, newline=False)
            self.print(item, color=item_color)
    
    def print_checklist(self, items: Dict[str, bool], 
                        checked_color: str = 'green', 
                        unchecked_color: str = 'bright_black') -> None:
        """打印勾选列表
        
        Args:
            items: {文本: 是否选中}
            checked_color: 选中状态颜色
            unchecked_color: 未选中状态颜色
        """
        for text, checked in items.items():
            icon = StatusIcons.CHECK if checked else StatusIcons.CROSS
            color = checked_color if checked else unchecked_color
            self.print(f"{icon} ", color=color, bold=True, newline=False)
            self.print(text, color=color if not checked else None)
    
    def print_steps(self, steps: List[str], current_step: int = 0) -> None:
        """打印步骤指示器
        
        Args:
            steps: 步骤列表
            current_step: 当前步骤索引（0-based）
        """
        for i, step in enumerate(steps):
            if i < current_step:
                self.print(f"{StatusIcons.CHECK} ", color='green', bold=True, newline=False)
                self.print(step, color='green')
            elif i == current_step:
                self.print(f"{StatusIcons.PENDING} ", color='yellow', bold=True, newline=False)
                self.print(step, color='yellow', bold=True)
            else:
                self.print(f"  ", newline=False)
                self.print(step, color='bright_black')
    
    # ==================== 表格输出方法 ====================
    
    def print_table(self, headers: List[str], rows: List[List[Any]], 
                    align: str = 'left', grid: bool = True,
                    header_color: str = 'cyan') -> None:
        """打印表格
        
        Args:
            headers: 表头
            rows: 数据行
            align: 对齐方式 ('left', 'center', 'right')
            grid: 是否显示网格
            header_color: 表头颜色
        """
        if not headers and not rows:
            return
        
        # 计算列宽
        all_data = [headers] + rows if headers else rows
        col_widths = []
        for col_idx in range(len(all_data[0])):
            max_width = max(len(str(row[col_idx])) if col_idx < len(row) else 0 
                          for row in all_data)
            col_widths.append(max_width + 2)
        
        def align_text(text: str, width: int, alignment: str) -> str:
            text = str(text)
            if alignment == 'center':
                return text.center(width)
            elif alignment == 'right':
                return text.rjust(width)
            return text.ljust(width)
        
        # 打印表头
        if headers:
            if grid:
                self.print('┌' + '┬'.join('─' * w for w in col_widths) + '┐')
            header_row = '│'.join(align_text(h, col_widths[i], align) 
                                  for i, h in enumerate(headers))
            self.print('│' + header_row + '│', color=header_color, bold=True)
            if grid:
                self.print('├' + '┼'.join('─' * w for w in col_widths) + '┤')
        elif grid:
            self.print('┌' + '┬'.join('─' * w for w in col_widths) + '┐')
        
        # 打印数据行
        for row in rows:
            row_str = '│'.join(align_text(str(row[i]), col_widths[i], align) 
                              for i in range(len(row)))
            self.print('│' + row_str + '│')
        
        # 打印表格底部
        if grid:
            self.print('└' + '┴'.join('─' * w for w in col_widths) + '┘')
    
    def print_tree(self, data: Dict[str, Any], level: int = 0, 
                   is_last: bool = True, prefix: str = '',
                   branch_char: str = '│', leaf_char: str = '├', 
                   end_char: str = '└') -> None:
        """打印树形结构
        
        Args:
            data: 树形数据字典
            level: 当前层级
            is_last: 是否是最后一个节点
            prefix: 前缀字符串
            branch_char: 分支字符
            leaf_char: 叶节点字符
            end_char: 结束字符
        """
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            current_prefix = prefix + (end_char if is_last else leaf_char) + '── '
            next_prefix = prefix + ('    ' if is_last else branch_char + '   ')
            
            self.print(current_prefix, color='cyan', bold=True, newline=False)
            
            if isinstance(value, dict) and value:
                self.print(key, color='yellow', bold=True)
                self.print_tree(value, level + 1, is_last_item, next_prefix,
                              branch_char, leaf_char, end_char)
            elif isinstance(value, list) and value:
                self.print(f"{key} ({len(value)} items)", color='yellow', bold=True)
                for j, item in enumerate(value):
                    self.print_tree(item if isinstance(item, dict) else {'value': item},
                                  level + 1, j == len(value) - 1, next_prefix,
                                  branch_char, leaf_char, end_char)
            else:
                self.print(key, color='yellow', bold=True, newline=False)
                if value is not None and value != '':
                    self.print(f': {value}', color='white')
    
    # ==================== 进度和状态方法 ====================
    
    def print_status(self, status: str, icon: str = StatusIcons.INFO,
                     status_color: str = 'blue') -> None:
        """打印状态
        
        Args:
            status: 状态文本
            icon: 状态图标
            status_color: 状态颜色
        """
        self.print(f"{icon} ", color=status_color, bold=True, newline=False)
        self.print(status, color=status_color)
    
    def print_loading(self, message: str, duration: float = 2.0, 
                      steps: int = 10, style: str = 'dots') -> None:
        """打印加载动画
        
        Args:
            message: 加载消息
            duration: 持续时间（秒）
            steps: 动画步数
            style: 样式 ('dots', 'bar', 'spinner')
        """
        if style == 'dots':
            frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            interval = duration / steps
            for i in range(steps):
                frame = frames[i % len(frames)]
                print(f"\r{message} {frame}", end='', flush=True)
                time.sleep(interval)
            print('\r' + ' ' * (len(message) + 3) + '\r', end='')
        
        elif style == 'bar':
            interval = duration / steps
            for i in range(steps + 1):
                bar_length = 20
                filled = int(bar_length * i / steps)
                bar = '█' * filled + '░' * (bar_length - filled)
                percent = i * 100 // steps
                print(f"\r{message} [{bar}] {percent}%", end='', flush=True)
                time.sleep(interval)
            print('\r' + ' ' * (len(message) + bar_length + 10) + '\r', end='')
        
        elif style == 'spinner':
            chars = ['-', '\\', '|', '/']
            interval = duration / steps
            for i in range(steps):
                char = chars[i % len(chars)]
                print(f"\r{message} {char}", end='', flush=True)
                time.sleep(interval)
            print('\r' + ' ' * (len(message) + 3) + '\r', end='')
        
        self.success(f"{message} 完成！")
    
    def print_progress(self, current: int, total: int, prefix: str = '', 
                       suffix: str = '', length: int = 30,
                       fill: str = '█', empty: str = '░',
                       show_percent: bool = True) -> None:
        """打印进度条
        
        Args:
            current: 当前进度
            total: 总进度
            prefix: 前缀文本
            suffix: 后缀文本
            length: 进度条长度
            fill: 填充字符
            empty: 空字符
            show_percent: 是否显示百分比
        """
        percent = current / total if total > 0 else 1.0
        filled = int(length * percent)
        bar = fill * filled + empty * (length - filled)
        
        if show_percent:
            percent_str = f"{percent * 100:.1f}%"
        else:
            percent_str = f"{current}/{total}"
        
        line = f"\r{prefix} [{bar}] {percent_str} {suffix}"
        print(line, end='', flush=True)
        
        if current >= total:
            print()
    
    # ==================== 特殊效果方法 ====================
    
    def print_rainbow(self, text: str) -> None:
        """打印彩虹渐变文本"""
        colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
        result = ''
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            result += Colors.colored(char, color)
        self.print(result)
    
    def print_gradient(self, text: str, start_color: str = 'red', 
                       end_color: str = 'blue') -> None:
        """打印渐变文本"""
        colors = [start_color, 'yellow', end_color]
        result = ''
        for i, char in enumerate(text):
            color_idx = int(i / len(text) * (len(colors) - 1))
            result += Colors.colored(char, colors[color_idx])
        self.print(result)
    
    def print_code_block(self, code: str, language: str = 'python') -> None:
        """打印代码块"""
        self.print(f"```{language}", color='bright_black')
        self.print(code, color='white')
        self.print("```", color='bright_black')
    
    def print_quote(self, text: str, author: str = None, 
                    quote_char: str = '"') -> None:
        """打印引用"""
        lines = text.split('\n')
        for line in lines:
            self.print(f"{quote_char} {line}", color='magenta', italic=True)
        if author:
            self.print(f"  — {author}", color='bright_black', italic=True)
    
    def print_alert(self, alert_type: str, message: str, title: str = None) -> None:
        """打印警告框
        
        Args:
            alert_type: 类型 ('info', 'success', 'warning', 'error')
            message: 消息内容
            title: 可选标题
        """
        configs = {
            'info': ('ℹ️', 'blue', '信息'),
            'success': ('✅', 'green', '成功'),
            'warning': ('⚠️', 'yellow', '警告'),
            'error': ('❌', 'red', '错误'),
        }
        
        icon, color, default_title = configs.get(alert_type, configs['info'])
        title = title or default_title
        
        self.print_section(f"{icon} {title}", message, color=color)
    
    def print_banner(self, text: str, border_char: str = '*', 
                     border_color: str = 'cyan') -> None:
        """打印横幅
        
        Args:
            text: 横幅文本
            border_char: 边框字符
            border_color: 边框颜色
        """
        width = len(text) + 4
        border = border_char * width
        self.print(border, color=border_color)
        self.print(f"{border_char} {text} {border_char}", color=border_color)
        self.print(border, color=border_color)
    
    def print_box(self, text: str, padding: int = 2, 
                  border_color: str = 'cyan', text_color: str = None) -> None:
        """打印文本框
        
        Args:
            text: 文本内容
            padding: 内边距
            border_color: 边框颜色
            text_color: 文本颜色
        """
        lines = text.split('\n')
        max_len = max(len(line) for line in lines)
        width = max_len + padding * 2 + 2
        
        border = '─' * (width - 2)
        
        self.print('┌' + border + '┐', color=border_color)
        for line in lines:
            padded = ' ' * padding + line + ' ' * (max_len - len(line) + padding)
            self.print('│' + padded + '│', color=text_color)
        self.print('└' + border + '┘', color=border_color)
    
    # ==================== 缩进管理 ====================
    
    def indent(self, level: int = 1) -> 'ColoredConsole':
        """增加缩进
        
        Args:
            level: 缩进级别
        
        Returns:
            self
        """
        self._indent_level += level
        return self
    
    def dedent(self, level: int = 1) -> 'ColoredConsole':
        """减少缩进
        
        Args:
            level: 缩进级别
        
        Returns:
            self
        """
        self._indent_level = max(0, self._indent_level - level)
        return self
    
    def reset_indent(self) -> 'ColoredConsole':
        """重置缩进
        
        Returns:
            self
        """
        self._indent_level = 0
        return self
    
    # ==================== 颜色和样式快捷方法 ====================
    
    def black(self, text: str) -> str:
        return Colors.colored(text, 'black')
    
    def red(self, text: str) -> str:
        return Colors.colored(text, 'red')
    
    def green(self, text: str) -> str:
        return Colors.colored(text, 'green')
    
    def yellow(self, text: str) -> str:
        return Colors.colored(text, 'yellow')
    
    def blue(self, text: str) -> str:
        return Colors.colored(text, 'blue')
    
    def magenta(self, text: str) -> str:
        return Colors.colored(text, 'magenta')
    
    def cyan(self, text: str) -> str:
        return Colors.colored(text, 'cyan')
    
    def white(self, text: str) -> str:
        return Colors.colored(text, 'white')
    
    def bright_black(self, text: str) -> str:
        return Colors.colored(text, 'bright_black')
    
    def bright_red(self, text: str) -> str:
        return Colors.colored(text, 'bright_red')
    
    def bright_green(self, text: str) -> str:
        return Colors.colored(text, 'bright_green')
    
    def bright_yellow(self, text: str) -> str:
        return Colors.colored(text, 'bright_yellow')
    
    def bright_blue(self, text: str) -> str:
        return Colors.colored(text, 'bright_blue')
    
    def bright_magenta(self, text: str) -> str:
        return Colors.colored(text, 'bright_magenta')
    
    def bright_cyan(self, text: str) -> str:
        return Colors.colored(text, 'bright_cyan')
    
    def bright_white(self, text: str) -> str:
        return Colors.colored(text, 'bright_white')
    
    def bold(self, text: str) -> str:
        return Colors.colored(text, attrs=['bold'])
    
    def italic(self, text: str) -> str:
        return Colors.colored(text, attrs=['italic'])
    
    def underline(self, text: str) -> str:
        return Colors.colored(text, attrs=['underline'])


# ============================================
# 全局实例
# ============================================

console = ColoredConsole()


# ============================================
# 演示和测试
# ============================================

def demo():
    """演示各种功能"""
    c = console
    c.print_header("🎨 彩色终端输出工具演示", color='cyan')
    c.print_empty()
    
    # 基础打印
    c.print_section("基础打印功能", "这是基础打印功能的演示")
    
    c.print("普通文本")
    c.print("红色文本", color='red')
    c.print("绿色文本", color='green')
    c.print("蓝色文本", color='blue')
    c.print("加粗文本", bold=True)
    c.print("红色加粗文本", color='red', bold=True)
    c.print_empty()
    
    # 日志输出
    c.print_section("日志输出", "不同级别的日志输出")
    c.debug("这是一条调试信息")
    c.info("这是一条普通信息")
    c.success("操作成功！")
    c.warning("这是一条警告")
    c.error("发生了一个错误")
    c.critical("发生严重错误！")
    c.print_empty()
    
    # 状态输出
    c.print_section("状态输出", "各种状态图标和颜色")
    c.print_status("系统运行正常", StatusIcons.SUCCESS, 'green')
    c.print_status("正在处理...", StatusIcons.LOADING, 'yellow')
    c.print_status("任务已锁定", StatusIcons.LOCK, 'red')
    c.print_empty()
    
    # 列表输出
    c.print_section("列表输出", "不同风格的列表")
    c.print_list(["Python", "JavaScript", "Go", "Rust"], bullet='•')
    c.print_empty()
    c.print_numbered_list(["功能一", "功能二", "功能三"], start=1)
    c.print_empty()
    c.print_checklist({"已完成": True, "进行中": True, "待开始": False})
    c.print_empty()
    
    # 表格输出
    c.print_section("表格输出", "ASCII表格展示")
    headers = ["语言", "排名", "热度"]
    rows = [
        ["Python", "1", "92.5%"],
        ["JavaScript", "2", "88.2%"],
        ["Java", "3", "76.3%"],
        ["TypeScript", "4", "72.1%"],
    ]
    c.print_table(headers, rows, grid=True)
    c.print_empty()
    
    # 进度条
    c.print_section("进度条演示", "加载进度显示")
    c.print("正在加载...", newline=False)
    c.print_loading("加载中", duration=1.5, style='bar')
    c.print_empty()
    
    # 代码块
    c.print_section("代码展示", "代码块样式")
    c.print_code_block("""
def hello():
    print("Hello, World!")
    
result = hello()
print(f"Result: {result}")
    """, language='python')
    c.print_empty()
    
    # 引用
    c.print_section("引用展示", "引用样式")
    c.print_quote("编程是思考的艺术，而非敲键的技巧。", author="Edsger W. Dijkstra")
    c.print_empty()
    
    # 警告框
    c.print_section("警告框", "不同类型的提示框")
    c.print_alert("info", "这是一条提示信息")
    c.print_alert("success", "操作已成功完成！")
    c.print_alert("warning", "请注意，这只是一个警告")
    c.print_alert("error", "发生了一个错误，请检查！")
    c.print_empty()
    
    # 横幅和文本框
    c.print_section("特殊效果", "横幅和文本框")
    c.print_banner("HELLO WORLD", border_char='*', border_color='cyan')
    c.print_empty()
    c.print_box("这是一段在文本框中的内容\n支持多行文本展示", border_color='blue')
    c.print_empty()
    
    # 彩虹和渐变
    c.print_section("渐变效果", "彩虹渐变文本")
    c.print_rainbow("RAINBOW TEXT")
    c.print_gradient("GRADIENT TEXT", start_color='red', end_color='blue')
    c.print_empty()
    
    # 树形结构
    c.print_section("树形结构", "树形数据展示")
    tree_data = {
        "项目": {
            "src": {
                "main.py": "主程序",
                "utils.py": "工具函数"
            },
            "tests": {
                "test_main.py": None,
                "test_utils.py": None
            },
            "docs": ["README.md", "CHANGELOG.md"]
