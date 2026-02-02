#!/usr/bin/env python3
"""
命令行参数解析器 - Command Line Argument Parser
=================================================

一个功能强大且用户友好的命令行参数解析工具，
支持位置参数、可选参数、子命令、参数验证等功能。

GitHub: https://github.com/my1162709474/MarsAssistant-Code-Journey
"""

import argparse
import shlex
import sys
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class ArgType(Enum):
    """参数类型枚举"""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    CHOICE = "choice"
    PATH = "path"
    EMAIL = "email"
    URL = "url"


class ParameterStyle(Enum):
    """参数风格枚举"""
    UNIX = "unix"          # -o --option
    DOS = "dos"            # /option
    GNU = "gnu"            # --long-option
    SHORT = "short"        # -o


@dataclass
class ChoiceConstraint:
    """选择约束"""
    choices: List[Any]
    case_sensitive: bool = True
    
    def validate(self, value: Any) -> bool:
        if not self.case_sensitive and isinstance(value, str):
            return value.lower() in [c.lower() for c in self.choices]
        return value in self.choices


@dataclass 
class RangeConstraint:
    """范围约束（用于数值类型）"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    exclusive: bool = False


@dataclass
class Argument:
    """参数定义"""
    name: str
    arg_type: ArgType = ArgType.STRING
    required: bool = False
    help: str = ""
    default: Any = None
    choices: Optional[List[Any]] = None
    range_constraint: Optional[RangeConstraint] = None
    validators: List[Callable] = field(default_factory=list)
    positional: bool = False
    short_name: Optional[str] = None
    action: str = "store"  # store, store_true, store_false, append, count
    nargs: Optional[Union[int, str]] = None
    metavar: Optional[str] = None
    dest: Optional[str] = None
    
    def __post_init__(self):
        if self.choices:
            self.validators.append(self._validate_choices)
        if self.range_constraint:
            self.validators.append(self._validate_range)
    
    def _validate_choices(self, value: Any) -> Tuple[bool, str]:
        if self.choices:
            if not self.choices:
                return True, ""
            if self.choices and value not in self.choices:
                choices_str = ", ".join(map(str, self.choices))
                return False, f"'{value}' 不是有效的选项，有效选项为: {choices_str}"
        return True, ""
    
    def _validate_range(self, value: Any) -> Tuple[bool, str]:
        if self.range_constraint and isinstance(value, (int, float)):
            rc = self.range_constraint
            if rc.min_value is not None:
                if rc.exclusive:
                    if value <= rc.min_value:
                        return False, f"值必须大于 {rc.min_value}"
                else:
                    if value < rc.min_value:
                        return False, f"值必须大于等于 {rc.min_value}"
            if rc.max_value is not None:
                if rc.exclusive:
                    if value >= rc.max_value:
                        return False, f"值必须小于 {rc.max_value}"
                else:
                    if value > rc.max_value:
                        return False, f"值必须小于等于 {rc.max_value}"
        return True, ""


class ArgumentParser:
    """
    功能强大的命令行参数解析器
    
    特性:
    - 支持多种参数风格 (UNIX, DOS, GNU, SHORT)
    - 自动类型转换
    - 参数验证和约束
    - 子命令支持
    - 交互式帮助
    - 参数默认值处理
    - 必需参数检查
    """
    
    def __init__(
        self,
        prog: str = None,
        description: str = "",
        epilog: str = "",
        parameter_style: ParameterStyle = ParameterStyle.UNIX,
        allow_abbrev: bool = True,
        add_help: bool = True
    ):
        self.prog = prog or sys.argv[0]
        self.description = description
        self.epilog = epilog
        self.parameter_style = parameter_style
        self.allow_abbrev = allow_abbrev
        self.add_help = add_help
        
        self.arguments: Dict[str, Argument] = {}
        self.positional_args: List[Argument] = []
        self.optional_args: List[Argument] = []
        self.subcommands: Dict[str, 'SubCommand'] = {}
        self.groups: Dict[str, argparse._ArgumentGroup] = {}
        self._defaults: Dict[str, Any] = {}
        self._parsed: Dict[str, Any] = {}
        
    def add_argument(
        self,
        *names,
        arg_type: Union[ArgType, type] = ArgType.STRING,
        required: bool = False,
        help: str = "",
        default: Any = None,
        choices: List[Any] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        validator: Callable[[Any], Tuple[bool, str]] = None,
        positional: bool = False,
        short_name: str = None,
        action: str = "store",
        nargs: Optional[Union[int, str]] = None,
        metavar: str = None,
        dest: str = None,
        group: str = None
    ) -> Argument:
        """添加一个参数"""
        # 转换类型
        if isinstance(arg_type, type):
            type_map = {
                str: ArgType.STRING,
                int: ArgType.INT,
                float: ArgType.FLOAT,
                bool: ArgType.BOOL
            }
            arg_type = type_map.get(arg_type, ArgType.STRING)
        
        # 处理范围约束
        range_constraint = None
        if min_value is not None or max_value is not None:
            range_constraint = RangeConstraint(min_value, max_value)
        
        # 创建约束
        choice_constraint = None
        if choices:
            choice_constraint = ChoiceConstraint(choices)
        
        # 处理名称
        if positional:
            name = names[0] if names else f"arg_{len(self.positional_args)}"
            arg = Argument(
                name=name,
                arg_type=arg_type,
                required=required,
                help=help,
                default=default,
                choices=choices,
                range_constraint=range_constraint,
                validators=[],
                positional=True,
                short_name=short_name,
                action=action,
                nargs=nargs,
                metavar=metavar,
                dest=dest
            )
            self.positional_args.append(arg)
        else:
            name = names[0] if names else None
            arg = Argument(
                name=name,
                arg_type=arg_type,
                required=required,
                help=help,
                default=default,
                choices=choices,
                range_constraint=range_constraint,
                validators=[validator] if validator else [],
                positional=False,
                short_name=short_name,
                action=action,
                nargs=nargs,
                metavar=metavar,
                dest=dest
            )
            self.optional_args.append(arg)
            
        # 存储参数
        key = dest or name or f"arg_{len(self.arguments)}"
        self.arguments[key] = arg
        if default is not None:
            self._defaults[key] = default
            
        return arg
    
    def add_subcommand(self, name: str, parser: 'ArgumentParser', help: str = "") -> 'SubCommand':
        """添加子命令"""
        subcmd = SubCommand(name, parser, help)
        self.subcommands[name] = subcmd
        return subcmd
    
    def add_argument_group(self, title: str, description: str = "") -> argparse._ArgumentGroup:
        """添加参数组"""
        group = argparse._ArgumentGroup(self, title=title, description=description)
        self.groups[title] = group
        return group
    
    def set_defaults(self, **kwargs):
        """设置默认值"""
        self._defaults.update(kwargs)
    
    def get_defaults(self) -> Dict[str, Any]:
        """获取所有默认值"""
        defaults = self._defaults.copy()
        for arg in self.positional_args:
            if arg.default is not None:
                defaults[arg.dest or arg.name] = arg.default
        return defaults
    
    def parse_args(
        self, 
        args: List[str] = None,
        namespace: Any = None
    ) -> Dict[str, Any]:
        """解析参数"""
        args = args or sys.argv[1:]
        
        result = self.get_defaults().copy()
        result.update(self._parsed)
        
        i = 0
        while i < len(args):
            arg_str = args[i]
            
            # 处理子命令
            if arg_str in self.subcommands:
                subcmd = self.subcommands[arg_str]
                sub_result = subcmd.parser.parse_args(args[i+1:])
                result[arg_str] = sub_result
                break
            
            # 处理帮助参数
            if arg_str in ('-h', '--help') and self.add_help:
                self.print_help()
                sys.exit(0)
            
            # 匹配参数
            matched = False
            for arg in self.optional_args:
                # 检查长选项
                prefixes = self._get_prefixes()
                for prefix in prefixes:
                    long_name = f"{prefix}{arg.name}"
                    short_name = f"{prefix}{arg.short_name}" if arg.short_name else None
                    
                    if arg_str == long_name or (short_name and arg_str == short_name):
                        value = self._get_value(args, i, arg)
                        i += 1 + (1 if i + 1 < len(args) and not arg_str.startswith("--") and not arg_str.startswith("-") else 0)
                        if value is not None:
                            result[arg.dest or arg.name] = value
                        matched = True
                        break
                
                if matched:
                    break
            
            if not matched:
                # 尝试作为位置参数
                if i < len(args):
                    for arg in self.positional_args:
                        if arg.name not in result or arg.action in ('append', 'count'):
                            value = self._convert_value(args[i], arg)
                            result[arg.dest or arg.name] = value
                            break
                    i += 1
        
        self._parsed = result
        return result
    
    def _get_prefixes(self) -> List[str]:
        """获取参数前缀"""
        if self.parameter_style == ParameterStyle.UNIX:
            return ['-', '--']
        elif self.parameter_style == ParameterStyle.DOS:
            return ['/']
        elif self.parameter_style == ParameterStyle.GNU:
            return ['--']
        elif self.parameter_style == ParameterStyle.SHORT:
            return ['-']
        return ['-', '--']
    
    def _get_value(self, args: List[str], i: int, arg: Argument) -> Any:
        """获取参数值"""
        if arg.action in ('store_true', 'store_false'):
            return arg.action == 'store_true'
        
        if i + 1 < len(args):
            next_arg = args[i + 1]
            prefixes = self._get_prefixes()
            if not any(next_arg.startswith(p) for p in prefixes):
                return self._convert_value(next_arg, arg)
        
        if arg.default is not None:
            return arg.default
        return None
    
    def _convert_value(self, value: str, arg: Argument) -> Any:
        """转换值类型"""
        if arg.arg_type == ArgType.INT:
            return int(value)
        elif arg.arg_type == ArgType.FLOAT:
            return float(value)
        elif arg.arg_type == ArgType.BOOL:
            return value.lower() in ('true', '1', 'yes', 'y')
        elif arg.arg_type == ArgType.CHOICE:
            return value
        return value
    
    def _validate_args(self, parsed: Dict[str, Any]) -> List[str]:
        """验证参数"""
        errors = []
        for key, value in parsed.items():
            if key in self.arguments:
                arg = self.arguments[key]
                for validator in arg.validators:
                    valid, msg = validator(value)
                    if not valid:
                        errors.append(f"参数 '{key}': {msg}")
        return errors
    
    def format_help(self) -> str:
        """格式化帮助信息"""
        lines = []
        
        # 程序信息
        if self.description:
            lines.append(f"{self.prog}: {self.description}")
        else:
            lines.append(self.prog)
        
        lines.append("")
        lines.append("用法:")
        
        # 用法行
        usage_parts = [self.prog]
        for arg in self.positional_args:
            if arg.required:
                usage_parts.append(f"<{arg.name}>")
            else:
                usage_parts.append(f"[<{arg.name}>]")
        for arg in self.optional_args:
            prefix = self._get_prefixes()[0]
            if arg.required:
                usage_parts.append(f"{prefix}{arg.name} <值>")
            else:
                usage_parts.append(f"[{prefix}{arg.name} <值>]")
        if self.subcommands:
            usage_parts.append("<子命令>")
        lines.append(" ".join(usage_parts))
        lines.append("")
        
        # 子命令
        if self.subcommands:
            lines.append("子命令:")
            for name, subcmd in self.subcommands.items():
                lines.append(f"  {name:<15} {subcmd.help}")
            lines.append("")
        
        # 参数
        lines.append("参数:")
        for arg in self.optional_args:
            prefix = self._get_prefixes()[0]
            short = f"{prefix}{arg.short_name}, " if arg.short_name else ""
            long = f"{prefix}{arg.name}"
            lines.append(f"  {short}{long:<20} {arg.help}")
        for arg in self.positional_args:
            lines.append(f"  <{arg.name:<18}> {arg.help}")
        lines.append("")
        
        # 示例
        if self.epilog:
            lines.append("示例:")
            lines.append(self.epilog)
        
        return "\n".join(lines)
    
    def print_help(self):
        """打印帮助信息"""
        print(self.format_help())
    
    def print_usage(self):
        """打印用法信息"""
        print(f"用法: {self.prog} [选项]")
    
    def error(self, message: str):
        """打印错误信息并退出"""
        print(f"错误: {message}", file=sys.stderr)
        self.print_usage()
        sys.exit(2)


class SubCommand:
    """子命令定义"""
    
    def __init__(self, name: str, parser: ArgumentParser, help: str = ""):
        self.name = name
        self.parser = parser
        self.help = help


# ==================== 便捷函数 ====================

def create_parser(
    prog: str = None,
    description: str = "",
    style: ParameterStyle = ParameterStyle.UNIX
) -> ArgumentParser:
    """创建参数解析器的便捷函数"""
    return ArgumentParser(prog=prog, description=description, parameter_style=style)


def parse_integer(value: str, min_val: int = None, max_val: int = None) -> int:
    """安全解析整数"""
    try:
        result = int(value)
        if min_val is not None and result < min_val:
            raise ValueError(f"值必须大于等于 {min_val}")
        if max_val is not None and result > max_val:
            raise ValueError(f"值必须小于等于 {max_val}")
        return result
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def parse_float(value: str, min_val: float = None, max_val: float = None) -> float:
    """安全解析浮点数"""
    try:
        result = float(value)
        if min_val is not None and result < min_val:
            raise ValueError(f"值必须大于等于 {min_val}")
        if max_val is not None and result > max_val:
            raise ValueError(f"值必须小于等于 {max_val}")
        return result
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def parse_path(value: str, must_exist: bool = False, must_be_file: bool = False) -> str:
    """安全解析路径"""
    import os
    if must_exist and not os.path.exists(value):
        raise argparse.ArgumentTypeError(f"路径不存在: {value}")
    if must_be_file and os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"必须是文件: {value}")
    return value


def parse_email(value: str) -> str:
    """验证并解析邮箱"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(f"无效的邮箱格式: {value}")
    return value


