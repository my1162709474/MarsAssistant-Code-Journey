#!/usr/bin/env python3
"""
Shell命令学习器 - Shell Command Learner v1.0
============================================
帮助用户学习常用Shell命令的交互式工具。

功能:
- 命令教程：系统化学习常用命令
- 交互练习：边学边练
- 知识测试：检验学习成果
- 进度追踪：记录学习进度

作者: MarsAssistant-Code-Journey
日期: 2026-02-02
"""

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Difficulty(Enum):
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


@dataclass
class Command:
    name: str
    description: str
    syntax: str
    examples: List[str]
    category: str
    difficulty: Difficulty
    tips: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)


@dataclass
class LearningProgress:
    command_name: str
    times_practiced: int = 0
    times_mastered: int = 0
    last_practiced: Optional[datetime] = None
    quiz_score: float = 0.0
    is_mastered: bool = False


# 命令数据库
COMMANDS = {
    "ls": Command(
        name="ls", description="列出目录内容",
        syntax="ls [选项] [目录]",
        examples=["ls", "ls -l", "ls -a", "ls -lh", "ls -la", "ls /path/to/dir"],
        category="文件操作", difficulty=Difficulty.BEGINNER,
        tips=["使用 -l 查看详细信息", "使用 -a 显示隐藏文件", "使用 -h 以易读格式显示大小"],
        related_commands=["ll", "dir", "tree"],
    ),
    "cd": Command(
        name="cd", description="切换当前工作目录",
        syntax="cd [目录路径]",
        examples=["cd /path/to/dir", "cd ..", "cd ~", "cd -", "cd ../.."],
        category="目录操作", difficulty=Difficulty.BEGINNER,
        tips=["cd .. 返回上级目录", "cd ~ 或 cd 直接回家目录", "cd - 返回上一次所在目录"],
        related_commands=["pwd", "pushd", "popd"],
    ),
    "pwd": Command(
        name="pwd", description="显示当前工作目录",
        syntax="pwd", examples=["pwd", "pwd -P"],
        category="目录操作", difficulty=Difficulty.BEGINNER,
        tips=["pwd = Print Working Directory", "常用于确认当前位置"],
        related_commands=["cd", "ls"],
    ),
    "mkdir": Command(
        name="mkdir", description="创建新目录",
        syntax="mkdir [选项] 目录名",
        examples=["mkdir new_folder", "mkdir -p a/b/c", "mkdir -m 755 folder", "mkdir folder1 folder2"],
        category="目录操作", difficulty=Difficulty.BEGINNER,
        tips=["使用 -p 选项可以创建嵌套目录", "默认权限受 umask 影响", "可以一次创建多个目录"],
        related_commands=["rmdir", "touch"],
    ),
    "rm": Command(
        name="rm", description="删除文件或目录",
        syntax="rm [选项] 文件或目录",
        examples=["rm file.txt", "rm -f file.txt", "rm -r dirname", "rm -rf dirname", "rm *.txt"],
        category="文件操作", difficulty=Difficulty.BEGINNER,
        tips=["rm -r 删除目录及其内容", "rm -f 强制删除，不提示", "rm -i 删除前询问确认"],
        related_commands=["rmdir", "unlink"],
    ),
    "cp": Command(
        name="cp", description="复制文件或目录",
        syntax="cp [选项] 源 目标",
        examples=["cp file1.txt file2.txt", "cp file.txt /path/to/dir/", "cp -r dir1 dir2", "cp -i file.txt file2.txt"],
        category="文件操作", difficulty=Difficulty.BEGINNER,
        tips=["使用 -r 复制目录", "使用 -i 复制前询问确认", "使用 -p 保留文件属性", "使用 -a 保持所有属性"],
        related_commands=["mv", "rsync"],
    ),
    "mv": Command(
        name="mv", description="移动或重命名文件/目录",
        syntax="mv [选项] 源 目标",
        examples=["mv old.txt new.txt", "mv file.txt /path/to/dir/", "mv dir1 dir2", "mv -i file.txt new.txt"],
        category="文件操作", difficulty=Difficulty.BEGINNER,
        tips=["可用于重命名文件或目录", "移动到同一目录就是重命名", "使用 -i 防止意外覆盖"],
        related_commands=["cp", "rename"],
    ),
    "cat": Command(
        name="cat", description="连接文件并打印到标准输出",
        syntax="cat [选项] [文件...]",
        examples=["cat file.txt", "cat file1.txt file2.txt", "cat -n file.txt", "cat > newfile.txt", "cat file.txt >> another.txt"],
        category="文件查看", difficulty=Difficulty.BEGINNER,
        tips=["使用 -n 显示行号", "使用 -s 压缩空行", "使用 > 重定向创建文件", "使用 >> 追加到文件末尾"],
        related_commands=["less", "more", "head", "tail"],
    ),
    "grep": Command(
        name="grep", description="文本搜索工具",
        syntax="grep [选项] 模式 [文件...]",
        examples=["grep \"pattern\" file.txt", "grep -r \"pattern\" .", "grep -i \"pattern\" file.txt", "grep -n \"pattern\" file.txt", "grep -v \"pattern\" file.txt"],
        category="文本处理", difficulty=Difficulty.INTERMEDIATE,
        tips=["使用 -i 忽略大小写", "使用 -r 递归搜索目录", "使用 -n 显示行号", "使用 -v 反向选择"],
        related_commands=["egrep", "fgrep", "ag", "rg"],
    ),
    "find": Command(
        name="find", description="在目录树中搜索文件",
        syntax="find [路径] [选项] [表达式]",
        examples=["find . -name \"*.txt\"", "find /path -type f", "find . -size +1M", "find . -mtime -7", "find . -type d"],
        category="文件搜索", difficulty=Difficulty.INTERMEDIATE,
        tips=["使用 -name 按名称搜索", "使用 -type 按类型搜索", "使用 -size 按大小搜索", "使用 -mtime 按修改时间搜索"],
        related_commands=["locate", "which", "whereis"],
    ),
    "chmod": Command(
        name="chmod", description="修改文件权限",
        syntax="chmod [选项] 模式 文件...",
        examples=["chmod 755 file.txt", "chmod +x script.sh", "chmod -R 644 dir/", "chmod u=rwx,g=rx,o=r file"],
        category="权限管理", difficulty=Difficulty.INTERMEDIATE,
        tips=["权限表示：r=4, w=2, x=1", "常见权限：755(rwxr-xr-x), 644(rw-r--r--)", "使用 -R 递归修改"],
        related_commands=["chown", "chgrp"],
    ),
    "tar": Command(
        name="tar", description="归档文件工具",
        syntax="tar [选项] [文件...]",
        examples=["tar -cvf archive.tar dir/", "tar -xvf archive.tar", "tar -czvf archive.tar.gz dir/", "tar -xzvf archive.tar.gz", "tar -tf archive.tar"],
        category="归档压缩", difficulty=Difficulty.INTERMEDIATE,
        tips=["c=创建, x=解压, t=列出", "v=显示详情, f=文件名", "z=gzip压缩(.gz)", "j=bzip2压缩(.bz2)"],
        related_commands=["zip", "unzip", "gzip", "gunzip"],
    ),
    "ssh": Command(
        name="ssh", description="安全远程登录",
        syntax="ssh [选项] 用户@主机 [命令]",
        examples=["ssh user@hostname", "ssh -p 2222 user@host", "ssh -i key.pem user@host", "ssh user@host \"command\""],
        category="网络工具", difficulty=Difficulty.INTERMEDIATE,
        tips=["默认端口22，可使用 -p 指定", "使用 -i 指定私钥文件", "使用 -v 显示调试信息"],
        related_commands=["scp", "sftp", "ssh-keygen"],
    ),
    "curl": Command(
        name="curl", description="数据传输工具",
        syntax="curl [选项] [URL...]",
        examples=["curl https://example.com", "curl -O https://example.com/file", "curl -d \"a=1\" URL", "curl -H \"Header: value\" URL"],
        category="网络工具", difficulty=Difficulty.INTERMEDIATE,
        tips=["使用 -O 保存文件", "使用 -o 指定保存文件名", "使用 -d 发送POST数据", "使用 -H 添加请求头"],
        related_commands=["wget", "httpie"],
    ),
    "ps": Command(
        name="ps", description="查看进程状态",
        syntax="ps [选项]",
        examples=["ps", "ps aux", "ps -ef", "ps -ef | grep python", "ps -u username"],
        category="系统监控", difficulty=Difficulty.BEGINNER,
        tips=["aux 显示所有进程", "-ef 显示完整格式", "使用管道和grep过滤", "PID是进程ID"],
        related_commands=["top", "htop", "kill", "pkill"],
    ),
    "top": Command(
        name="top", description="实时查看系统进程",
        syntax="top [选项]",
        examples=["top", "top -u username", "top -p 1234"],
        category="系统监控", difficulty=Difficulty.BEGINNER,
        tips=["按CPU排序：按P", "按内存排序：按M", "按 q 退出"],
        related_commands=["htop", "ps", "vmstat"],
    ),
    "kill": Command(
        name="kill", description="终止进程",
        syntax="kill [选项] PID",
        examples=["kill 1234", "kill -9 1234", "kill -l", "killall process_name", "pkill pattern"],
        category="系统监控", difficulty=Difficulty.BEGINNER,
        tips=["默认发送TERM信号（15）", "-9 发送KILL信号（强制终止）", "使用 -l 查看所有信号"],
        related_commands=["ps", "pkill", "killall"],
    ),
    "df": Command(
        name="df", description="查看磁盘空间使用情况",
        syntax="df [选项]",
        examples=["df", "df -h", "df -T", "df -i"],
        category="系统监控", difficulty=Difficulty.BEGINNER,
        tips=["使用 -h 以易读格式显示", "使用 -T 显示文件系统类型", "使用 -i 显示inode使用"],
        related_commands=["du", "lsblk"],
    ),
    "du": Command(
        name="du", description="查看目录或文件大小",
        syntax="du [选项] [文件或目录]",
        examples=["du", "du -h file.txt", "du -sh dir/", "du -h --max-depth=1"],
        category="系统监控", difficulty=Difficulty.BEGINNER,
        tips=["使用 -h 易读格式", "使用 -s 显示总计", "使用 --max-depth 控制深度"],
        related_commands=["df", "ncdu"],
    ),
    "man": Command(
        name="man", description="查看命令手册",
        syntax="man 命令名",
        examples=["man ls", "man -k keyword", "man -f command", "whatis command"],
        category="帮助文档", difficulty=Difficulty.BEGINNER,
        tips=["按 / 搜索，按 n 下一个", "按 q 退出", "使用 -k 搜索关键字", "使用 -f 获取简要说明"],
        related_commands=["help", "info", "whatis"],
    ),
    "alias": Command(
        name="alias", description="创建命令别名",
        syntax="alias [别名='命令']",
        examples=["alias ll='ls -lh'", "alias rm='rm -i'", "alias gs='git status'", "unalias ll", "alias"],
        category="系统配置", difficulty=Difficulty.BEGINNER,
        tips=["别名只在当前shell生效", "写入 ~/.bashrc 永久生效", "使用 \\command 跳过别名执行原命令"],
        related_commands=["unalias", "source"],
    ),
    "echo": Command(
        name="echo", description="输出文本",
        syntax="echo [选项] 字符串",
        examples=["echo \"Hello World\"", "echo -e \"a\\tb\"", "echo $VAR", "echo *", "echo {1..5}"],
        category="基础命令", difficulty=Difficulty.BEGINNER,
        tips=["使用 -e 解析转义字符", "变量前加 $", "支持通配符展开", "支持大括号展开"],
        related_commands=["printf"],
    ),
    "sed": Command(
        name="sed", description="流编辑器",
        syntax="sed [选项] '命令' [文件]",
        examples=["sed 's/old/new/' file.txt", "sed 's/old/new/g' file.txt", "sed -i 's/old/new/g' file.txt", "sed '2d' file.txt"],
        category="文本处理", difficulty=Difficulty.ADVANCED,
        tips=["s= substitution 替换", "g= global 全局", "使用 -i 直接修改文件", "使用 -n 只打印指定行"],
        related_commands=["awk", "tr", "cut"],
    ),
    "awk": Command(
        name="awk", description="模式扫描和处理语言",
        syntax="awk '模式{动作}' [文件]",
        examples=["awk '{print $1}' file.txt", "awk -F: '{print $1}' /etc/passwd", "awk 'NR==5' file.txt", "awk '$1 > 100' file.txt"],
        category="文本处理", difficulty=Difficulty.ADVANCED,
        tips=["$0 整行, $1 第一列, $NF 最后一列", "NR 行号, NF 列数", "使用 -F 指定分隔符"],
        related_commands=["sed", "cut", "sort"],
    ),
    "vim": Command(
        name="vim", description="高级文本编辑器",
        syntax="vim [文件]",
        examples=["vim file.txt", "vim +100 file.txt", "vim -O file1 file2"],
        category="文本编辑", difficulty=Difficulty.ADVANCED,
        tips=["模式：Normal, Insert, Visual, Command", "i 进入插入模式", ":w 保存, :q 退出"],
        related_commands=["vi", "nano", "emacs"],
    ),
}


