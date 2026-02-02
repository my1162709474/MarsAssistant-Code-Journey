#!/usr/bin/env python3
"""
🎯 Day 39: 实时文件系统监控器
==============================
实时监控目录/文件的创建、修改、删除事件
支持正则过滤、定时报告、多种输出格式

功能特性:
- 🔍 实时文件事件监控
- 📊 定时汇总报告
- 🎯 正则表达式过滤
- 📈 事件统计分析
- 💾 支持多种输出格式

作者: AI Assistant
日期: 2026-02-02
"""

import os
import sys
import time
import json
import re
import argparse
import threading
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from enum import Enum
from typing import Optional, Callable, Dict, List, Set, Any
import hashlib


class EventType(Enum):
    """文件事件类型"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    ACCESSED = "accessed"


class FileMonitor:
    """文件系统监控器"""
    
    def __init__(self, 
                 path: str,
                 recursive: bool = True,
                 event_types: Optional[Set[EventType]] = None,
                 pattern: Optional[str] = None,
                 ignore_pattern: Optional[str] = None):
        self.path = Path(path)
        self.recursive = recursive
        self.event_types = event_types or {EventType.CREATED, EventType.MODIFIED, EventType.DELETED}
        self.pattern = re.compile(pattern) if pattern else None
        self.ignore_pattern = re.compile(ignore_pattern) if ignore_pattern else None
        
        self.events: deque = deque(maxlen=10000)
        self.stats: Dict[str, Any] = {
            'total_events': 0,
            'by_type': defaultdict(int),
            'by_extension': defaultdict(int),
            'by_hour': defaultdict(int),
            'largest_files': [],
            'most_active_files': defaultdict(int),
            'start_time': None,
            'end_time': None
        }
        self._running = False
        self._lock = threading.Lock()
        
    def _should_watch(self, filepath: Path) -> bool:
        """检查是否应该监控该文件"""
        # 检查忽略模式
        if self.ignore_pattern and self.ignore_pattern.search(str(filepath)):
            return False
        
        # 检查包含模式
        if self.pattern and not self.pattern.search(str(filepath)):
            return False
        
        return True
    
    def _get_event_type(self, old_state: Optional[Dict], new_state: Optional[Dict]) -> Optional[EventType]:
        """确定事件类型"""
        if old_state is None and new_state is not None:
            return EventType.CREATED
        elif old_state is not None and new_state is None:
            return EventType.DELETED
        elif old_state is not None and new_state is not None:
            if old_state['size'] != new_state['size'] or old_state['mtime'] != new_state['mtime']:
                return EventType.MODIFIED
        return None
    
    def _get_file_state(self, filepath: Path) -> Optional[Dict]:
        """获取文件当前状态"""
        try:
            if filepath.is_file():
                stat = filepath.stat()
                return {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'ctime': stat.st_ctime,
                    'atime': stat.st_atime,
                    'hash': self._calculate_hash(filepath)
                }
        except (PermissionError, FileNotFoundError):
            pass
        return None
    
    def _calculate_hash(self, filepath: Path, chunk_size: int = 8192) -> str:
        """计算文件哈希值"""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]
        except Exception:
            return ""
    
    def _compare_states(self, old_states: Dict[str, Dict], new_states: Dict[str, Dict]) -> List[Dict]:
        """比较文件状态变化"""
        events = []
        
        # 检查新建和修改
        for filepath, new_state in new_states.items():
            old_state = old_states.get(filepath)
            event_type = self._get_event_type(old_state, new_state)
            
            if event_type and self._should_watch(Path(filepath)):
                events.append({
                    'type': event_type.value,
                    'path': filepath,
                    'timestamp': datetime.now().isoformat(),
                    'size': new_state.get('size', 0),
                    'size_formatted': self._format_size(new_state.get('size', 0))
                })
        
        # 检查删除
        for filepath, old_state in old_states.items():
            if filepath not in new_states:
                if self._should_watch(Path(filepath)):
                    events.append({
                        'type': EventType.DELETED.value,
                        'path': filepath,
                        'timestamp': datetime.now().isoformat(),
                        'size': old_state.get('size', 0),
                        'size_formatted': self._format_size(old_state.get('size', 0))
                    })
        
        return events
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def scan_directory(self) -> Dict[str, Dict]:
        """扫描目录获取所有文件状态"""
        states = {}
        
        if self.path.is_file():
            files = [self.path]
        else:
            files = self.path.rglob('*') if self.recursive else self.path.glob('*')
        
        for filepath in files:
            if filepath.is_file():
                state = self._get_file_state(filepath)
                if state:
                    states[str(filepath)] = state
        
        return states
    
    def start(self, interval: float = 1.0, callback: Optional[Callable] = None):
        """开始监控"""
        self._running = True
        self.stats['start_time'] = datetime.now()
        
        old_states = self.scan_directory()
        
        def monitor_loop():
            while self._running:
                try:
                    time.sleep(interval)
                    new_states = self.scan_directory()
                    events = self._compare_states(old_states, new_states)
                    
                    if events:
                        with self._lock:
                            for event in events:
                                self.events.append(event)
                                self._update_stats(event)
                        
                        if callback:
                            callback(events)
                    
                    old_states = new_states
                    
                except Exception as e:
                    print(f"监控错误: {e}", file=sys.stderr)
        
        self._thread = threading.Thread(target=monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止监控"""
        self._running = False
        self.stats['end_time'] = datetime.now()
        if hasattr(self, '_thread'):
            self._thread.join(timeout=2)
    
    def _update_stats(self, event: Dict):
        """更新统计信息"""
        self.stats['total_events'] += 1
        self.stats['by_type'][event['type']] += 1
        
        # 按扩展名统计
        ext = Path(event['path']).suffix.lower()
        self.stats['by_extension'][ext or '(无)'] += 1
        
        # 按小时统计
        hour = datetime.fromisoformat(event['timestamp']).hour
        self.stats['by_hour'][hour] += 1
        
        # 活跃文件统计
        self.stats['most_active_files'][event['path']] += 1
        
        # 大文件追踪
        size = event.get('size', 0)
        self.stats['largest_files'].append({
            'path': event['path'],
            'size': size,
            'type': event['type']
        })
        self.stats['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        self.stats['largest_files'] = self.stats['largest_files'][:10]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            stats = dict(self.stats)
        
        # 计算运行时长
        if stats['start_time']:
            if stats['end_time']:
                duration = stats['end_time'] - stats['start_time']
            else:
                duration = datetime.now() - stats['start_time']
            stats['duration_seconds'] = duration.total_seconds()
        
        # 计算事件率
        if stats.get('duration_seconds', 0) > 0:
            stats['events_per_second'] = stats['total_events'] / stats['duration_seconds']
        
        return stats
    
    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """获取最近事件"""
        with self._lock:
            return list(self.events)[-count:]


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_summary(stats: Dict, events: List[Dict]) -> str:
        """生成汇总报告"""
        lines = [
            "=" * 60,
            "📊 文件系统监控报告",
            "=" * 60,
            f"⏰ 监控时长: {stats.get('duration_seconds', 0):.1f} 秒",
            f"📁 总事件数: {stats['total_events']}",
            f"⚡ 事件速率: {stats.get('events_per_second', 0):.2f} 事件/秒",
            "",
            "📈 事件类型分布:",
        ]
        
        for event_type, count in stats['by_type'].items():
            percentage = (count / stats['total_events'] * 100) if stats['total_events'] > 0 else 0
            bar = '█' * int(percentage / 5)
            lines.append(f"  {event_type:12s}: {count:5d} ({percentage:5.1f}%) {bar}")
        
        lines.extend(["", "📁 文件扩展名分布:"])
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"  {ext:15s}: {count:5d}")
        
        lines.extend(["", "🔥 最活跃文件 (Top 5):"])
        for path, count in sorted(stats['most_active_files'].items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"  {count:3d} 次 - {path}")
        
        if events:
            lines.extend(["", "📋 最近事件:"])
            for event in events[-5:]:
                emoji = {'created': '🆕', 'modified': '📝', 'deleted': '🗑️', 'moved': '➡️', 'accessed': '👁️'}
                e = emoji.get(event['type'], '📄')
                lines.append(f"  {e} {event['type']:8s} - {event['path']}")
        
        lines.append("=" * 60)
        return '\n'.join(lines)
    
    @staticmethod
    def generate_json(stats: Dict, events: List[Dict]) -> str:
        """生成JSON格式报告"""
        return json.dumps({
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'recent_events': events
        }, indent=2, ensure_ascii=False)


