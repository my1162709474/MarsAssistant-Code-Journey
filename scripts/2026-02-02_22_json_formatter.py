#!/usr/bin/env python3
"""
JSON格式化工具 - JSON Formatter Tool
支持格式化、美化、压缩JSON，并可以检测JSON错误
"""

import json
import sys
import argparse
import os


def format_json(input_str: str, indent: int = 2, sort_keys: bool = False) -> str:
    """格式化JSON字符串"""
    try:
        data = json.loads(input_str)
        return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: {e}")


def minify_json(input_str: str) -> str:
    """压缩JSON字符串"""
    try:
        data = json.loads(input_str)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: {e}")


def validate_json(input_str: str) -> tuple[bool, str]:
    """验证JSON格式"""
    try:
        data = json.loads(input_str)
        return True, f"✓ JSON有效，包含 {len(data) if isinstance(data, (dict, list)) else 1} 个元素"
    except json.JSONDecodeError as e:
        return False, f"✗ JSON无效: {e}"


def convert_yaml_to_json(yaml_str: str) -> str:
    """简单的YAML转JSON（仅支持基本类型）"""
    import re
    result = {}
    lines = yaml_str.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value == '' or value is None:
                result[key] = {}
            elif value.startswith('[') and value.endswith(']'):
                result[key] = eval(value)  # 简单列表
            elif value.isdigit():
                result[key] = int(value)
            elif value.replace('.', '').isdigit():
                result[key] = float(value)
            elif value in ('true', 'True'):
                result[key] = True
            elif value in ('false', 'False'):
                result[key] = False
            elif value in ('null', 'None'):
                result[key] = None
            else:
                result[key] = value.strip('"\'')
    
    return json.dumps(result, indent=2, ensure_ascii=False)


def interactive_mode():
    """交互模式"""
    print("JSON工具 - 交互模式")
    print("输入JSON字符串进行操作，输入 :q 退出")
    print("命令: :format, :minify, :validate, :yaml")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input == ':q':
                print("再见！")
                break
            
            if not user_input:
                continue
            
            if user_input.startswith(':'):
                cmd = user_input[1:]
                data = []
                print("输入JSON内容（多行输入，空行结束）:")
                while True:
                    line = input()
                    if not line.strip():
                        break
                    data.append(line)
                json_input = '\n'.join(data)
                
                if cmd == 'format':
                    print(format_json(json_input))
                elif cmd == 'minify':
                    print(minify_json(json_input))
                elif cmd == 'validate':
                    valid, msg = validate_json(json_input)
                    print(msg)
                elif cmd == 'yaml':
                    print(convert_yaml_to_json(json_input))
                else:
                    print(f"未知命令: {cmd}")
            else:
                print("请以 : 开头输入命令")
                
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break


def main():
    parser = argparse.ArgumentParser(
        description='JSON格式化工具 - 格式化、美化、压缩JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s file.json                    # 格式化文件
  %(prog)s file.json -m                 # 压缩文件
  %(prog)s file.json --validate         # 验证JSON
  %(prog)s '{"a":1}' -i 4               # 自定义缩进
  %(prog)s -i                            # 交互模式
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入文件或JSON字符串')
    parser.add_argument('-m', '--minify', action='store_true', help='压缩JSON')
    parser.add_argument('-i', '--indent', type=int, default=2, help='缩进空格数 (默认: 2)')
    parser.add_argument('-s', '--sort', action='store_true', help='按键排序')
    parser.add_argument('--validate', action='store_true', help='仅验证JSON格式')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--yaml', action='store_true', help='YAML转JSON')
    
    args = parser.parse_args()
    
    if args.interactive or (not args.input and not args.validate):
        interactive_mode()
        return
    
    # 读取输入
    if args.input and os.path.exists(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.input:
        content = args.input
    else:
        # 从标准输入读取
        content = sys.stdin.read()
    
    if args.validate:
        valid, msg = validate_json(content)
        print(msg)
        sys.exit(0 if valid else 1)
    
    if args.yaml:
        try:
            result = convert_yaml_to_json(content)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.minify:
        try:
            result = minify_json(content)
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            result = format_json(content, args.indent, args.sort)
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"已保存到: {args.output}")
    else:
        print(result)


if __name__ == '__main__':
    main()
