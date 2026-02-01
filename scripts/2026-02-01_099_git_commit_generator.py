#!/usr/bin/env python3
"""
🎯 Git智能提交消息生成器
AI辅助生成规范化的Git提交信息

功能：
- 分析变更类型（feat, fix, docs, style, refactor, test, chore）
- 智能生成符合Conventional Commits规范的提交消息
- 支持多文件变更分析
- 生成Emoji前缀
"""

import os
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class GitCommitMessageGenerator:
    """Git提交消息智能生成器"""
    
    # 变更类型定义
    CHANGE_TYPES = {
        'feat': {
            'patterns': [r'新增', r'添加', r'新功能', r'implement', r'add\s+'],
            'emoji': '✨',
            'description': '新功能',
            'conventional': 'feat'
        },
        'fix': {
            'patterns': [r'修复', r'修复', r'解决', r'fix', r'bug', r'解决'],
            'emoji': '🐛',
            'description': 'Bug修复',
            'conventional': 'fix'
        },
        'docs': {
            'patterns': [r'文档', r'readme', r'doc', r'注释', r'注释'],
            'emoji': '📚',
            'description': '文档更新',
            'conventional': 'docs'
        },
        'style': {
            'patterns': [r'格式', r'样式', r'风格', r'style', r'format', r'lint'],
            'emoji': '💎',
            'description': '代码格式',
            'conventional': 'style'
        },
        'refactor': {
            'patterns': [r'重构', r'重写', r'refactor', r'优化', r'improve'],
            'emoji': '♻️',
            'description': '代码重构',
            'conventional': 'refactor'
        },
        'test': {
            'patterns': [r'测试', r'test', r'单元测试', r'测试用例'],
            'emoji': '🧪',
            'description': '测试相关',
            'conventional': 'test'
        },
        'chore': {
            'patterns': [r'构建', r'依赖', r'配置', r'chore', r'update', r'升级'],
            'emoji': '🔧',
            'description': '构建/工具',
            'conventional': 'chore'
        },
        'perf': {
            'patterns': [r'性能', r'优化', r'perf', r'optimize', r'speed'],
            'emoji': '⚡',
            'description': '性能优化',
            'conventional': 'perf'
        }
    }
    
    def __init__(self):
        self.change_log = []
        
    def get_staged_files(self) -> List[str]:
        """获取暂存的文件列表"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return self.get_modified_files()
    
    def get_modified_files(self) -> List[str]:
        """获取修改的文件列表"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        status = parts[0]
                        filename = ' '.join(parts[1:])
                        files.append((status, filename))
            return files
        except subprocess.CalledProcessError:
            return []
    
    def get_diff_summary(self, filepath: str) -> Dict:
        """获取文件变更摘要"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--stat', filepath],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                'filepath': filepath,
                'stats': result.stdout.strip()
            }
        except subprocess.CalledProcessError:
            return {'filepath': filepath, 'stats': 'Unknown'}
    
    def detect_change_type(self, filepath: str, diff_content: str = '') -> Tuple[str, str]:
        """检测变更类型"""
        filepath_lower = filepath.lower()
        diff_lower = diff_content.lower()
        
        best_match = ('chore', '🔧')  # 默认类型
        max_score = 0
        
        for change_type, config in self.CHANGE_TYPES.items():
            score = 0
            
            # 检查文件路径
            for pattern in config['patterns']:
                if re.search(pattern, filepath_lower, re.IGNORECASE):
                    score += 2
            
            # 检查diff内容
            for pattern in config['patterns']:
                if re.search(pattern, diff_lower, re.IGNORECASE):
                    score += 1
            
            # 特殊文件类型匹配
            if filepath_lower.endswith('.py') and change_type in ['feat', 'fix', 'refactor']:
                score += 1
            if filepath_lower.endswith(('.md', '.txt', '.rst')) and change_type == 'docs':
                score += 1
            if filepath_lower.endswith(('.json', '.yaml', '.yml', '.toml')) and change_type == 'chore':
                score += 1
                
            if score > max_score:
                max_score = score
                best_match = (config['conventional'], config['emoji'])
        
        return best_match
    
    def extract_scope(self, filepath: str) -> Optional[str]:
        """提取影响范围（模块名）"""
        parts = filepath.replace('\\', '/').split('/')
        if len(parts) > 1:
            # 取目录名作为scope
            scope = parts[0] if parts[0] not in ['.', 'src', 'lib', 'scripts'] else parts[-2] if len(parts) > 2 else None
            return scope
        return None
    
    def generate_commit_message(self, files: List[str]) -> str:
        """生成提交消息"""
        if not files:
            return "未检测到变更"
        
        if len(files) == 1:
            filepath = files[0]
            change_type, emoji = self.detect_change_type(filepath)
            scope = self.extract_scope(filepath)
            
            filename = os.path.basename(filepath)
            description = self.generate_description(filename, change_type)
            
            if scope:
                message = f"{emoji} {change_type}({scope}): {description}"
            else:
                message = f"{emoji} {change_type}: {description}"
        else:
            # 多文件变更
            types_count = {}
            for filepath in files:
                change_type, _ = self.detect_change_type(filepath)
                types_count[change_type] = types_count.get(change_type, 0) + 1
            
            # 找出主要变更类型
            primary_type = max(types_count, key=types_count.get)
            emoji = self.CHANGE_TYPES.get(primary_type, self.CHANGE_TYPES['chore'])['emoji']
            
            count = len(files)
            message = f"{emoji} {primary_type}: 更新 {count} 个文件"
            
            if len(types_count) > 1:
                type_names = ', '.join(types_count.keys())
                message = f"{emoji} {primary_type}: 多类型变更 ({type_names})"
        
        return message
    
    def generate_description(self, filename: str, change_type: str) -> str:
        """生成描述"""
        name_without_ext = os.path.splitext(filename)[0]
        
        # 尝试从文件名提取意图
        if change_type == 'feat':
            return f"添加{name_without_ext.replace('_', ' ')}功能"
        elif change_type == 'fix':
            return f"修复{name_without_ext.replace('_', ' ')}相关问题"
        elif change_type == 'docs':
            return f"更新{name_without_ext.replace('_', ' ')}文档"
        elif change_type == 'refactor':
            return f"重构{name_without_ext.replace('_', ' ')}"
        elif change_type == 'test':
            return f"添加{name_without_ext.replace('_', ' ')}测试"
        elif change_type == 'style':
            return f"优化{name_without_ext.replace('_', ' ')}代码格式"
        else:
            return f"更新{name_without_ext.replace('_', ' ')}"
    
    def generate_conventional_message(self, files: List[str], body: str = '', footer: str = '') -> str:
        """生成完整Conventional Commits格式消息"""
        main_message = self.generate_commit_message(files)
        
        # 添加详细描述
        message = f"{main_message}\n\n"
        
        if body:
            message += f"{body}\n\n"
        
        # 添加文件列表
        if len(files) > 1:
            file_list = '\n'.join([f"- {f}" for f in files[:10]])
            if len(files) > 10:
                file_list += f"\n- ... 还有 {len(files) - 10} 个文件"
            message += f"变更文件:\n{file_list}\n"
        
        if footer:
            message += footer
        
        return message
    
    def interactive_generate(self):
        """交互式生成提交消息"""
        print("🎯 Git智能提交消息生成器\n")
        print("=" * 50)
        
        # 获取变更文件
        files = self.get_staged_files()
        if not files:
            print("📭 暂无暂存的变更")
            files = [f for _, f in self.get_modified_files()]
        
        if not files:
            print("📭 未检测到任何变更")
            return None
        
        print(f"📝 检测到 {len(files)} 个变更文件:\n")
        for f in files[:5]:
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  - ... 还有 {len(files) - 5} 个")
        print()
        
        # 生成提交消息
        commit_msg = self.generate_commit_message(files)
        print(f"💡 推荐的提交消息:\n")
        print(f"  {commit_msg}\n")
        
        # 生成详细版本
        detailed = self.generate_conventional_message(files)
        print(f"📄 详细格式:\n")
        print(f"{detailed}\n")
        
        return commit_msg
    
    def auto_commit(self, message: str = None):
        """自动提交"""
        files = self.get_staged_files()
        
        if not files:
            print("📭 暂存区为空，请先添加文件: git add <files>")
            return False
        
        if not message:
            message = self.generate_commit_message(files)
        
        try:
            # 配置提交信息
            subprocess.run(['git', 'config', 'user.email', 'assistant@mars.ai'], check=True)
            subprocess.run(['git', 'config', 'user.name', 'MarsAssistant'], check=True)
            
            # 提交
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ 提交成功: {message}")
                return True
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 错误: {e}")
            return False


def main():
    """主函数"""
    generator = GitCommitMessageGenerator()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--auto':
            # 自动提交模式
            generator.auto_commit()
        elif command == '--generate':
            # 仅生成消息
            files = generator.get_staged_files()
            if not files:
                files = [f for _, f in generator.get_modified_files()]
            msg = generator.generate_commit_message(files)
            print(msg)
        elif command == '--help':
            print("""
🎯 Git智能提交消息生成器

用法:
  python git_commit_generator.py           # 交互式生成
  python git_commit_generator.py --generate  # 生成消息
  python git_commit_generator.py --auto   # 自动提交
  python git_commit_generator.py --help   # 显示帮助
            """)
        else:
            print("未知参数，使用 --help 查看帮助")
    else:
        # 交互模式
        generator.interactive_generate()


if __name__ == "__main__":
    main()
