#!/usr/bin/env python3
"""
智能日志分析器 - Smart Log Analyzer
=====================================

功能:
- 支持多种日志格式 (Apache/Nginx/Syslog/JSON/自定义)
- 实时日志解析和统计分析
- 错误模式检测和告警
- 可视化报告生成
- 实时流式分析

作者: AI Coding Journey
日期: 2026-02-02
"""

import re
import json
import gzip
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import sys

# ANSI颜色代码
COLORS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m', 
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
}

def colorize(text: str, color: str) -> str:
    """为文本添加颜色"""
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"

@dataclass
class LogEntry:
    """日志条目数据结构"""
    timestamp: datetime
    level: str
    source: str
    message: str
    raw: str
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class LogStats:
    """日志统计信息"""
    total_lines: int = 0
    total_size: int = 0
    level_counts: Dict[str, int] = field(default_factory=dict)
    source_counts: Dict[str, int] = field(default_factory=dict)
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    top_messages: List[Tuple[str, int]] = field(default_factory=list)
    error_patterns: List[str] = field(default_factory=list)
    time_range: Tuple[datetime, datetime] = None

class LogParser:
    """日志解析器基类"""
    
    def parse(self, line: str) -> Optional[LogEntry]:
        raise NotImplementedError
    
    @staticmethod
    def detect_format(log_line: str) -> str:
        """自动检测日志格式"""
        patterns = {
            'apache_combined': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} - - \[',
            'syslog': r'\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}',
            'json': r'^\{.*\}$',
            'nginx': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} - \w+ \[',
        }
        
        for fmt, pattern in patterns.items():
            if re.search(pattern, log_line):
                return fmt
        return 'custom'

class ApacheParser(LogParser):
    """Apache/Nginx日志解析器"""
    
    APACHE_PATTERN = re.compile(
        r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+-\s+-\s+\['
        r'(?P<timestamp>.*?)\]\s+'
        r'"(?P<request>.*?)"\s+'
        r'(?P<status>\d{3})\s+'
        r'(?P<bytes>\d+)\s+'
        r'"(?P<referer>.*?)"\s+'
        r'"(?P<user_agent>.*?)"'
    )
    
    def parse(self, line: str) -> Optional[LogEntry]:
        match = self.APACHE_PATTERN.match(line)
        if not match:
            return None
        
        try:
            timestamp = datetime.strptime(
                match.group('timestamp'), 
                '%d/%b/%Y:%H:%M:%S %z'
            )
        except ValueError:
            timestamp = datetime.now()
        
        return LogEntry(
            timestamp=timestamp,
            level=self._status_to_level(int(match.group('status'))),
            source=match.group('ip'),
            message=match.group('request'),
            raw=line,
            extra={
                'status': match.group('status'),
                'bytes': match.group('bytes'),
                'referer': match.group('referer'),
                'user_agent': match.group('user_agent')[:100]
            }
        )
    
    def _status_to_level(self, status: int) -> str:
        if status < 300: return 'INFO'
        if status < 400: return 'WARNING'  
        if status < 500: return 'ERROR'
        return 'CRITICAL'

class SyslogParser(LogParser):
    """Syslog解析器"""
    
    SYSLOG_PATTERN = re.compile(
        r'(?P<timestamp>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<process>\S+?)(?:\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)'
    )
    
    LEVEL_MAP = {
        'emerg': 'CRITICAL', 'alert': 'CRITICAL', 'crit': 'ERROR',
        'err': 'ERROR', 'warning': 'WARNING', 'warn': 'WARNING', 
        'notice': 'INFO', 'info': 'INFO', 'debug': 'DEBUG'
    }
    
    def parse(self, line: str) -> Optional[LogEntry]:
        match = self.SYSLOG_PATTERN.match(line)
        if not match:
            return None
        
        try:
            timestamp = datetime.strptime(
                match.group('timestamp'), 
                '%b %d %H:%M:%S'
            )
            timestamp = timestamp.replace(year=datetime.now().year)
        except ValueError:
            timestamp = datetime.now()
        
        process = match.group('process')
        message = match.group('message')
        
        # 检测日志级别
        level = 'INFO'
        for key, level_name in self.LEVEL_MAP.items():
            if key in message.lower()[:20]:
                level = level_name
                break
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            source=f"{match.group('hostname')}/{process}",
            message=message,
            raw=line,
            extra={'pid': match.group('pid')}
        )