def create_sample_monitor():
    """创建示例文件用于测试"""
    sample_dir = Path("/tmp/file_monitor_test")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建测试文件
    test_files = [
        sample_dir / "test1.txt",
        sample_dir / "test2.txt", 
        sample_dir / "data.json",
        sample_dir / "notes.md"
    ]
    
    for i, f in enumerate(test_files):
        f.write_text(f"测试文件 {i+1}\n创建时间: {datetime.now()}\n")
    
    return sample_dir


def interactive_mode():
    """交互式监控模式"""
    print("🎯 文件系统监控器 - 交互模式")
    print("=" * 50)
    
    path = input("监控路径 (直接回车使用 /tmp): ").strip() or "/tmp"
    recursive = input("递归监控? (y/n, 默认y): ").strip().lower() != 'n'
    interval = float(input("扫描间隔秒数 (默认1.0): ").strip() or "1.0")
    
    if not os.path.exists(path):
        print(f"❌ 路径不存在: {path}")
        return
    
    monitor = FileMonitor(path, recursive=recursive)
    
    def on_events(events):
        print(f"\n📥 检测到 {len(events)} 个事件:")
        for event in events[-3:]:  # 只显示最近3个
            emoji = {'created': '🆕', 'modified': '📝', 'deleted': '🗑️'}
            e = emoji.get(event['type'], '📄')
            print(f"  {e} {event['type']:8s} | {event['size_formatted']:8s} | {event['path'][-50:]}")
    
    print(f"\n✅ 开始监控: {path}")
    print("💡 按 Ctrl+C 停止监控并生成报告\n")
    
    monitor.start(interval=interval, callback=on_events)
    
    try:
        while True:
            time.sleep(5)
            stats = monitor.get_stats()
            print(f"\r⏱️ 运行 {stats.get('duration_seconds', 0):.0f}s | 📊 {stats['total_events']} 事件 | ⚡ {stats.get('events_per_second', 0):.1f}/s", end='', flush=True)
    except KeyboardInterrupt:
        print("\n\n🛑 停止监控...")
        monitor.stop()
        
        events = monitor.get_recent_events(50)
        stats = monitor.get_stats()
        
        print("\n" + ReportGenerator.generate_summary(stats, events))


