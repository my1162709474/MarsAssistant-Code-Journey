#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能系统监控工具
================
一个功能强大的系统资源监控工具，支持实时监控CPU、内存、磁盘、网络、进程等。
支持多种输出格式（终端高亮、JSON、CSV）、告警阈值设置、历史数据记录。

功能特性:
- 实时监控CPU、内存、磁盘、网络使用率
- 进程监控（CPU/内存排序、资源占用分析）
- 网络连接监控（TCP/UDP统计、端口扫描）
- 历史数据记录（JSON格式）
- 自定义告警阈值
- 彩色终端输出
- 多格式导出（JSON、CSV）
- 支持连续监控模式

作者: AI Assistant
日期: 2026-02-02
"""

import os
import sys
import time
import json
import csv
import socket
import threading
from datetime import datetime
from collections import defaultdict
import platform

# 尝试导入可选依赖
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("建议安装 psutil: pip install psutil")
    print("使用基础监控模式")

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    print("建议安装 colorama: pip install colorama")

try:
    import GPUtil
    HAS_GPUUTIL = True
except ImportError:
    HAS_GPUUTIL = False

# 颜色定义
if HAS_COLORAMA:
    class Colors:
        HEADER = Fore.CYAN + Style.BRIGHT
        INFO = Fore.BLUE
        SUCCESS = Fore.GREEN
        WARNING = Fore.YELLOW
        ERROR = Fore.RED + Style.BRIGHT
        CPU = Fore.MAGENTA
        MEMORY = Fore.BLUE
        DISK = Fore.YELLOW
        NETWORK = Fore.GREEN
        PROCESS = Fore.CYAN
        RESET = Style.RESET_ALL
        DIM = Style.DIM
else:
    class Colors:
        HEADER = ''
        INFO = ''
        SUCCESS = ''
        WARNING = ''
        ERROR = ''
        CPU = ''
        MEMORY = ''
        DISK = ''
        NETWORK = ''
        PROCESS = ''
        RESET = ''
        DIM = ''


class SystemMonitor:
    """系统监控主类"""
    
    def __init__(self, history_file='monitor_history.json', alert_thresholds=None):
        self.history_file = history_file
        self.alert_thresholds = alert_thresholds or {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0,
            'network_upload': 10000000,
            'network_download': 10000000,
        }
        self.history_data = self._load_history()
        self.monitoring = False
        self.monitor_thread = None
        
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史数据失败: {e}")
                return {'metrics': []}
        return {'metrics': []}
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2)
        except Exception as e:
            print(f"保存历史数据失败: {e}")
    
    def get_system_info(self):
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
        }
        return info
    
    def get_cpu_info(self):
        info = {}
        if HAS_PSUTIL:
            info['usage_percent'] = psutil.cpu_percent(interval=1)
            info['count'] = psutil.cpu_count()
            info['frequency'] = psutil.cpu_freq().current if psutil.cpu_freq() else 0
            info['load_avg'] = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            times = psutil.cpu_times_percent(interval=1)
            info['times'] = {
                'user': times.user,
                'system': times.system,
                'idle': times.idle,
                'iowait': times.iowait if hasattr(times, 'iowait') else 0,
            }
        else:
            info['usage_percent'] = 0
            info['count'] = os.cpu_count() or 1
            info['frequency'] = 0
            info['load_avg'] = (0, 0, 0)
        return info
    
    def get_memory_info(self):
        info = {}
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            info['total'] = self._format_bytes(mem.total)
            info['available'] = self._format_bytes(mem.available)
            info['used'] = self._format_bytes(mem.used)
            info['usage_percent'] = mem.percent
            info['swap_total'] = self._format_bytes(psutil.swap_memory().total)
            info['swap_used'] = self._format_bytes(psutil.swap_memory().used)
            info['swap_percent'] = psutil.swap_memory().percent
        else:
            info['total'] = 'Unknown'
            info['available'] = 'Unknown'
            info['used'] = 'Unknown'
            info['usage_percent'] = 0
        return info
    
    def get_disk_info(self):
        info = {}
        if HAS_PSUTIL:
            disk_usage = psutil.disk_usage('/')
            info['total'] = self._format_bytes(disk_usage.total)
            info['used'] = self._format_bytes(disk_usage.used)
            info['free'] = self._format_bytes(disk_usage.free)
            info['usage_percent'] = disk_usage.percent
            disk_io = psutil.disk_io_counters()
            if disk_io:
                info['io_read'] = self._format_bytes(disk_io.read_bytes)
                info['io_write'] = self._format_bytes(disk_io.write_bytes)
                info['io_read_count'] = disk_io.read_count
                info['io_write_count'] = disk_io.write_count
        else:
            info['total'] = 'Unknown'
            info['used'] = 'Unknown'
            info['free'] = 'Unknown'
            info['usage_percent'] = 0
        return info
    
    def get_network_info(self):
        info = {}
        if HAS_PSUTIL:
            net_io = psutil.net_io_counters()
            info['bytes_sent'] = self._format_bytes(net_io.bytes_sent)
            info['bytes_recv'] = self._format_bytes(net_io.bytes_recv)
            info['packets_sent'] = net_io.packets_sent
            info['packets_recv'] = net_io.packets_recv
            info['errin'] = net_io.errin
            info['errout'] = net_io.errout
            info['dropin'] = net_io.dropin
            info['dropout'] = net_io.dropout
            connections = psutil.net_connections()
            info['connections_count'] = len(connections)
            info['connections_established'] = len([c for c in connections if c.status == 'ESTABLISHED'])
            info['connections_listening'] = len([c for c in connections if c.status == 'LISTEN'])
        else:
            info['bytes_sent'] = 'Unknown'
            info['bytes_recv'] = 'Unknown'
            info['packets_sent'] = 0
            info['packets_recv'] = 0
        return info
    
    def get_processes(self, sort_by='cpu', limit=10):
        processes = []
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'] or 'Unknown',
                        'cpu_percent': info['cpu_percent'] or 0,
                        'memory_percent': info['memory_percent'] or 0,
                        'status': info['status'] or 'Unknown',
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            sort_key = sort_by if sort_by in ['cpu_percent', 'memory_percent', 'pid'] else 'cpu_percent'
            processes.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
            processes = processes[:limit]
        return processes
    
    def get_gpu_info(self):
        info = {'available': False, 'gpus': []}
        if HAS_GPUUTIL:
            try:
                gpus = GPUtil.getGPUs()
                info['available'] = True
                for gpu in gpus:
                    info['gpus'].append({
                        'id': gpu.id,
                        'name': gpu.name,
                        'memory_total': f"{gpu.memoryTotal}MB",
                        'memory_used': f"{gpu.memoryUsed}MB",
                        'memory_free': f"{gpu.memoryFree}MB",
                        'usage_percent': gpu.load * 100,
                        'temperature': gpu.temperature,
                    })
            except Exception as e:
                info['error'] = str(e)
        return info
    
    def get_temperature_info(self):
        info = {'available': False, 'sensors': []}
        if HAS_PSUTIL:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    info['available'] = True
                    for name, entries in temps.items():
                        for entry in entries:
                            info['sensors'].append({
                                'name': name,
                                'label': entry.label,
                                'current': entry.current,
                                'high': entry.high,
                                'critical': entry.critical,
                            })
            except Exception as e:
                info['error'] = str(e)
        return info
    
    def get_battery_info(self):
        info = {'available': False}
        if HAS_PSUTIL:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    info['available'] = True
                    info['percent'] = battery.percent
                    info['power_plugged'] = battery.power_plugged
                    info['seconds_left'] = battery.secsleft
            except Exception as e:
                info['error'] = str(e)
        return info
    
    def get_all_metrics(self):
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'gpu': self.get_gpu_info(),
            'temperature': self.get_temperature_info(),
            'battery': self.get_battery_info(),
        }
        self.history_data['metrics'].append(metrics)
        if len(self.history_data['metrics']) > 1000:
            self.history_data['metrics'] = self.history_data['metrics'][-1000:]
        return metrics
    
    def check_alerts(self, metrics):
        alerts = []
        if metrics['cpu']['usage_percent'] > self.alert_thresholds.get('cpu', 80):
            alerts.append({
                'type': 'CPU',
                'level': 'WARNING' if metrics['cpu']['usage_percent'] < 95 else 'CRITICAL',
                'message': f"CPU使用率: {metrics['cpu']['usage_percent']:.1f}%",
            })
        if metrics['memory']['usage_percent'] > self.alert_thresholds.get('memory', 85):
            alerts.append({
                'type': 'MEMORY',
                'level': 'WARNING' if metrics['memory']['usage_percent'] < 95 else 'CRITICAL',
                'message': f"内存使用率: {metrics['memory']['usage_percent']:.1f}%",
            })
        if metrics['disk']['usage_percent'] > self.alert_thresholds.get('disk', 90):
            alerts.append({
                'type': 'DISK',
                'level': 'CRITICAL',
                'message': f"磁盘使用率: {metrics['disk']['usage_percent']:.1f}%",
            })
        return alerts
    
    def _format_bytes(self, bytes_num):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f}{unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f}PB"
    
    def print_report(self, metrics=None, verbose=False):
        if metrics is None:
            metrics = self.get_all_metrics()
        self._save_history()
        
        print()
        print(f"{Colors.HEADER}========================================{Colors.RESET}")
        print(f"{Colors.HEADER}  智能系统监控器 v1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.HEADER}========================================{Colors.RESET}")
        print()
        
        # 系统信息
        print(f"{Colors.INFO}系统信息:{Colors.RESET}")
        print(f"  主机名: {metrics['system']['hostname']}")
        print(f"  IP地址: {metrics['system']['ip_address']}")
        print(f"  平台: {metrics['system']['platform']} {metrics['system']['platform_version']}")
        print()
        
        # CPU
        print(f"{Colors.CPU}CPU 信息:{Colors.RESET}")
        print(f"  使用率: {self._get_usage_color(metrics['cpu']['usage_percent'])}{metrics['cpu']['usage_percent']:.1f}%{Colors.RESET}")
        if 'count' in metrics['cpu']:
            print(f"  核心数: {metrics['cpu']['count']}")
        if 'frequency' in metrics['cpu'] and metrics['cpu']['frequency']:
            print(f"  频率: {metrics['cpu']['frequency']:.0f} MHz")
        print()
        
        # 内存
        print(f"{Colors.MEMORY}内存信息:{Colors.RESET}")
        mem = metrics['memory']
        print(f"  使用率: {self._get_usage_color(mem['usage_percent'])}{mem['usage_percent']:.1f}%{Colors.RESET}")
        print(f"  已用/总计: {mem['used']} / {mem['total']}")
        print()
        
        # 磁盘
        print(f"{Colors.DISK}磁盘信息:{Colors.RESET}")
        disk = metrics['disk']
        print(f"  使用率: {self._get_usage_color(disk['usage_percent'])}{disk['usage_percent']:.1f}%{Colors.RESET}")
        print(f"  已用/空闲: {disk['used']} / {disk['free']}")
        if 'io_read' in disk:
            print(f"  IO读写: {disk['io_read']} / {disk['io_write']}")
        print()
        
        # 网络
        print(f"{Colors.NETWORK}网络信息:{Colors.RESET}")
        net = metrics['network']
        print(f"  发送/接收: {net['bytes_sent']} / {net['bytes_recv']}")
        if 'connections_count' in net:
            print(f"  连接数: {net['connections_established']} (已建立) / {net['connections_listening']} (监听)")
        print()
        
        # GPU
        if metrics['gpu']['available']:
            print(f"{Colors.INFO}GPU 信息:{Colors.RESET}")
            for gpu in metrics['gpu']['gpus']:
                print(f"  {gpu['name']}:")
                print(f"    使用率: {self._get_usage_color(gpu['usage_percent'])}{gpu['usage_percent']:.1f}%{Colors.RESET}")
                print(f"    显存: {gpu['memory_used']} / {gpu['memory_total']}")
                print(f"    温度: {gpu['temperature']}C")
            print()
        
        # 温度
        if metrics['temperature']['available']:
            print(f"{Colors.INFO}温度信息:{Colors.RESET}")
            for sensor in metrics['temperature']['sensors']:
                label = sensor['label'] or sensor['name']
                temp = sensor['current']
                temp_color = Colors.SUCCESS if temp < 50 else Colors.WARNING if temp < 70 else Colors.ERROR
                print(f"  {label}: {temp_color}{temp:.1f}C{Colors.RESET}")
            print()
        
        # 电池
        if metrics['battery']['available']:
            print(f"{Colors.INFO}电池信息:{Colors.RESET}")
            bat = metrics['battery']
            bat_color = Colors.SUCCESS if bat['percent'] > 50 else Colors.WARNING if bat['percent'] > 20 else Colors.ERROR
            print(f"  电量: {bat_color}{bat['percent']}%{Colors.RESET}")
            if bat['power_plugged']:
                print(f"  状态: 充电中")
            else:
                print(f"  状态: 使用电池")
            print()
        
        # 进程
        if verbose:
            print(f"{Colors.PROCESS}Top 10 进程 (CPU占用):{Colors.RESET}")
            processes = self.get_processes(sort_by='cpu_percent', limit=10)
            for i, proc in enumerate(processes, 1):
                print(f"  {i:2}. PID:{proc['pid']:6} {proc['name'][:20]:20} CPU:{proc['cpu_percent']:5.1f}% MEM:{proc['memory_percent']:5.1f}%")
            print()
        
        # 告警
        alerts = self.check_alerts(metrics)
        if alerts:
            print(f"{Colors.WARNING}告警:{Colors.RESET}")
            for alert in alerts:
                level_icon = "CRITICAL" if alert['level'] == 'CRITICAL' else "WARNING"
                print(f"  [{level_icon}] {alert['message']}")
            print()
    
    def _get_usage_color(self, percent):
        if percent < 50:
            return Colors.SUCCESS
        elif percent < 80:
            return Colors.WARNING
        else:
            return Colors.ERROR
    
    def export_data(self, metrics, format='json', filename=None):
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitor_export_{timestamp}.{format}"
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
        elif format == 'csv':
            flat_data = {
                'timestamp': metrics['timestamp'],
                'cpu_percent': metrics['cpu']['usage_percent'],
                'memory_percent': metrics['memory']['usage_percent'],
                'disk_percent': metrics['disk']['usage_percent'],
                'network_bytes_sent': metrics['network']['bytes_sent'],
                'network_bytes_recv': metrics['network']['bytes_recv'],
            }
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data.keys())
                writer.writeheader()
                writer.writerow(flat_data)
        else:
            print(f"不支持的格式: {format}")
            return False
        
        print(f"数据已导出到: {filename}")
        return True
    
    def start_continuous_monitor(self, interval=5):
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                metrics = self.get_all_metrics()
                self.print_report(metrics)
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()
        print(f"开始连续监控，间隔: {interval}秒")
        print("按 Ctrl+C 停止监控")
    
    def stop_continuous_monitor(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            print("监控已停止")
            self._save_history()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='智能系统监控工具')
    parser.add_argument('-i', '--interval', type=int, default=5, help='监控间隔(秒)')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细进程信息')
    parser.add_argument('-e', '--export', type=str, choices=['json', 'csv'], help='导出数据格式')
    parser.add_argument('-o', '--output', type=str, help='输出文件名')
    parser.add_argument('-t', '--thresholds', type=str, help='告警阈值配置文件(JSON格式)')
    parser.add_argument('--history', action='store_true', help='显示历史记录')
    args = parser.parse_args()
    
    alert_thresholds = None
    if args.thresholds:
        try:
            with open(args.thresholds, 'r') as f:
                alert_thresholds = json.load(f)
        except Exception as e:
            print(f"加载阈值配置失败: {e}")
            return
    
    monitor = SystemMonitor(alert_thresholds=alert_thresholds)
    
    if args.history:
        print("历史记录:")
        for metric in monitor.history_data['metrics'][-10:]:
            print(f"  {metric['timestamp']}")
            print(f"    CPU: {metric['cpu']['usage_percent']:.1f}%")
            print(f"    内存: {metric['memory']['usage_percent']:.1f}%")
            print(f"    磁盘: {metric['disk']['usage_percent']:.1f}%")
        return
    
    metrics = monitor.get_all_metrics()
    
    if args.export:
        monitor.export_data(metrics, format=args.export, filename=args.output)
    
    monitor.print_report(metrics, verbose=args.verbose)
    
    if not args.export:
        try:
            response = input("
是否继续监控? (y/n): ")
            if response.lower() == 'y':
                monitor.start_continuous_monitor(interval=args.interval)
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop_continuous_monitor()
        except KeyboardInterrupt:
            print()


if __name__ == '__main__':
    main()