class JSONParser(LogParser):
    """JSON日志解析器"""
    
    def parse(self, line: str) -> Optional[LogEntry]:
        try:
            data = json.loads(line.strip())
            return LogEntry(
                timestamp=datetime.fromisoformat(
                    data.get('timestamp', datetime.now().isoformat())
                ),
                level=data.get('level', data.get('severity', 'INFO')),
                source=data.get('source', data.get('service', 'unknown')),
                message=data.get('message', data.get('msg', '')),
                raw=line,
                extra={k: v for k, v in data.items() 
                      if k not in ['timestamp', 'level', 'source', 'message']}
            )
        except json.JSONDecodeError:
            return None

class CustomParser(LogParser):
    """自定义格式解析器"""
    
    def __init__(self, pattern: str, timestamp_format: str = None):
        self.pattern = re.compile(pattern)
        self.timestamp_format = timestamp_format
    
    def parse(self, line: str) -> Optional[LogEntry]:
        match = self.pattern.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        timestamp = datetime.now()
        
        if 'timestamp' in groups and self.timestamp_format:
            try:
                timestamp = datetime.strptime(
                    groups['timestamp'], 
                    self.timestamp_format
                )
            except ValueError:
                pass
        
        return LogEntry(
            timestamp=timestamp,
            level=groups.get('level', 'INFO'),
            source=groups.get('source', 'unknown'),
            message=groups.get('message', line),
            raw=line,
            extra={k: v for k, v in groups.items() 
                  if k not in ['timestamp', 'level', 'source', 'message']}
        )

