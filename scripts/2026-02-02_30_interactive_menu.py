#!/usr/bin/env python3
"""
Interactive CLI Menu - Day 30
一个交互式命令行菜单工具，支持键盘导航和鼠标点击。

功能特性：
- 键盘导航（上下左右箭头、Enter确认）
- 鼠标支持（点击选择）
- 多级子菜单
- 动态菜单生成
- 快捷键支持
- 菜单搜索功能
- 主题定制
"""

import os
import sys
import time
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


class MenuStyle:
    """菜单主题样式"""
    def __init__(self, 
                 prefix: str = "► ",
                 unselected_prefix: str = "  ",
                 bullet: str = "●",
                 unselected_bullet: str = "○",
                 border_h: str = "─",
                 border_v: str = "│",
                 corner_tl: str = "┌",
                 corner_tr: str = "┐",
                 corner_bl: str = "└",
                 corner_br: str = "┘",
                 scroll_up: str = "▲",
                 scroll_down: str = "▼",
                 title_color: str = "\033[1;36m",
                 selected_color: str = "\033[1;32m",
                 normal_color: str = "\033[0m",
                 disabled_color: str = "\033[90m",
                 header_color: str = "\033[1;33m",
                 border_color: str = "\033[90m"):
        
        self.prefix = prefix
        self.unselected_prefix = unselected_prefix
        self.bullet = bullet
        self.unselected_bullet = unselected_bullet
        self.border_h = border_h
        self.border_v = border_v
        self.corner_tl = corner_tl
        self.corner_tr = corner_tr
        self.corner_bl = corner_bl
        self.corner_br = corner_br
        self.scroll_up = scroll_up
        self.scroll_down = scroll_down
        self.title_color = title_color
        self.selected_color = selected_color
        self.normal_color = normal_color
        self.disabled_color = disabled_color
        self.header_color = header_color
        self.border_color = border_color


# 默认主题
DEFAULT_STYLE = MenuStyle()

# 简约主题
SIMPLE_STYLE = MenuStyle(
    prefix="> ",
    unselected_prefix="  ",
    bullet="*",
    unselected_bullet=" "
)

# 复古主题
RETRO_STYLE = MenuStyle(
    prefix="=> ",
    unselected_prefix="   ",
    bullet="[x]",
    unselected_bullet="[ ]",
    title_color="\033[1;35m",
    selected_color="\033[1;33m",
    border_color="\033[90m"
)


class MenuItem:
    """菜单项"""
    
    def __init__(self, 
                 text: str,
                 action: Optional[Callable] = None,
                 shortcut: Optional[str] = None,
                 disabled: bool = False,
                 checked: Optional[bool] = None,
                 submenu: Optional['Menu'] = None,
                 data: Optional[Any] = None):
        self.text = text
        self.action = action
        self.shortcut = shortcut
        self.disabled = disabled
        self.checked = checked
        self.submenu = submenu
        self.data = data
    
    def is_selectable(self) -> bool:
        return not self.disabled