def daemon_mode(path: str, output: str = "text"):
    """守护进程模式 - 持续监控并定期报告"""
    print(f"🚀 启动守护进程模式: {path}")
    
    if not os.path.exists(path):
        print(f"❌ 路径不存在: {path}")
        return
    
    monitor = FileMonitor(path)
    monitor.start(interval=1.0)
    
    try:
        while True:
            time.sleep(60)  # 每分钟报告一次
            stats = monitor.get_stats()
            events = monitor.get_recent_events(100)
            
            if output == "json":
                print(ReportGenerator.generate_json(stats, events))
            else:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] " + ReportGenerator.generate_summary(stats, events))
            
    except KeyboardInterrupt:
        print("\n🛑 停止监控...")
        monitor.stop()
        print("\n" + ReportGenerator.generate_summary(monitor.get_stats(), monitor.get_recent_events()))


def watch_created_files():
    """仅监控新创建的文件"""
    path = input("监控路径: ").strip()
    if not os.path.exists(path):
        print(f"❌ 路径不存在: {path}")
        return
    
    print(f"👀 仅监控新创建的文件: {path}")
    
    existing_files = set()
    for f in Path(path).rglob('*'):
        if f.is_file():
            existing_files.add(str(f))
    
    monitor = FileMonitor(path, event_types={EventType.CREATED})
    created_files = []
    
    def on_events(events):
        for event in events:
            if event['type'] == 'created':
                created_files.append(event)
                print(f"🆕 新文件: {event['path']} ({event['size_formatted']})")
    
    monitor.start(interval=0.5, callback=on_events)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print(f"\n📊 共发现 {len(created_files)} 个新文件")


def main():
    parser = argparse.ArgumentParser(
        description="🎯 实时文件系统监控器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                              # 交互模式
  %(prog)s --path /tmp --daemon         # 守护进程模式
  %(prog)s --path /tmp --watch-new      # 仅监控新文件
  %(prog)s --path /tmp --report 60      # 每60秒输出报告
  %(prog)s --create-sample              # 创建测试环境
        """
    )
    
    parser.add_argument('-p', '--path', default='/tmp', help='监控路径 (默认: /tmp)')
    parser.add_argument('-i', '--interval', type=float, default=1.0, help='扫描间隔秒数 (默认: 1.0)')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归监控子目录')
    parser.add_argument('--pattern', help='正则表达式过滤模式')
    parser.add_argument('--ignore', help='正则表达式忽略模式')
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--daemon', action='store_true', help='守护进程模式 (持续监控)')
    mode_group.add_argument('--watch-new', action='store_true', help='仅监控新创建的文件')
    mode_group.add_argument('--report', type=int, metavar='SECONDS', help='定时报告模式')
    mode_group.add_argument('--create-sample', action='store_true', help='创建测试样本目录')
    mode_group.add_argument('--once', action='store_true', help='单次扫描对比')
    
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--json', action='store_true', help='JSON输出 (等同于 --output json)')
    
    args = parser.parse_args()
    
    if args.json:
        args.output = 'json'
    
    if args.create_sample:
        sample_dir = create_sample_dir()
        print(f"✅ 测试目录: {sample_dir}")
        print("📝 目录中有4个测试文件，可以开始监控测试")
        return
    
    path = args.path
    if not os.path.exists(path):
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)
    
    if args.watch_new:
        watch_created_files()
        return
    
    if args.daemon or args.report:
        daemon_mode(path, args.output)
        return
    
    if args.once:
        # 单次扫描模式
        print(f"🔍 单次扫描: {path}")
        monitor = FileMonitor(path, recursive=args.recursive, pattern=args.pattern, ignore_pattern=args.ignore)
        states = monitor.scan_directory()
        print(f"📁 发现 {len(states)} 个文件")
        for f, state in list(states.items())[:10]:
            print(f"  {f}: {monitor._format_size(state['size'])}")
        return
    
    # 默认交互模式
    interactive_mode()


if __name__ == "__main__":
    main()