class SmartLogAnalyzer:
    """智能日志分析器主类"""
    
    def __init__(self):
        self.stats = LogStats()
        self.entries: List[LogEntry] = []
        self.errors: List[LogEntry] = []
    
    def load_file(self, filepath: str, format: str = 'auto') -> int:
        """加载日志文件"""
        count = 0
        parser = self._get_parser(filepath, format)
        
        open_func = gzip.open if filepath.endswith('.gz') else open
        
        with open_func(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                entry = parser.parse(line) if parser else None
                if entry:
                    self.entries.append(entry)
                    count += 1
                    
                    if entry.level in ['ERROR', 'CRITICAL', 'WARNING']:
                        self.errors.append(entry)
        
        self._calculate_stats()
        return count
    
    def _get_parser(self, filepath: str, format: str) -> LogParser:
        """获取合适的解析器"""
        if format != 'auto':
            return self._create_parser(format)
        
        # 读取第一行检测格式
        open_func = gzip.open if filepath.endswith('.gz') else open
        with open_func(filepath, 'r') as f:
            first_line = f.readline()
        
        detected = LogParser.detect_format(first_line)
        return self._create_parser(detected)
    
    def _create_parser(self, format: str) -> LogParser:
        """创建指定格式的解析器"""
        parsers = {
            'apache': ApacheParser(),
            'apache_combined': ApacheParser(),
            'nginx': ApacheParser(),
            'syslog': SyslogParser(),
            'json': JSONParser(),
        }
        return parsers.get(format, SyslogParser())
    
    def _calculate_stats(self):
        """计算统计信息"""
        if not self.entries:
            return
        
        self.stats.total_lines = len(self.entries)
        
        # 级别统计
        for entry in self.entries:
            self.stats.level_counts[entry.level] = \
                self.stats.level_counts.get(entry.level, 0) + 1
            self.stats.source_counts[entry.source] = \
                self.stats.source_counts.get(entry.source, 0) + 1
            self.stats.hourly_distribution[entry.timestamp.hour] = \
                self.stats.hourly_distribution.get(entry.timestamp.hour, 0) + 1
        
        # 时间范围
        timestamps = [e.timestamp for e in self.entries]
        self.stats.time_range = (min(timestamps), max(timestamps))
        
        # 热门消息
        messages = [e.message[:100] for e in self.entries]
        self.stats.top_messages = Counter(messages).most_common(10)
        
        # 错误模式检测
        self._detect_error_patterns()
    
    def _detect_error_patterns(self):
        """检测常见错误模式"""
        error_patterns = [
            (r'connection.*refused', '连接被拒绝'),
            (r'timeout', '超时错误'),
            (r'permission.*denied', '权限拒绝'),
            (r'null.*pointer', '空指针异常'),
            (r'memory.*exhausted', '内存耗尽'),
            (r'disk.*full', '磁盘空间不足'),
            (r'segmentation.*fault', '段错误'),
            (r'key.*error', '键值错误'),
            (r'import.*error', '导入错误'),
            (r'syntax.*error', '语法错误'),
        ]
        
        error_messages = ' '.join([e.message.lower() for e in self.errors])
        
        for pattern, description in error_patterns:
            if re.search(pattern, error_messages):
                self.stats.error_patterns.append(description)
    
    def generate_report(self, output_format: str = 'text') -> str:
        """生成分析报告"""
        if output_format == 'json':
            return self._generate_json_report()
        return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """生成文本格式报告"""
        lines = [
            colorize("=" * 60, 'CYAN'),
            colorize("📊 智能日志分析报告", 'BOLD'),
            colorize("=" * 60, 'CYAN'),
            "",
            colorize("📈 概览统计", 'BOLD'),
            "-" * 40,
            f"  总日志行数: {colorize(str(self.stats.total_lines), 'GREEN')}",
            f"  错误数量: {colorize(str(len(self.errors)), 'RED')}",
            f"  错误率: {colorize(f'{len(self.errors)/max(1,self.stats.total_lines)*100:.2f}%', 'YELLOW')}",
            "",
        ]
        
        if self.stats.time_range:
            start, end = self.stats.time_range
            lines.extend([
                f"  时间范围: {start} 至 {end}",
                "",
            ])
        
        # 级别分布
        lines.extend([
            colorize("📊 日志级别分布", 'BOLD'),
            "-" * 40,
        ])
        level_colors = {
            'DEBUG': 'WHITE', 'INFO': 'GREEN', 'WARNING': 'YELLOW',
            'ERROR': 'RED', 'CRITICAL': 'MAGENTA'
        }
        for level, count in sorted(self.stats.level_counts.items()):
            pct = count / self.stats.total_lines * 100
            bar = '█' * int(pct / 2)
            lines.append(
                f"  {colorize(level, level_colors.get(level, 'WHITE')):10} "
                f"{bar:25} {count:6} ({pct:5.1f}%)"
            )
        lines.append("")
        
        # 来源统计
        if len(self.stats.source_counts) > 1:
            lines.extend([
                colorize("🌐 Top来源", 'BOLD'),
                "-" * 40,
            ])
            for source, count in list(self.stats.source_counts.items())[:5]:
                lines.append(f"  {source}: {count}")
            lines.append("")
        
        # 错误模式
        if self.stats.error_patterns:
            lines.extend([
                colorize("⚠️ 检测到的错误模式", 'BOLD'),
                "-" * 40,
            ])
            for pattern in self.stats.error_patterns:
                lines.append(f"  • {colorize(pattern, 'RED')}")
            lines.append("")
        
        # 热门消息
        if self.stats.top_messages:
            lines.extend([
                colorize("💬 热门消息Top 5", 'BOLD'),
                "-" * 40,
            ])
            for i, (msg, count) in enumerate(self.stats.top_messages[:5], 1):
                msg_display = msg[:50] + "..." if len(msg) > 50 else msg
                lines.append(f"  {i}. [{count}x] {msg_display}")
        
        lines.append("")
        lines.append(colorize("=" * 60, 'CYAN'))
        
        return '\n'.join(lines)
    
    def _generate_json_report(self) -> str:
        """生成JSON格式报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_lines': self.stats.total_lines,
            'error_count': len(self.stats.error_patterns),
            'level_distribution': self.stats.level_counts,
            'source_distribution': dict(self.stats.source_counts),
            'hourly_distribution': dict(self.stats.hourly_distribution),
            'time_range': {
                'start': self.stats.time_range[0].isoformat() if self.stats.time_range else None,
                'end': self.stats.time_range[1].isoformat() if self.stats.time_range else None
            },
            'top_messages': self.stats.top_messages,
            'detected_patterns': self.stats.error_patterns
        }
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def print_summary(self):
        """打印摘要信息"""
        print(self.generate_report())

class InteractiveMode:
    """交互式模式"""
    
    def __init__(self):
        self.analyzer = SmartLogAnalyzer()
    
    def run(self):
        """运行交互式分析"""
        print(colorize("\n🔍 智能日志分析器 - 交互模式", 'BOLD'))
        print(colorize("输入日志文件路径进行分析 (输入 'q' 退出):\n", 'CYAN'))
        
        while True:
            filepath = input(colorize("📁 文件路径: ", 'GREEN')).strip()
            
            if filepath.lower() == 'q':
                print(colorize("\n👋 再见!", 'CYAN'))
                break
            
            if not Path(filepath).exists():
                print(colorize(f"❌ 文件不存在: {filepath}", 'RED'))
                continue
            
            print(colorize(f"\n⏳ 正在分析: {filepath}...", 'YELLOW'))
            
            try:
                count = self.analyzer.load_file(filepath)
                print(colorize(f"✅ 分析完成! 共 {count} 条日志记录\n", 'GREEN'))
                self.analyzer.print_summary()
                print()
            except Exception as e:
                print(colorize(f"❌ 分析失败: {e}", 'RED'))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能日志分析器 - Smart Log Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s access.log              # 分析日志文件
  %(prog)s access.log --json       # JSON格式输出
  %(prog)s access.log -i           # 交互模式
  %(prog)s --interactive           # 启动交互模式
        """
    )
    
    parser.add_argument('filepath', nargs='?', help='日志文件路径')
    parser.add_argument('-f', '--format', default='auto',
                       choices=['auto', 'apache', 'nginx', 'syslog', 'json'],
                       help='日志格式')
    parser.add_argument('-o', '--output', default='text',
                       choices=['text', 'json'],
                       help='输出格式')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='交互模式')
    parser.add_argument('--stats', action='store_true',
                       help='仅显示统计摘要')
    
    args = parser.parse_args()
    
    if args.interactive:
        InteractiveMode().run()
        return
    
    if not args.filepath:
        parser.print_help()
        return
    
    if not Path(args.filepath).exists():
        print(colorize(f"❌ 文件不存在: {args.filepath}", 'RED'))
        sys.exit(1)
    
    analyzer = SmartLogAnalyzer()
    print(colorize(f"\n⏳ 正在加载: {args.filepath}...", 'YELLOW'))
    
    count = analyzer.load_file(args.filepath, args.format)
    print(colorize(f"✅ 已加载 {count} 条日志记录\n", 'GREEN'))
    
    if args.stats:
        print(f"📊 总行数: {analyzer.stats.total_lines}")
        print(f"⚠️ 错误数: {len(analyzer.errors)}")
        print(f"📈 级别分布: {analyzer.stats.level_counts}")
    else:
        print(analyzer.generate_report(args.output))

if __name__ == '__main__':
    main()