def parse_url(value: str, schemes: List[str] = None) -> str:
    """验证并解析URL"""
    schemes = schemes or ['http', 'https']
    pattern = r'^(' + '|'.join(schemes) + r')://[^\s]+$'
    if not re.match(pattern, value, re.IGNORECASE):
        raise argparse.ArgumentTypeError(f"无效的URL格式，支持协议: {', '.join(schemes)}")
    return value


# ==================== 示例和测试 ====================

def demo_basic_usage():
    """基础用法演示"""
    print("=" * 60)
    print("1. 基础用法演示")
    print("=" * 60)
    
    parser = ArgumentParser(
        prog="demo",
        description="演示参数解析器的基本用法"
    )
    
    parser.add_argument("-n", "--name", required=True, help="你的名字")
    parser.add_argument("-a", "--age", arg_type=ArgType.INT, help="你的年龄")
    parser.add_argument("--city", default="北京", help="所在城市")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    
    try:
        # 测试参数
        args = parser.parse_args(["--name", "张三", "--age", "25", "--verbose"])
        print(f"姓名: {args.get('name')}")
        print(f"年龄: {args.get('age')}")
        print(f"城市: {args.get('city')}")
        print(f"详细模式: {args.get('verbose')}")
    except SystemExit:
        pass


def demo_with_validation():
    """带验证的用法演示"""
    print("\n" + "=" * 60)
    print("2. 参数验证演示")
    print("=" * 60)
    
    parser = ArgumentParser(
        prog="validate_demo",
        description="演示参数验证功能"
    )
    
    parser.add_argument("-e", "--email", required=True, help="邮箱地址", 
                       validator=parse_email)
    parser.add_argument("-p", "--port", arg_type=ArgType.INT, required=True,
                       help="端口号", min_value=1, max_value=65535)
    parser.add_argument("-s", "--score", arg_type=ArgType.FLOAT, default=0.0,
                       help="分数", min_value=0.0, max_value=100.0)
    parser.add_argument("--output", choices=["json", "yaml", "xml"], 
                       help="输出格式")
    
    try:
        args = parser.parse_args([
            "--email", "user@example.com",
            "--port", "8080",
            "--score", "95.5",
            "--output", "json"
        ])
        print(f"邮箱: {args.get('email')}")
        print(f"端口: {args.get('port')}")
        print(f"分数: {args.get('score')}")
        print(f"输出格式: {args.get('output')}")
    except SystemExit:
        pass


