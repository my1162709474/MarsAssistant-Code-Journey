#!/usr/bin/env python3
"""
📊 进度条生成器 - Progress Bar Generator

支持多种样式的进度条，适用于CLI程序、循环进度显示等场景。

特性:
- 多种动画风格（经典、点、块、蛇形）
- 自定义字符和颜色
- 显示进度百分比和ETA
- 支持线程安全更新

作者: AI Assistant
创建时间: 2026-02-02
"""

import sys
import time
import threading
from typing import Callable, Optional
from datetime import datetime, timedelta


class ProgressBar:
    """多功能进度条类"""
    
    # 预定义动画样式
    STYLES = {
        'classic': ['█', '▒', '░'],
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼'],
        'blocks': ['▏', '▎', '▍', '▌', '▋', '▊', '▉'],
        'snake': ['▖', '▘', '▝', '▗'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'bounce': ['⠁', '⠂', '⠄', '⠂'],
    }
    
    # 颜色代码
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
    }
    
    def __init__(
        self,
        total: int,
        prefix: 'Progress',
        suffix: 'Complete',
        length: 30,
        fill: '█',
        style: str = 'classic',
        color: Optional[str] = None,
        decimals: 1,
        show_eta: bool = True,
    ):
        """
        初始化进度条
        
        Args:
            total: 总任务数
            prefix: 前缀文本
            suffix: 后缀文本
            length: 进度条长度（字符数）
            fill: 填充字符
            style: 动画样式 ('classic', 'dots', 'blocks', 'snake', 'arrow', 'bounce')
            color: 颜色 ('red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white')
            decimals: 百分比小数位数
            show_eta: 是否显示预计完成时间
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.style = style
        self.color = color
        self.decimals = decimals
        self.show_eta = show_eta
        
        self.iteration = 0
        self.start_time = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        
    def start(self):
        """开始进度条动画"""
        self.start_time = datetime.now()
        self._running = True
        
        # 启动动画线程（如果是动画样式）
        if self.style in self.STYLES and self.total == 0:
            self._thread = threading.Thread(target=self._animate_indeterminate)
            self._thread.daemon = True
            self._thread.start()
        
        print(f'\r{self.prefix}', end='', flush=True)
    
    def update(self, n: int = 1, custom_text: Optional[str] = None):
        """
        更新进度
        
        Args:
            n: 增加的迭代次数
            custom_text: 自定义文本（可选）
        """
        with self._lock:
            self.iteration += n
            percent = self._get_progress_percent()
            filled_length = int(self.length * self.iteration // self.total)
            bar = self._create_bar(filled_length)
            
            # 构建显示文本
            if self.color:
                bar = f"{self.COLORS[self.color]}{bar}{self.COLORS['reset']}"
            
            eta = self._get_eta()
            eta_text = f" | ETA: {eta}" if self.show_eta and eta else ""
            
            # 自定义文本或默认格式
            if custom_text:
                display = f'\r{custom_text}'
            else:
                display = f'\r{self.prefix} |{bar}| {percent}% {self.suffix}{eta_text}'
            
            print(display, end='\r', flush=True)
            
            if self.iteration >= self.total:
                print()  # 换行完成
    
    def update_to(self, iteration: int, custom_text: Optional[str] = None):
        """直接设置当前进度"""
        with self._lock:
            self.iteration = iteration
            self.update(0, custom_text)
    
    def _get_progress_percent(self) -> float:
        """计算进度百分比"""
        if self.total == 0:
            return 100.0
        return (self.iteration / self.total * 100)
    
    def _create_bar(self, filled_length: int) -> str:
        """创建进度条字符串"""
        bar = self.fill * filled_length + ' ' * (self.length - filled_length)
        return bar
    
    def _get_eta(self) -> str:
        """计算预计完成时间"""
        if self.total == 0 or self.iteration == 0:
            return '--:--'
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed == 0:
            return '--:--'
        
        rate = self.iteration / elapsed
        remaining = (self.total - self.iteration) / rate
        eta = timedelta(seconds=int(remaining))
        
        # 格式化
        total_seconds = int(remaining)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def _animate_indeterminate(self):
        """不确定进度动画"""
        chars = self.STYLES.get(self.style, ['*'])
        idx = 0
        
        while self._running:
            char = chars[idx % len(chars)]
            bar = char * self.length
            if self.color:
                bar = f"{self.COLORS[self.color]}{bar}{self.COLORS['reset']}"
            print(f'\r{self.prefix} |{bar}| {self.suffix}', end='\r', flush=True)
            idx += 1
            time.sleep(0.1)
    
    def finish(self):
        """完成进度条"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        self.update(self.total)


