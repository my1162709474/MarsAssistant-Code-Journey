#!/usr/bin/env python3
"""
Git Sync Tracker - 自动同步并追踪 Git 仓库进度的工具
Day 5: 创建一个实用的 Git 仓库同步和进度追踪脚本
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Optional, Dict, List

class GitSyncTracker:
    """Git 仓库同步追踪器"""
    
    def __init__(self, repo_path: str = ".", config_file: str = "sync_config.json"):
        self.repo_path = repo_path
        self.config_file = config_file
        self.sync_history: List[Dict] = []
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.sync_history = data.get('history', [])
        else:
            self.sync_history = []
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump({
                'last_sync': datetime.now().isoformat(),
                'history': self.sync_history
            }, f, indent=2)
    
    def run_command(self, cmd: List[str]) -> tuple:
        """执行命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def get_repo_status(self) -> Dict:
        """获取仓库当前状态"""
        status = {}
        
        # 获取远程仓库信息
        code, stdout, _ = self.run_command(['git', 'remote', '-v'])
        if code == 0:
            status['remotes'] = stdout.strip()
        
        # 获取当前分支
        code, stdout, _ = self.run_command(['git', 'branch', '--show-current'])
        status['branch'] = stdout.strip() if code == 0 else 'unknown'
        
        # 获取最后提交
        code, stdout, _ = self.run_command(['git', 'log', '-1', '--oneline'])
        status['last_commit'] = stdout.strip() if code == 0 else 'unknown'
        
        # 获取未提交的更改
        code, stdout, _ = self.run_command(['git', 'status', '--short'])
        status['uncommitted'] = len(stdout.strip().split('\n')) if stdout.strip() else 0
        
        # 获取远程分支
        code, stdout, _ = self.run_command(['git', 'branch', '-r'])
        status['remote_branches'] = len(stdout.strip().split('\n')) if stdout.strip() else 0
        
        return status
    
    def sync_to_remote(self, remote: str = "origin", branch: str = "main") -> Dict:
        """同步到远程仓库"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'remote': remote,
            'branch': branch,
            'success': False,
            'details': {}
        }
        
        # 拉取最新代码
        code, stdout, stderr = self.run_command(['git', 'pull', remote, branch])
        result['details']['pull'] = {'code': code, 'output': stdout.strip()}
        
        if code == 0:
            # 推送到远程（如果有本地更改）
            code, stdout, stderr = self.run_command(['git', 'push', remote, branch])
            result['details']['push'] = {'code': code, 'output': stdout.strip()}
            result['success'] = code == 0
        
        self.sync_history.append(result)
        self.save_config()
        
        return result
    
    def get_sync_stats(self) -> Dict:
        """获取同步统计"""
        stats = {
            'total_syncs': len(self.sync_history),
            'successful_syncs': sum(1 for s in self.sync_history if s['success']),
            'failed_syncs': sum(1 for s in self.sync_history if not s['success']),
            'last_sync': None,
            'streak': 0
        }
        
        if self.sync_history:
            stats['last_sync'] = self.sync_history[-1]['timestamp']
            
            # 计算连续成功次数
            streak = 0
            for sync in reversed(self.sync_history):
                if sync['success']:
                    streak += 1
                else:
                    break
            stats['streak'] = streak
        
        return stats
    
    def display_status(self):
        """显示当前状态"""
        status = self.get_repo_status()
        stats = self.get_sync_stats()
        
        print("=" * 50)
        print("Git Sync Tracker - 状态报告")
        print("=" * 50)
        print(f"📦 当前分支: {status['branch']}")
        print(f"📝 最后提交: {status['last_commit']}")
        print(f"📊 未提交更改: {status['uncommitted']} 个文件")
        print(f"🔗 远程分支: {status['remote_branches']} 个")
        print("-" * 50)
        print(f"📈 总同步次数: {stats['total_syncs']}")
        print(f"✅ 成功同步: {stats['successful_syncs']}")
        print(f"❌ 失败同步: {stats['failed_syncs']}")
        print(f"🔥 连续成功: {stats['streak']} 次")
        print("=" * 50)


def main():
    """主函数"""
    tracker = GitSyncTracker()
    
    # 显示当前状态
    tracker.display_status()
    
    # 示例：执行一次同步
    print("\n🚀 执行同步测试...")
    result = tracker.sync_to_remote()
    
    if result['success']:
        print("✅ 同步成功!")
    else:
        print("❌ 同步失败")
        if result['details'].get('pull', {}).get('output'):
            print(f"错误信息: {result['details']['pull']['output']}")


if __name__ == "__main__":
    main()