def demo_subcommands():
    """子命令演示"""
    print("\n" + "=" * 60)
    print("3. 子命令演示")
    print("=" * 60)
    
    # 主解析器
    main_parser = ArgumentParser(
        prog="git",
        description="版本控制工具示例"
    )
    
    # 子命令解析器
    commit_parser = ArgumentParser(prog="commit", description="提交更改")
    commit_parser.add_argument("-m", "--message", required=True, help="提交信息")
    commit_parser.add_argument("--amend", action="store_true", help="修改上次提交")
    
    push_parser = ArgumentParser(prog="push", description="推送更改")
    push_parser.add_argument("-u", "--upstream", help="上游分支")
    push_parser.add_argument("--force", action="store_true", help="强制推送")
    
    # 添加子命令
    main_parser.add_subcommand("commit", commit_parser, "提交更改到仓库")
    main_parser.add_subcommand("push", push_parser, "推送更改到远程仓库")
    main_parser.add_subcommand("pull", ArgumentParser(prog="pull", description="拉取更改"), "拉取远程更改")
    
    # 解析参数
    try:
        args = main_parser.parse_args(["commit", "-m", "初始提交", "--amend"])
        print(f"执行子命令: commit")
        print(f"提交信息: {args.get('commit', {}).get('message')}")
        print(f"修改提交: {args.get('commit', {}).get('amend')}")
    except SystemExit:
        pass


