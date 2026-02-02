#!/usr/bin/env python3
"""
URL编码/解码工具
URL Encoder & Decoder Tool
=======================================
支持：
- URL编码（特殊字符转%XX格式）
- URL解码（%XX格式转原始字符）
- Query参数解析
- 自动检测并处理编码/解码
- 批量处理文本文件

Author: AI Assistant
Date: 2026-02-02
"""

import urllib.parse
import argparse
import sys
import base64
from pathlib import Path


def encode_url(text: str, safe: str = '/') -> str:
    """URL编码"""
    return urllib.parse.quote(text, safe=safe)


def decode_url(text: str) -> str:
    """URL解码"""
    try:
        return urllib.parse.unquote(text)
    except Exception as e:
        return f"解码错误: {e}"


def parse_query_string(query: str) -> dict:
    """解析URL查询字符串"""
    params = {}
    pairs = query.split('&') if '&' in query else query.split(';')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[urllib.parse.unquote(key)] = urllib.parse.unquote(value)
    return params


def build_query_string(params: dict, encode: bool = True) -> str:
    """构建URL查询字符串"""
    parts = []
    for key, value in params.items():
        if encode:
            key = urllib.parse.quote(key)
            value = urllib.parse.quote(str(value))
        parts.append(f"{key}={value}")
    return '&'.join(parts)


def is_encoded(text: str) -> bool:
    """检测文本是否已被URL编码"""
    return '%' in text and any(c.isupper() or c.isdigit() for c in text)


def process_file(input_path: str, output_path: str = None, mode: str = 'auto'):
    """批量处理文件"""
    path = Path(input_path)
    if not path.exists():
        print(f"错误: 文件不存在 - {input_path}")
        return False
    
    content = path.read_text(encoding='utf-8')
    
    if mode == 'auto':
        mode = 'decode' if is_encoded(content) else 'encode'
    
    if mode == 'encode':
        result = encode_url(content)
    else:
        result = decode_url(content)
    
    if output_path:
        Path(output_path).write_text(result, encoding='utf-8')
        print(f"已保存到: {output_path}")
    else:
        print(result)
    
    return True


def print_usage():
    """打印使用说明"""
    print("""
URL 编码/解码工具
==================

用法: python url_encoder_decoder.py [选项]

选项:
  -t, --text TEXT     要编码/解码的文本
  -e, --encode        强制编码模式
  -d, --decode        强制解码模式
  -q, --query "key1=val1&key2=val2"  解析查询字符串
  -f, --file FILE     处理文件（输入）
  -o, --output FILE   输出文件路径
  -s, --safe CHARS    编码时保留的字符（默认: /）
  -h, --help          显示此帮助信息

示例:
  python url_encoder_decoder.py -t "Hello World!"
  python url_encoder_decoder.py -d -t "Hello%20World%21"
  python url_encoder_decoder.py -q "name=张三&age=25"
  python url_encoder_decoder.py -f input.txt -o output.txt
""")


def main():
    parser = argparse.ArgumentParser(description='URL编码/解码工具', add_help=False)
    parser.add_argument('-t', '--text', type=str, help='要编码/解码的文本')
    parser.add_argument('-e', '--encode', action='store_true', help='强制编码模式')
    parser.add_argument('-d', '--decode', action='store_true', help='强制解码模式')
    parser.add_argument('-q', '--query', type=str, help='解析URL查询字符串')
    parser.add_argument('-f', '--file', type=str, help='输入文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出文件路径')
    parser.add_argument('-s', '--safe', type=str, default='/', help='编码时保留的字符')
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
    
    args = parser.parse_args()
    
    if args.help:
        print_usage()
        return
    
    # 处理文本
    if args.text:
        if args.encode:
            print(f"编码结果: {encode_url(args.text, args.safe)}")
        elif args.decode:
            print(f"解码结果: {decode_url(args.text)}")
        else:
            mode = 'decode' if is_encoded(args.text) else 'encode'
            if mode == 'encode':
                print(f"编码结果: {encode_url(args.text, args.safe)}")
            else:
                print(f"解码结果: {decode_url(args.text)}")
        return
    
    # 处理查询字符串
    if args.query:
        print("查询参数解析:")
        params = parse_query_string(args.query)
        for key, value in params.items():
            print(f"  {key}: {value}")
        return
    
    # 处理文件
    if args.file:
        mode = 'encode' if args.encode else ('decode' if args.decode else 'auto')
        process_file(args.file, args.output, mode)
        return
    
    # 无参数时显示使用说明
    print_usage()


if __name__ == '__main__':
    main()
