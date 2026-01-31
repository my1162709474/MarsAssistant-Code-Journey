# -*- coding: utf-8 -*-
"""
番茄钟计时器 (Pomodoro Timer)
一个简单而优雅的时间管理工具

使用方法:
    python pomodoro_timer.py              # 交互模式
    python pomodoro_timer.py 25 5         # 自定义工作/休息时间(分钟)
    python pomodoro_timer.py --notify     # 启用系统通知
"""

import time
import sys
import os
import signal
from datetime import datetime

# 颜色定义
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class PomodoroTimer:
    """番茄钟计时器类"""
    
    DEFAULT_WORK_TIME = 25
    DEFAULT_BREAK_TIME = 5
    DEFAULT_LONG_BREAK = 15
    
    WORK = "工作"
    SHORT_BREAK = "短休息"
    LONG_BREAK = "长休息"
    
    def __init__(self, work_time=None, break_time=None, long_break_time=None):
        self.work_time = work_time or self.DEFAULT_WORK_TIME
        self.break_time = break_time or self.DEFAULT_BREAK_TIME
        self.long_break_time = long_break_time or self.DEFAULT_LONG_BREAK
        
        self.current_session = 0
        self.total_sessions = 0
        self.is_running = False
        self.is_paused = False
        self.current_state = self.WORK
        self.remaining_seconds = 0
        self.start_time = None
        
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        print(f"\n{Colors.YELLOW}计时器已暂停。按 Enter 继续，Ctrl+C 退出...{Colors.RESET}")
        self.is_paused = True
        input()
        self.is_paused = False
        self._countdown()
    
    def _format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _notify(self, title, message):
        if sys.platform == "darwin":
            os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
        elif sys.platform == "linux":
            os.system(f"notify-send \"{title}\" \"{message}\"")
    
    def _play_sound(self):
        if sys.platform == "darwin":
            os.system("afplay /System/Library/Sounds/Blow.aiff")
        elif sys.platform == "linux":
            print("\a")
    
    def _countdown(self):
        while self.remaining_seconds > 0 and self.is_running:
            if self.is_paused:
                time.sleep(1)
                continue
            
            elapsed = (datetime.now() - self.start_time).total_seconds()
            total_seconds = self.work_time * 60 if self.current_state == self.WORK else self.break_time * 60
            self.remaining_seconds = max(0, total_seconds - elapsed)
            
            self._display_status()
            time.sleep(1)
    
    def _display_status(self):
        os.system("cls" if os.name == "nt" else "clear")
        
        emoji = "🍅" if self.current_state == self.WORK else "☕"
        
        if self.current_state == self.WORK:
            color = Colors.RED
        elif self.current_state == self.SHORT_BREAK:
            color = Colors.GREEN
        else:
            color = Colors.CYAN
        
        print(f"{color}{Colors.BOLD}")
        print("====================================")
        print(f"       {emoji} 番茄钟计时器 {emoji}")
        print("====================================")
        print(f"  状态: {self.current_state}")
        print(f"  剩余: {self._format_time(self.remaining_seconds)}")
        print(f"  番茄: total_ser��[��sions} 个")
        print("====================================")
        print(f"{Colors.RESET}")
    
    def start(self, sessions=4, notify=False):
        self.is_running = True
        
        print(f"{Colors.CYAN}开始番茄钟之旅！连续工作 {sessions} 个周期{Colors.RESET}")
        print(f"{Colors.YELLOW}按 Ctrl+C 暂停...{Colors.RESET}\n")
        time.sleep(2)
        
        for session in range(1, sessions + 1):
            if not self.is_running:
                break
            
            self.current_session = session
            self.current_state = self.WORK
            self.start_time = datetime.now()
            self.remaining_seconds = self.work_time * 60
            
            print(f"\n{Colors.RED}第 {session} 个番茄钟 ({self.work_time} 分钟){Colors.RESET}")
            self._countdown()
            
            if self.is_running:
                self.total_sessions += 1
                print(f"\n{Colors.GREEN}第 {session} 个番茄钟完成！{Colors.RESET}")
                
                if notify:
                    self._notify("番茄钟完成", f"第 {session} 个完成")
                self._play_sound()
                
                if session < sessions:
                    self.current_state = self.SHORT_BREAK
                    self.start_time = datetime.now()
                    self.remaining_seconds = self.break_time * 60
                    print(f"\n{Colors.BLUE}开始短休息 ({self.break_time} 分钟){Colors.RESET}")
                    self._countdown()
                else:
                    self.current_state = self.LONG_BREAK
                    self.start_time = datetime.now()
                    self.remaining_seconds = self.long_break_time * 60
                    print(f"\n{Colors.PURPLE}开始长休息 ({self.long_break_time} 分钟){Colors.RESET}")
                    self._countdown()
        
        self.is_running = False
        print(f"\n{Colors.GREEN}完成！共 {self.total_sessions} 个番茄钟{Colors.RESET}")
    
    def stop(self):
        self.is_running = False
        print(f"\n{Colors.YELLOW}计时器已停止{Colors.RESET}")


def main():
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    if not args:
        print("番茄钟计时器 - 交互模式")
        try:
            work = input("工作时间 (分钟, 默认 25): ").strip()
            work = int(work) if work else 25
            break_t = input("休息时间 (分钟, 默认 5): ").strip()
            break_t = int(break_t) if break_t else 5
            notify = input("启用系统通知? (y/N): ").strip().lower() == "y"
            
            timer = PomodoroTimer(work_time=work, break_time=break_t)
            timer.start(notify=notify)
        except (ValueError, KeyboardInterrupt):
            print("\n程序退出")
    else:
        try:
            work_time = int(args[0]) if args[0].lstrip("-").isdigit() else None
            break_time = int(args[1]) if len(args) > 1 and args[1].lstrip("-").isdigit() else None
            notify = "--notify" in args
            
            timer = PomodoroTimer(work_time=work_time, break_time=break_time)
            timer.start(notify=notify)
        except ValueError:
            print("用法: python pomodoro_timer.py [工作时间] [休息时间] [--notify]")


if __name__ == "__main__":
    main()
