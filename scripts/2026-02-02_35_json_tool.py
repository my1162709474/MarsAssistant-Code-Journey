#!/usr/bin/env python3
"""
JSON工具箱 - JSON解析、验证、格式化与转换工具
支持JSON语法验证、格式化压缩、字段提取、JSON<->CSV转换
"""

import json
import csv
import base64
import re
import sys
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
from dataclasses import dataclass
from enum import Enum


class OutputFormat(Enum):
    """输出格式枚举"""
    PRETTY = "pretty"      # 格式化缩进
    COMPACT = "compact"    # 紧凑无空格
    MINIFIED = "minified"  # 单行最小化


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_message: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None


class JSONToolkit:
    """JSON工具箱主类"""
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def validate(self, json_str: str) -> ValidationResult:
        """
        验证JSON语法
        
        Args:
            json_str: JSON字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        try:
            json.loads(json_str)
            return ValidationResult(is_valid=True)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=str(e),
                error_line=e.lineno,
                error_column=e.colno
            )
    
    def format(self, json_str: str, format_type: OutputFormat = OutputFormat.PRETTY) -> str:
        """
        格式化JSON
        
        Args:
            json_str: JSON字符串
            format_type: 输出格式
            
        Returns:
            str: 格式化后的JSON字符串
        """
        data = json.loads(json_str)
        
        if format_type == OutputFormat.PRETTY:
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        elif format_type == OutputFormat.COMPACT:
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        else:  # MINIFIED
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    def minify(self, json_str: str) -> str:
        """压缩JSON为最小形式"""
        return self.format(json_str, OutputFormat.MINIFIED)
    
    def extract_fields(self, json_str: str, fields: List[str]) -> Dict[str, Any]:
        """
        提取指定字段
        
        Args:
            json_str: JSON字符串
            fields: 要提取的字段列表
            
        Returns:
            Dict[str, Any]: 提取的字段字典
        """
        data = json.loads(json_str)
        result = {}
        
        for field in fields:
            keys = field.split('.')
            value = data
            
            try:
                for key in keys:
                    if isinstance(value, list):
                        key = int(key)
                    value = value[key]
                result[field] = value
            except (KeyError, IndexError, TypeError, ValueError):
                result[field] = None
        
        return result
    
    def flatten(self, json_str: str, prefix: str = '', separator: str = '_') -> Dict[str, Any]:
        """
        扁平化嵌套JSON
        
        Args:
            json_str: JSON字符串
            prefix: 前缀
            separator: 分隔符
            
        Returns:
            Dict[str, Any]: 扁平化后的字典
        """
        data = json.loads(json_str)
        result = {}
        
        def _flatten(obj: Any, current_key: str):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{current_key}{separator}{k}" if current_key else k
                    _flatten(v, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{current_key}[{i}]"
                    _flatten(item, new_key)
            else:
                result[current_key] = obj
        
        _flatten(data, prefix)
        return result
    
    def unflatten(self, flat_dict: Dict[str, Any], separator: str = '_') -> Dict[str, Any]:
        """
        反扁平化字典
        
        Args:
            flat_dict: 扁平化字典
            separator: 分隔符
            
        Returns:
            Dict[str, Any]: 嵌套字典
        """
        result = {}
        
        for key, value in flat_dict.items():
            keys = re.split(r'[\.\[\]]+', key)
            keys = [k for k in keys if k]  # 移除空字符串
            
            current = result
            for k in keys[:-1]:
                if k not in current:
                    # 尝试判断下一个键的类型
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
        
        return result
    
    def json_to_csv(self, json_str: str, csv_path: str, 
                    flatten: bool = True, encoding: str = 'utf-8-sig') -> int:
        """
        JSON转CSV
        
        Args:
            json_str: JSON字符串
            csv_path: CSV文件路径
            flatten: 是否先扁平化
            encoding: 文件编码
            
        Returns:
            int: 写入的行数
        """
        data = json.loads(json_str)
        
        if not isinstance(data, list):
            data = [data]
        
        if flatten:
            flat_data = [self.flatten(json.dumps(item)) for item in data]
        else:
            flat_data = data
        
        if not flat_data:
            return 0
        
        # 获取所有可能的字段
        all_fields = set()
        for item in flat_data:
            all_fields.update(item.keys())
        fields = sorted(all_fields)
        
        with open(csv_path, 'w', newline='', encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(flat_data)
        
        return len(flat_data)
    
    def csv_to_json(self, csv_path: str, output_format: OutputFormat = OutputFormat.PRETTY,
                    encoding: str = 'utf-8-sig') -> str:
        """
        CSV转JSON
        
        Args:
            csv_path: CSV文件路径
            output_format: 输出格式
            encoding: 文件编码
            
        Returns:
            str: JSON字符串
        """
        data = []
        
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 转换类型
                processed_row = {}
                for k, v in row.items():
                    if v == '':
                        continue
                    # 尝试数值转换
                    if v.lower() == 'true':
                        processed_row[k] = True
                    elif v.lower() == 'false':
                        processed_row[k] = False
                    elif v.lower() == 'null':
                        processed_row[k] = None
                    else:
                        try:
                            if '.' in v:
                                processed_row[k] = float(v)
                            else:
                                processed_row[k] = int(v)
                        except ValueError:
                            processed_row[k] = v
                
                data.append(processed_row)
        
        return self.format(json.dumps(data), output_format)
    
    def compare(self, json_str1: str, json_str2: str) -> Dict[str, Any]:
        """
        比较两个JSON对象的差异
        
        Args:
            json_str1: 第一个JSON字符串
            json_str2: 第二个JSON字符串
            
        Returns:
            Dict[str, Any]: 差异报告
        """
        data1 = json.loads(json_str1)
        data2 = json.loads(json_str2)
        
        flat1 = self.flatten(json.dumps(data1))
        flat2 = self.flatten(json.dumps(data2))
        
        all_keys = set(flat1.keys()) | set(flat2.keys())
        
        added = []
        removed = []
        changed = []
        
        for key in all_keys:
            if key not in flat1:
                added.append(key)
            elif key not in flat2:
                removed.append(key)
            elif flat1[key] != flat2[key]:
                changed.append({
                    'key': key,
                    'old': flat1[key],
                    'new': flat2[key]
                })
        
        return {
            'added': added,
            'removed': removed,
            'changed': changed,
            'total_changes': len(added) + len(removed) + len(changed)
        }
    
    def template(self, template_str: str, **kwargs) -> str:
        """
        使用JSON模板（支持占位符替换）
        
        Args:
            template_str: 包含{{placeholder}}的模板字符串
            **kwargs: 替换变量
            
        Returns:
            str: 渲染后的JSON字符串
        """
        result = template_str
        for key, value in kwargs.items():
            result = result.replace(f'{{{{{key}}}}}', str(value))
        
        # 验证结果
        self.validate(result)
        return result


def demo():
    """演示JSON工具箱的功能"""
    toolkit = JSONToolkit(indent=2)
    
    # 1. 验证JSON
    print("=" * 50)
    print("1. JSON验证示例")
    print("=" * 50)
    
    valid_json = '{"name": "Alice", "age": 25, "city": "Beijing"}'
    invalid_json = '{"name": "Alice", "age": 25,}'  # 末尾逗号
    
    result = toolkit.validate(valid_json)
    print(f"Valid JSON: {result.is_valid}")
    
    result = toolkit.validate(invalid_json)
    print(f"Invalid JSON: {result.is_valid}")
    if not result.is_valid:
        print(f"  Error: {result.error_message}")
    
    # 2. 格式化与压缩
    print("\n" + "=" * 50)
    print("2. 格式化与压缩示例")
    print("=" * 50)
    
    compact = '{"name":"Alice","age":25}'
    pretty = toolkit.format(compact, OutputFormat.PRETTY)
    print("Pretty format:")
    print(pretty)
    
    minified = toolkit.minify(compact)
    print(f"\nMinified: {minified}")
    
    # 3. 字段提取
    print("\n" + "=" * 50)
    print("3. 字段提取示例")
    print("=" * 50)
    
    complex_json = json.dumps({
        "user": {
            "profile": {
                "name": "Bob",
                "email": "bob@example.com"
            },
            "settings": {
                "theme": "dark",
                "language": "zh-CN"
            }
        },
        "posts": [
            {"title": "Hello", "views": 100},
            {"title": "World", "views": 200}
        ]
    })
    
    extracted = toolkit.extract_fields(complex_json, 
        ["user.profile.name", "user.profile.email", "posts[0].views"])
    print(f"Extracted fields: {json.dumps(extracted, indent=2, ensure_ascii=False)}")
    
    # 4. 扁平化
    print("\n" + "=" * 50)
    print("4. 扁平化示例")
    print("=" * 50)
    
    nested = json.dumps({"user": {"name": "Charlie", "addr": {"city": "Shanghai"}}})
    flat = toolkit.flatten(nested)
    print(f"Flattened: {json.dumps(flat, indent=2, ensure_ascii=False)}")
    
    # 5. JSON与CSV转换
    print("\n" + "=" * 50)
    print("5. JSON<->CSV转换示例")
    print("=" * 50)
    
    json_data = json.dumps([
        {"name": "Alice", "age": 25, "city": "Beijing"},
        {"name": "Bob", "age": 30, "city": "Shanghai"}
    ])
    
    # 写入CSV
    csv_path = "/tmp/demo.csv"
    rows = toolkit.json_to_csv(json_data, csv_path)
    print(f"CSV written: {rows} rows -> {csv_path}")
    
    # 读回JSON
    back_to_json = toolkit.csv_to_json(csv_path)
    print(f"Back to JSON:\n{back_to_json}")
    
    # 6. 比较差异
    print("\n" + "=" * 50)
    print("6. JSON比较示例")
    print("=" * 50)
    
    json1 = json.dumps({"a": 1, "b": 2, "c": 3})
    json2 = json.dumps({"a": 1, "b": 5, "d": 4})
    
    diff = toolkit.compare(json1, json2)
    print(f"Comparison result:")
    print(f"  Added: {diff['added']}")
    print(f"  Removed: {diff['removed']}")
    print(f"  Changed: {diff['changed']}")
    
    # 7. 模板渲染
    print("\n" + "=" * 50)
    print("7. 模板渲染示例")
    print("=" * 50)
    
    template = '{"name": "{{name}}", "age": {{age}}, "city": "{{city}}"}'
    rendered = toolkit.template(template, name="Diana", age=28, city="Guangzhou")
    print(f"Template: {template}")
    print(f"Rendered: {rendered}")


def main():
    """命令行入口"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'demo':
            demo()
        elif command == 'validate':
            content = sys.stdin.read()
            result = JSONToolkit().validate(content)
            print("Valid" if result.is_valid else f"Invalid: {result.error_message}")
        elif command == 'format':
            content = sys.stdin.read()
            fmt = sys.argv[2] if len(sys.argv) > 2 else 'pretty'
            format_type = OutputFormat.PRETTY if fmt == 'pretty' else OutputFormat.COMPACT
            print(JSONToolkit().format(content, format_type))
        elif command == 'minify':
            content = sys.stdin.read()
            print(JSONToolkit().minify(content))
        else:
            print(f"Unknown command: {command}")
            print("Usage: json_tool.py [demo|validate|format|minify]")
    else:
        demo()


if __name__ == "__main__":
    main()