def demo_dos_style():
    """DOS风格参数演示"""
    print("\n" + "=" * 60)
    print("4. DOS风格参数演示")
    print("=" * 60)
    
    parser = ArgumentParser(
        prog="winapp",
        description="Windows应用示例",
        parameter_style=ParameterStyle.DOS
    )
    
    parser.add_argument("/input", required=True, help="输入文件")
    parser.add_argument("/output", help="输出文件")
    parser.add_argument("/verbose", action="store_true", help="详细输出")
    
    try:
        args = parser.parse_args(["/input", "data.txt", "/output", "result.txt", "/verbose"])
        print(f"输入文件: {args.get('input')}")
        print(f"输出文件: {args.get('output')}")
        print(f"详细模式: {args.get('verbose')}")
    except SystemExit:
        pass


def demo_positional_args():
    """位置参数演示"""
    print("\n" + "=" * 60)
    print("5. 位置参数演示")
    print("=" * 60)
    
    parser = ArgumentParser(
        prog="cp",
        description="复制文件示例"
    )
    
    parser.add_argument("source", positional=True, help="源文件")
    parser.add_argument("destination", positional=True, help="目标文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    
    try:
        args = parser.parse_args(["file1.txt", "file2.txt", "--verbose"])
        print(f"源文件: {args.get('source')}")
        print(f"目标文件: {args.get('destination')}")
        print(f"详细模式: {args.get('verbose')}")
    except SystemExit:
        pass


def run_interactive_demo():
    """运行交互式演示"""
    print("\n" + "=" * 60)
    print("交互式参数解析器演示")
    print("=" * 60)
    print("\n此演示将引导你创建自己的参数解析器...")
    
    parser = create_parser(
        prog="mytool",
        description="我的自定义工具"
    )
    
    # 添加参数
    parser.add_argument("-n", "--name", required=True, help="你的名字")
    parser.add_argument("-a", "--age", arg_type=ArgType.INT, 
                       help="你的年龄", min_value=0, max_value=150)
    parser.add_argument("-e", "--email", help="你的邮箱",
                       validator=parse_email)
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="详细输出模式")
    
    # 打印帮助
    print("\n生成的参数解析器帮助:")
    print("-" * 40)
    print(parser.format_help())
    
    # 提示用户尝试
    print("\n尝试运行:")
    print('  python argparse_demo.py --name "你的名字" --age 25 --email "you@example.com" -v')


