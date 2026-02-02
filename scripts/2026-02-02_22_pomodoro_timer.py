#!/usr/bin/env python3
"""
番茄钟计时器 (Day 22)

一个智能番茄钟工具，帮助你管理工作和休息时间。

功能:
- 番茄工作法计时（默认25分钟）
- 智能休息提醒
- 工作统计
- 自定义时长
- 桌面通知
"""

import time
import sys
import os
from datetime import datetime, timedelta
from enum import Enum
import json
import threading

# 尝试导入通知库
try:
    from plyer import notification
    HAS_NOTIFICATION = True
except ImportError:
    HAS_NOTIFICATION = False


class PomodoroState(Enum):
    IDLE = "空闲"
    WORK = "工作中"
    SHORT_BREAK = "短休息"
    LONG_BREAK = "长休息"


class PomodoroTimer:
    """番茄钟计时器类"""
    
    def __init__(self, work_minutes=25, short_break_minutes=5, long_break_minutes=15):
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.current_state = PomodoroState.IDLE
        self.time_remaining = 0
        self.total_work_sessions = 0
        self.total_work_minutes = 0
        self.is_running = False
        self.is_paused = False
        self.current_session_start = None
        self.history_file = "pomodoro_history.json"
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.total_work_sessions = data.get('total_sessions', 0)
                    self.total_work_minutes = data.get('total_minutes', 0)
            except:
                self.total_work_sessions = 0
                self.total_work_minutes = 0
    
    def save_history(self):
        """保存历史记录"""
        data = {
            'total_sessions': self.total_work_sessions,
            'total_minutes': self.total_work_minutes,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def get_state_info(self):
        """获取当前状态信息"""
        state_names = {
            PomodoroState.IDLE: "🛋️ 空闲 - 按 Enter 开始",
            PomodoroState.WORK: f"💼 工作中 - 剩余 {self.format_time(self.time_remaining)}",
            PomodoroState.SHORT_BREAK: f"☕ 短休息 - 剩余 {self.format_time(self.time_remaining)}",
            PomodoroState.LONG_BREAK: f"🌟 长休息 - 剩余 {self.format_time(self.time_remaining)}"
        }
        return state_names.get(self.current_state, "未知状态")
    
    def show_notification(self, title, message):
        """显示桌面通知"""
        if HAS_NOTIFICATION:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="🍅 Pomodoro Timer",
                    timeout=10
                )
            except:
                pass
    
    def send_notification(self):
        """发送完成通知"""
        if self.current_state == PomodoroState.WORK:
            self.show_notification("🍅 工作完成！", f"太棒了！你完成了 {self.work_minutes} 分钟的工作。现在休息一下吧。")
        elif self.current_state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            self.show_notification("☕ 休息结束！", "准备好开始下一个番茄钟了吗？")
    
    def play_sound(self):
        """播放提示音"""
        # 简单的系统蜂鸣
        try:
            if sys.platform == 'darwin':
                os.system('say "Time is up"')
            elif sys.platform == 'win32':
                import winsound
                winsound.Beep(1000, 500)
        except:
            pass
    
    def timer_loop(self):
        """计时器主循环"""
        while self.is_running and self.time_remaining > 0:
            if not self.is_paused:
                time.sleep(1)
                self.time_remaining -= 1
            else:
                time.sleep(0.1)
        
        if self.is_running:
            self.complete_session()
    
    def start_work(self):
        """开始工作"""
        if self.is_running and self.current_state == PomodoroState.WORK:
            return
        
        self.current_state = PomodoroState.WORK
        self.time_remaining = self.work_minutes * 60
        self.current_session_start = datetime.now()
        self.is_running = True
        self.is_paused = False
        self.start_timer_thread()
    
    def start_short_break(self):
        """开始短休息"""
        self.current_state = PomodoroState.SHORT_BREAK
        self.time_remaining = self.short_break_minutes * 60
        self.is_paused = False
    
    def start_long_break(self):
        """开始长休息"""
        self.current_state = PomodoroState.LONG_BREAK
        self.time_remaining = self.long_break_minutes * 60
        self.is_paused = False
    
    def start_timer_thread(self):
        """启动计时器线程"""
        thread = threading.Thread(target=self.timer_loop)
        thread.daemon = True
        thread.start()
    
    def pause(self):
        """暂停"""
        if self.current_state != PomodoroState.IDLE:
            self.is_paused = not self.is_paused
            return self.is_paused
        return False
    
    def skip(self):
        """跳过当前阶段"""
        self.complete_session()
    
    def complete_session(self):
        """完成当前阶段"""
        self.is_running = False
        
        if self.current_state == PomodoroState.WORK:
            self.total_work_sessions += 1
            self.total_work_minutes += self.work_minutes
            self.save_history()
            self.send_notification()
            self.play_sound()
            
            # 自动进入休息
            if self.total_work_sessions % 4 == 0:
                self.start_long_break()
            else:
                self.start_short_break()
        else:
            self.send_notification()
            self.play_sound()
            # 进入工作状态
            self.start_work()
        
        self.is_running = True
        self.start_timer_thread()
    
    def reset(self):
        """重置"""
        self.is_running = False
        self.is_paused = False
        self.current_state = PomodoroState.IDLE
        self.time_remaining = 0
    
    def get_statistics(self):
        """获取统计信息"""
        return {
            "今日番茄钟数": self.total_work_sessions,
            "总工作时长（分钟）": self.total_work_minutes,
            "相当于": f"{self.total_work_minutes // 60}小时{self.total_work_minutes % 60}分钟"
        }
    
    def interactive_mode(self):
        """交互模式"""
        print("\n🍅 欢迎使用番茄钟计时器！")
        print("=" * 40)
        print("命令:")
        print("  [Enter] - 开始/暂停/继续")
        print("  [p]     - 暂停/继续")
        print("  [s]     - 跳过当前阶段")
        print("  [r]     - 重置")
        print("  [t]     - 设置时长")
        print("  [i]     - 查看统计")
        print("  [q]     - 退出")
        print("=" * 40)
        
        while True:
            print(f"\n{self.get_state_info()}")
            print(f"总完成: {self.total_work_sessions} 个番茄钟 ({self.total_work_minutes} 分钟)")
            
            command = input("\n请输入命令: ").strip().lower()
            
            if command == '':
                if self.current_state == PomodoroState.IDLE:
                    self.start_work()
                elif self.is_paused:
                    self.pause()
                else:
                    print("计时器正在运行中...")
            elif command == 'p':
                if self.current_state != PomodoroState.IDLE:
                    paused = self.pause()
                    if paused:
                        print("⏸️  已暂停")
                    else:
                        print("▶️  继续")
                else:
                    print("计时器未运行")
            elif command == 's':
                if self.current_sate != PomodoroState.IDLE:
                    self.skip(
            elif command == 'r':
                self.reset()
                print("\n🔄  已重置")
            elif command == 't':
                self.set_duration()
            elif command == 'i':
                stats = self.get_statistics()
                print("\n📊 统计信息:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            elif command == 'q':
                print("\n👋 感谢使用番茄钟！再见！")
                break
            else:
                print("未知命令")
            
            time.sleep(0.1)
    
    def set_duration(self):
        """设置时长"""
        try:
            print("\n⚙️  设置时长（分钟）")
            work = int(input(f"  工作时镴 [{self.work_minutes}]: ") or self.work_minutes)
            short = int(input(f"  短休息 [{self.short_break_minutes}]: ") or self.short_break_minutes)
            long = int(input(f"  长休息 [{self.long_break_minutes}]: ") or self.long_break_minutes)
            
            self.work_minutes = work
            self.short_break_minutes = short
            self.long_break_minutes = long
            
            print(f"✅ 已设置: 工作{work}分钟, 短休{short}分钟, 长休{long}分钟")
        except ValueError:
            print("❌ 无效输入")


def main():
    """主函数"""
    timer = PomodoroTimer()
    timer.interactive_mode()


if __name__ == "__main__":
    main()