class AnimatedSpinner:
    """加载动画/旋转器"""
    
    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['|', '/', '-', '\\'],
        'circle': ['◐', '◓', '◑', '◒'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'bar': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
    }
    
    def __init__(
        self,
        message: str = 'Loading',
        style: str = 'dots',
        color: Optional[str] = None,
        fps: float = 10,
    ):
        self.message = message
        self.style = style
        self.color = color
        self.fps = fps
        self.frames = self.SPINNERS.get(style, self.SPINNERS['dots'])
        self._running = False
        self._thread = None
        self._idx = 0
    
    def start(self):
        """开始动画"""
        self._running = True
        self._thread = threading.Thread(target=self._animate)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        """停止动画"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        # 清除当前行
        print('\r' + ' ' * 50 + '\r', end='', flush=True)
    
    def _animate(self):
        """动画循环"""
        interval = 1.0 / self.fps
        
        while self._running:
            frame = self.frames[self._idx % len(self.frames)]
            
            if self.color:
                frame = f"{ProgressBar.COLORS[self.color]}{frame}{ProgressBar.COLORS['reset']}"
            
            print(f'\r{self.message} {frame}', end='\r', flush=True)
            self._idx += 1
            time.sleep(interval)


class ProgressManager:
    """进度管理器 - 支持多任务并行进度"""
    
    def __init__(self, num_tasks: int):
        self.num_tasks = num_tasks
        self.current_task = 0
        self.bars = []
        
    def create_bar(self, **kwargs) -> ProgressBar:
        """为新任务创建进度条"""
        bar = ProgressBar(**kwargs)
        self.bars.append(bar)
        return bar
    
    def update_all(self, increment: int = 1):
        """更新所有进度条"""
        for bar in self.bars:
            if bar.iteration < bar.total:
                bar.update(increment)


def demo_classic_progress():
    """演示经典进度条"""
    print("📊 Classic Progress Bar Demo")
    print("-" * 40)
    
    total = 100
    bar = ProgressBar(total, prefix='Downloading', suffix='Complete', 
                     length=40, color='green')
    
    bar.start()
    for i in range(total + 1):
        time.sleep(0.05)
        bar.update(1)
    bar.finish()
    print()


def demo_multicolor_progress():
    """演示多颜色进度条"""
    print("🎨 Multi-Color Progress Demo")
    print("-" * 40)
    
    colors = ['red', 'yellow', 'green', 'cyan', 'purple']
    
    for i, color in enumerate(colors):
        total = 50
        bar = ProgressBar(total, prefix=f'Task {i+1}', suffix='Done',
                         length=40, color=color)
        bar.start()
        for j in range(total + 1):
            time.sleep(0.02)
            bar.update(1)
        bar.finish()
    
    print()


def demo_with_eta():
    """演示带ETA的进度条"""
    print("⏱️ Progress with ETA Demo")
    print("-" * 40)
    
    total = 100
    bar = ProgressBar(total, prefix='Processing', suffix='Complete',
                     length=40, color='blue', show_eta=True)
    
    bar.start()
    # 模拟不均匀处理时间
    for i in range(total + 1):
        time.sleep(0.1 if i < 50 else 0.05)  # 前面慢，后面快
        bar.update(1)
    bar.finish()
    print()


def demo_spinner():
    """演示加载动画"""
    print("🌀 Loading Spinner Demo")
    print("-" * 40)
    
    spinner = AnimatedSpinner('Loading data', style='dots', color='cyan')
    spinner.start()
    
    # 模拟加载
    time.sleep(3)
    
    spinner.stop()
    print("Data loaded! ✅")
    print()


def demo_indeterminate():
    """演示不确定进度"""
    print("❓ Indeterminate Progress Demo")
    print("-" * 40)
    
    bar = ProgressBar(0, prefix='Searching', suffix='...',
                     length=40, style='dots', color='yellow')
    bar.start()
    
    time.sleep(3)  # 模拟不确定任务
    
    bar._running = False
    print(f'\rSearching... Found! ✅')
    print()


def demo_custom_style():
    """演示自定义样式"""
    print("✨ Custom Style Demo")
    print("-" * 40)
    
    styles = ['classic', 'dots', 'snake', 'arrow', 'bounce']
    
    for style in styles:
        total = 25
        bar = ProgressBar(total, prefix=f'Style: {style}',
                         suffix='Complete', length=30, style=style)
        bar.start()
        for i in range(total + 1):
            time.sleep(0.08)
            bar.update(1)
        bar.finish()
    
    print()


def demo_multitask():
    """演示多任务进度"""
    print("📋 Multi-Task Progress Demo")
    print("-" * 40)
    
    manager = ProgressManager(3)
    
    bar1 = manager.create_bar(total=50, prefix='Task 1',
                             length=30, color='red')
    bar2 = manager.create_bar(total=100, prefix='Task 2',
                             length=30, color='green')
    bar3 = manager.create_bar(total=75, prefix='Task 3',
                             length=30, color='blue')
    
    for bar in [bar1, bar2, bar3]:
        bar.start()
    
    # 模拟并行处理
    while bar1.iteration < 50 or bar2.iteration < 100 or bar3.iteration < 75:
        for bar in [bar1, bar2, bar3]:
            if bar.iteration < bar.total:
                bar.update(1)
        time.sleep(0.05)
    
    print()


def interactive_demo():
    """交互式演示"""
    print("🎮 Interactive Progress Bar Demo")
    print("-" * 40)
    print("Press Enter to start, Ctrl+C to stop...")
    input()
    
    total = 50
    bar = ProgressBar(total, prefix='Interactive', suffix='Press Enter',
                     length=40, color='purple')
    bar.start()
    
    try:
        for i in range(total + 1):
            time.sleep(0.2)
            bar.update(1)
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted!")
        return
    
    print()


def main():
    """主函数 - 运行所有演示"""
    print("=" * 50)
    print("    📊 Progress Bar Generator Demo")
    print("    AI Coding Journey - Day 26")
    print("=" * 50)
    print()
    
    demos = [
        ("Classic Progress Bar", demo_classic_progress),
        ("Multi-Color Progress", demo_multicolor_progress),
        ("Progress with ETA", demo_with_eta),
        ("Loading Spinner", demo_spinner),
        ("Indeterminate Progress", demo_indeterminate),
        ("Custom Styles", demo_custom_style),
        ("Multi-Task Progress", demo_multitask),
        ("Interactive Demo", interactive_demo),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        print(f"[{i}] {name}")
    
    print()
    print("[0] Run All Demos")
    print("[q] Quit")
    print()
    
    choice = input("Select demo: ").strip().lower()
    
    if choice == 'q':
        return
    
    if choice == '0':
        for _, func in demos:
            try:
                func()
            except KeyboardInterrupt:
                print("\n⏹️  Demo stopped by user")
                break
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                demos[idx][1]()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a number!")
    
    print("✨ Demo complete!")


if __name__ == '__main__':
    main()