class ShellLearner:
    """Shell命令学习器"""
    
    def __init__(self, progress_file: str = "learning_progress.json"):
        self.progress_file = progress_file
        self.progress: Dict[str, LearningProgress] = self.load_progress()
    
    def load_progress(self) -> Dict[str, LearningProgress]:
        """加载学习进度"""
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                return {
                    k: LearningProgress(**v) 
                    for k, v in data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_progress(self):
        """保存学习进度"""
        data = {
            k: {
                'command_name': v.command_name,
                'times_practiced': v.times_practiced,
                'times_mastered': v.times_mastered,
                'last_practiced': v.last_practiced.isoformat() if v.last_practiced else None,
                'quiz_score': v.quiz_score,
                'is_mastered': v.is_mastered,
            }
            for k, v in self.progress.items()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_command(self, name: str) -> Optional[Command]:
        """获取命令信息"""
        return COMMANDS.get(name.lower())
    
    def list_commands(self, category: str = None, 
                      difficulty: Difficulty = None) -> List[Command]:
        """列出命令"""
        result = list(COMMANDS.values())
        if category:
            result = [c for c in result if c.category == category]
        if difficulty:
            result = [c for c in result if c.difficulty == difficulty]
        return result
    
    def practice_command(self, name: str) -> bool:
        """练习命令"""
        cmd = self.get_command(name)
        if not cmd:
            return False
        
        if name not in self.progress:
            self.progress[name] = LearningProgress(command_name=name)
        
        self.progress[name].times_practiced += 1
        self.progress[name].last_practiced = datetime.now()
        self.save_progress()
        return True
    
    def get_progress_stats(self) -> Dict:
        """获取学习统计"""
        total = len(COMMANDS)
        practiced = len(self.progress)
        mastered = len([p for p in self.progress.values() if p.is_mastered])
        
        return {
            'total_commands': total,
            'practiced_commands': practiced,
            'mastered_commands': mastered,
            'mastery_rate': f"{mastered/total*100:.1f}%" if total > 0 else "0%",
        }
    
    def search_commands(self, keyword: str) -> List[Command]:
        """搜索命令"""
        keyword = keyword.lower()
        return [c for c in COMMANDS.values() 
                if keyword in c.name.lower() or keyword in c.description.lower()]


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      Shell命令学习器 v1.0                                 ║
║      Interactive Shell Command Learner                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def print_menu():
    print("""
┌─────────────────────────────────────────────────────────┐
│                       主菜单                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 📚 学习命令   - 浏览并学习所有命令                   │
│  2. 🎯 练习模式   - 边学边练                             │
│  3. 📊 进度统计   - 查看学习进度                         │
│  4. 🔍 命令搜索   - 快速查找命令                         │
│  5. 🎲 随机命令   - 随机学习一个命令                     │
│                                                         │
│  0. 🚪 退出                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
    """)


def main():
    """主函数"""
    learner = ShellLearner()
    print_banner()
    
    while True:
        print_menu()
        choice = input("请选择: ").strip()
        
        if choice == "0":
            print("👋 再见！继续学习更多Shell命令！")
            break
        
        elif choice == "1":
            print("\n📚 所有命令:")
            for i, cmd in enumerate(sorted(COMMANDS.values(), key=lambda x: x.name), 1):
                print(f"  {i:2}. {cmd.name:10} [{cmd.difficulty.value}] {cmd.description}")
        
        elif choice == "2":
            name = input("输入要练习的命令名称: ").strip()
            if learner.practice_command(name):
                print(f"✅ {name} 练习完成！")
            else:
                print(f"❌ 未找到命令: {name}")
        
        elif choice == "3":
            stats = learner.get_progress_stats()
            print(f"\n📊 学习进度统计:")
            print(f"  总命令数: {stats['total_commands']}")
            print(f"  已练习: {stats['practiced_commands']}")
            print(f"  已掌握: {stats['mastered_commands']}")
            print(f"  掌握率: {stats['mastery_rate']}")
        
        elif choice == "4":
            keyword = input("输入搜索关键词: ").strip()
            results = learner.search_commands(keyword)
            if results:
                print(f"\n🔍 搜索结果:")
                for cmd in results:
                    print(f"  • {cmd.name}: {cmd.description}")
            else:
                print("未找到匹配的命令")
        
        elif choice == "5":
            cmd = random.choice(list(COMMANDS.values()))
            print(f"\n🎲 随机命令: {cmd.name}")
            print(f"   {cmd.description}")
            print(f"   语法: {cmd.syntax}")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