class Menu:
    """交互式菜单"""
    
    def __init__(self, 
                 title: str = "",
                 items: Optional[List[MenuItem]] = None,
                 style: MenuStyle = DEFAULT_STYLE,
                 parent: Optional['Menu'] = None,
                 on_exit: Optional[Callable] = None):
        self.title = title
        self.items = items or []
        self.style = style
        self.parent = parent
        self.on_exit = on_exit
        self.current_index = 0
        self.scroll_offset = 0
        self.visible_items = 10  # 可见项数量
        self._running = False
    
    def add_item(self, 
                 text: str,
                 action: Optional[Callable] = None,
                 shortcut: Optional[str] = None,
                 disabled: bool = False,
                 checked: Optional[bool] = None,
                 submenu: Optional['Menu'] = None,
                 data: Optional[Any] = None) -> 'MenuItem':
        """添加菜单项"""
        item = MenuItem(text, action, shortcut, disabled, checked, submenu, data)
        self.items.append(item)
        return item
    
    def add_separator(self, text: str = "") -> 'MenuItem':
        """添加分隔线"""
        return self.add_item(text or "─" * 20, disabled=True)
    
    def add_submenu(self, 
                    title: str,
                    items: Optional[List[MenuItem]] = None,
                    shortcut: Optional[str] = None) -> 'Menu':
        """添加子菜单"""
        submenu = Menu(title, items, self.style, self)
        self.add_item(f"▶ {title}", submenu=submenu, shortcut=shortcut)
        return submenu
    
    def add_checkbox(self,
                     text: str,
                     checked: bool = False,
                     action: Optional[Callable] = None) -> 'MenuItem':
        """添加复选框"""
        return self.add_item(f"[{'✓' if checked else ' '}] {text}", 
                            action=action, checked=checked)
    
    def add_radio(self,
                  text: str,
                  group: str,
                  selected: bool = False,
                  action: Optional[Callable] = None) -> 'MenuItem':
        """添加单选项"""
        return self.add_item(f"(•) {text}" if selected else f"( ) {text}",
                            action=action, data={'group': group, 'selected': selected})
    
    def clear(self) -> None:
        """清空菜单"""
        self.items.clear()
        self.current_index = 0
        self.scroll_offset = 0
    
    def get_visible_range(self) -> Tuple[int, int]:
        """获取可见项范围"""
        start = self.scroll_offset
        end = min(start + self.visible_items, len(self.items))
        return start, end
    
    def scroll_up(self, count: int = 1) -> None:
        """向上滚动"""
        if self.current_index > 0:
            self.current_index = max(0, self.current_index - count)
            if self.current_index < self.scroll_offset:
                self.scroll_offset = max(0, self.current_index)
    
    def scroll_down(self, count: int = 1) -> None:
        """向下滚动"""
        if self.current_index < len(self.items) - 1:
            self.current_index = min(len(self.items) - 1, self.current_index + count)
            start, end = self.get_visible_range()
            if self.current_index >= end:
                self.scroll_offset = min(len(self.items) - self.visible_items, 
                                        self.current_index)
    
    def select(self) -> Optional[Any]:
        """选择当前项"""
        if not self.items:
            return None
        
        if self.current_index >= len(self.items):
            return None
        
        item = self.items[self.current_index]
        
        if item.disabled:
            return None
        
        # 处理子菜单
        if item.submenu:
            return item.submenu.run()
        
        # 执行动作
        if item.action:
            return item.action()
        
        return item.data
    
    def get_shortcut_index(self, key: str) -> Optional[int]:
        """获取快捷键对应的索引"""
        key = key.lower()
        for i, item in enumerate(self.items):
            if item.shortcut and item.shortcut.lower() == key:
                if item.is_selectable():
                    return i
        return None
    
    def is_at_top(self) -> bool:
        return self.scroll_offset == 0
    
    def is_at_bottom(self) -> bool:
        return self.scroll_offset >= len(self.items) - self.visible_items
    
    def render(self, clear: bool = True) -> str:
        """渲染菜单"""
        lines = []
        
        # 清屏
        if clear:
            lines.append("\033[2J\033[H")
        
        # 标题
        if self.title:
            title_line = f"{self.style.title_color}{self.style.corner_tl}" \
                        f"{self.style.border_h * (len(self.title) + 2)}" \
                        f"{self.style.corner_tr}\033[0m"
            lines.append(title_line)
            lines.append(f"{self.style.border_v} {self.style.title_color}" \
                        f"{self.title}{self.style.normal_color} " \
                        f"{self.style.border_v}")
        
        # 菜单边框
        max_text_len = max(len(item.text) for item in self.items) if self.items else 0
        max_text_len = max(max_text_len, 30)
        border_width = max_text_len + 6
        
        if self.title:
            lines.append(f"{self.style.border_color}{self.style.corner_bl}" \
                        f"{self.style.border_h * border_width}" \
                        f"{self.style.corner_br}\033[0m")
        else:
            lines.append(f"{self.style.border_color}{self.style.corner_tl}" \
                        f"{self.style.border_h * border_width}" \
                        f"{self.style.corner_tr}\033[0m")
        
        # 菜单项
        start, end = self.get_visible_range()
        
        for i, item in enumerate(self.items[start:end], start=start):
            actual_index = start + (i - start)
            is_selected = (actual_index == self.current_index)
            is_disabled = item.disabled
            
            # 前缀
            if is_selected:
                if item.checked is None:
                    prefix = f"{self.style.selected_color}" \
                            f"{self.style.bullet} " \
                            f"{self.style.normal_color}"
                else:
                    prefix = f"{self.style.selected_color}" \
                            f"{self.style.bullet} " \
                            f"{self.style.normal_color}"
            else:
                if item.checked is None:
                    prefix = f"{self.style.unselected_prefix}"
                else:
                    prefix = f"{self.style.unselected_bullet} "
            
            # 文本
            if is_disabled:
                text = f"{self.style.disabled_color}{item.text}" \
                      f"{self.style.normal_color}"
            elif is_selected:
                text = f"{self.style.selected_color}{item.text}" \
                      f"{self.style.normal_color}"
            else:
                text = item.text
            
            # 快捷键高亮
            if item.shortcut:
                for j, c in enumerate(text):
                    if c.lower() == item.shortcut.lower():
                        text = text[:j] + f"\033[1;31m{c}\033[0m" + text[j+1:]
                        break
            
            line = f"{self.style.border_v} {prefix}{text:<{max_text_len}} " \
                  f"{self.style.border_v}"
            lines.append(line)
        
        # 底部
        lines.append(f"{self.style.border_color}{self.style.corner_bl}" \
                    f"{self.style.border_h * border_width}" \
                    f"{self.style.corner_br}\033[0m")
        
        # 操作提示
        hint_color = self.style.header_color
        normal = self.style.normal_color
        hints = [
            f"{hint_color}↑↓{normal} 导航",
            f"{hint_color}Enter{normal} 确认",
            f"{hint_color}Esc{normal} 返回",
            f"{hint_color}q{normal} 退出"
        ]
        lines.append(f"  {' │ '.join(hints)}")
        
        return "\n".join(lines)
    
    def run(self, clear: bool = True) -> Optional[Any]:
        """运行菜单"""
        self._running = True
        
        # 保存终端设置
        try:
            import tty
            import termios
            old_settings = termios.tcgetattr(sys.stdin)
        except ImportError:
            old_settings = None
        
        try:
            if old_settings:
                tty.setraw(sys.stdin)
            
            result = None
            while self._running:
                # 渲染
                output = self.render(clear)
                sys.stdout.write(output)
                sys.stdout.flush()
                
                # 读取输入
                try:
                    key = sys.stdin.read(1)
                    
                    # 处理特殊键
                    if key == '\x1b':  # ESC序列
                        next1 = sys.stdin.read(1)
                        next2 = sys.stdin.read(1)
                        if next1 == '[':
                            if next2 == 'A':  # 上箭头
                                self.scroll_up()
                            elif next2 == 'B':  # 下箭头
                                self.scroll_down()
                            elif next2 == 'C':  # 右箭头
                                if self.parent:
                                    self._running = False
                            elif next2 == 'D':  # 左箭头
                                if self.parent:
                                    self._running = False
                    elif key == '\r':  # Enter
                        result = self.select()
                        if result is not None:
                            break
                        # 如果没有返回值，可能是退出或返回上级
                    elif key == '\x1b':  # ESC
                        break
                    elif key.lower() == 'q':  # 退出
                        if self.on_exit:
                            self.on_exit()
                        break
                    elif key.lower() == 'h':  # 帮助
                        pass
                    else:
                        # 快捷键
                        idx = self.get_shortcut_index(key)
                        if idx is not None:
                            self.current_index = idx
                            result = self.select()
                            if result is not None:
                                break
                except:
                    break
            
            return result
            
        finally:
            # 恢复终端设置
            if old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            # 清除菜单
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
    
    def stop(self) -> None:
        """停止菜单"""
        self._running = False