if __name__ == "__main__":
    import sys
    
    # 如果有命令行参数，解析并执行
    if len(sys.argv) > 1:
        parser = create_parser(prog="argparse_demo", description="命令行参数解析器演示")
        
        parser.add_argument("--name", help="你的名字")
        parser.add_argument("--age", arg_type=ArgType.INT, help="年龄")
        parser.add_argument("--email", validator=parse_email, help="邮箱")
        parser.add_argument("--demo", choices=["basic", "validation", "subcommand", "dos", "positional", "help"],
                          default="help", help="运行特定演示")
        
        args = parser.parse_args()
        
        if args.get("demo") == "help" or len(sys.argv) == 1:
            demo_basic_usage()
            demo_with_validation()
            demo_subcommands()
            demo_dos_style()
            demo_positional_args()
            run_interactive_demo()
        elif args.get("demo") == "basic":
            demo_basic_usage()
        elif args.get("demo") == "validation":
            demo_with_validation()
        elif args.get("demo") == "subcommand":
            demo_subcommands()
        elif args.get("demo") == "dos":
            demo_dos_style()
        elif args.get("demo") == "positional":
            demo_positional_args()
    else:
        # 默认运行所有演示
        print("命令行参数解析器 - Command Line Argument Parser")
        print("=" * 60)
        
        demo_basic_usage()
        demo_with_validation()
        demo_subcommands()
        demo_dos_style()
        demo_positional_args()
        
        print("\n" + "=" * 60)
        print("快速使用指南")
        print("=" * 60)
        print("""
# 创建解析器
from argparse_demo import ArgumentParser, ArgType

parser = ArgumentParser(prog="myapp", description="我的应用")

# 添加参数
parser.add_argument("-n", "--name", required=True, help="姓名")
parser.add_argument("-a", "--age", arg_type=ArgType.INT, help="年龄")
parser.add_argument("-v", "--verbose", action="store_true", help="详细模式")

# 解析参数
args = parser.parse_args()
print(f"姓名: {args['name']}")
""")
