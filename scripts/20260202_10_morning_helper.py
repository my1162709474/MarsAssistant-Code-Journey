#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨间效率助手 (Morning Efficiency Helper)
帮助整理一天的任务、生成待办清单、提供激励语录

功能：
1. 任务收集与优先级排序
2. 番茄钟计时
3. 激励语录生成
4. 效率统计

使用方法：
    python morning_helper.py --add "任务描述" --priority high|medium|low
    python morning_helper.py --pomodoro 25
    python morning_helper.py --plan
"""

import json
import random
from datetime import datetime
from pathlib import Path

class MorningEfficiencyHelper:
    def __init__(self, data_file='tasks.json'):
        self.data_file = data_file
        self.tasks = self.load_tasks()
        self.motivational_quotes = [
            "早起的人，已经赢在了起跑线。",
            "每一个清晨都是新的开始。",
            "今天的努力，是明天的勋章。",
            "别让今天的犹豫，变成明天的遗憾。",
            "坚持早起，就是对自己的承诺。",
            "效率不是做得多，而是做得对。",
            "今天的任务，今天完成。",
            "每一个小目标的达成，都是进步的见证。",
        ]
        
    def load_tasks(self):
        """加载任务列表"""
        if Path(self.data_file).exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_tasks(self):
        """保存任务列表"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def add_task(self, description, priority='medium'):
        """添加新任务"""
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'completed': False,
            'completed_at': None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def complete_task(self, task_id):
        """完成任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def get_today_tasks(self):
        """获取今天的任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        return [t for t in self.tasks if t['created_at'].startswith(today) and not t['completed']]
    
    def get_quote(self):
        """获取随机激励语录"""
        return random.choice(self.motivational_quotes)
    
    def generate_plan(self):
        """生成今日计划报告"""
        today_tasks = self.get_today_tasks()
        high_priority = [t for t in today_tasks if t['priority'] == 'high']
        medium_priority = [t for t in today_tasks if t['priority'] == 'medium']
        low_priority = [t for t in today_tasks if t['priority'] == 'low']
        
        report = """
🌅 晨间效率报告 - {datetime}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        report += f"""
📝 今日激励：{self.get_quote()}

📊 任务统计：
   - 高优先级：{len(high_priority)} 个
   - 中优先级：{len(medium_priority)} 个
   - 低优先级：{len(low_priority)} 个
   - 总计：{len(today_tasks)} 个

🔥 今日焦点（高优先级）：
"""
        for i, task in enumerate(high_priority, 1):
            report += f"   {i}. {task['description']}
"
        
        report += "
💡 建议：先完成高优先级任务，保持专注！"
        return report

def pomodoro_timer(minutes=25):
    """番茄钟计时器"""
    import time
    import sys
    
    total_seconds = minutes * 60
    print(f"🍅 番茄钟开始！时长：{minutes} 分钟")
    print("按 Ctrl+C 可提前结束
")
    
    try:
        for remaining in range(total_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer_str = f"⏱️  剩余时间：{mins:02d}:{secs:02d}"
            print(timer_str, end="", flush=True)
            time.sleep(1)
        print("

🎉 番茄钟完成！休息一下，喝杯水吧！
")
    except KeyboardInterrupt:
        print("

⏸️ 番茄钟已暂停。记住：休息也是效率的一部分！
")

if __name__ == "__main__":
    import sys
    
    helper = MorningEfficiencyHelper()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add" or sys.argv[1] == "-a":
            desc = " ".join(sys.argv[2:])
            priority = "medium"
            if "--priority" in sys.argv or "-p" in sys.argv:
                idx = sys.argv.index("--priority") if "--priority" in sys.argv else sys.argv.index("-p")
                if idx + 1 < len(sys.argv):
                    priority = sys.argv[idx + 1]
            task = helper.add_task(desc, priority)
            print(f"✅ 任务已添加：{task['description']} (优先级：{priority})")
            
        elif sys.argv[1] == "--complete" or sys.argv[1] == "-c":
            if len(sys.argv) > 2:
                task_id = int(sys.argv[2])
                if helper.complete_task(task_id):
                    print(f"✅ 任务 {task_id} 已完成！")
                else:
                    print(f"❌ 未找到任务 {task_id}")
                    
        elif sys.argv[1] == "--pomodoro" or sys.argv[1] == "-p":
            minutes = 25
            if len(sys.argv) > 2:
                try:
                    minutes = int(sys.argv[2])
                except ValueError:
                    pass
            pomodoro_timer(minutes)
            
        elif sys.argv[1] == "--plan" or sys.argv[1] == "-P":
            print(helper.generate_plan())
            
        elif sys.argv[1] == "--quote" or sys.argv[1] == "-q":
            print(f"
💬 {helper.get_quote()}
")
            
        else:
            print("用法：")
            print("  python morning_helper.py --add "任务描述" [--priority high|medium|low]")
            print("  python morning_helper.py --complete <任务ID>")
            print("  python morning_helper.py --pomodoro [分钟数]")
            print("  python morning_helper.py --plan")
            print("  python morning_helper.py --quote")
    else:
        print(helper.generate_plan())