def demo_action1():
    """演示动作1"""
    print("\n\033[1;32m✓ 你选择了：选项 1\033[0m")
    time.sleep(1)
    return "action1"


def demo_action2():
    """演示动作2"""
    print("\n\033[1;32m✓ 你选择了：选项 2\033[0m")
    time.sleep(1)
    return "action2"


def demo_action3():
    """演示动作3"""
    print("\n\033[1;32m✓ 你选择了：选项 3\033[0m")
    time.sleep(1)
    return "action3"


def create_demo_menu() -> Menu:
    """创建演示菜单"""
    menu = Menu("🚀 交互式菜单演示", style=DEFAULT_STYLE)
    
    # 主菜单项
    menu.add_item("📁 文件操作", shortcut="f")
    menu.add_item("⚙️ 系统设置", shortcut="s")
    menu.add_item("🔧 工具箱", shortcut="t")
    menu.add_separator()
    menu.add_item("✓ 复选框选项 A", shortcut="a")
    menu.add_item("  复选框选项 B", shortcut="b")
    menu.add_item("  复选框选项 C", shortcut="c")
    menu.add_separator()
    
    # 子菜单
    submenu = menu.add_submenu("帮助与关于", shortcut="h")
    submenu.add_item("📖 使用说明")
    submenu.add_item("❓ 常见问题")
    submenu.add_item("ℹ️ 关于我们")
    submenu.add_item("📝 版本信息")
    
    menu.add_separator()
    menu.add_item("❌ 退出", shortcut="q")
    
    return menu


def main():
    """主函数"""
    print("\033[2J\033[H")  # 清屏
    
    print("=" * 60)
    print("  交互式CLI菜单工具 - Interactive CLI Menu")
    print("=" * 60)
    print()
    print("  这个工具提供了一个美观的命令行菜单界面，")
    print("  支持键盘导航、子菜单、快捷键等功能。")
    print()
    print("  按 Enter 键进入菜单...")
    input()
    
    # 创建并运行菜单
    menu = create_demo_menu()
    result = menu.run()
    
    print()
    print("=" * 60)
    print(f"  菜单返回结果: {result}")
    print("  感谢使用！")
    print("=" * 60)


if __name__ == "__main__":
    main()
