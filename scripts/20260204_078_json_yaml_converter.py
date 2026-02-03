#!/usr/bin/env python3
"""
JSON/YAML Converter - 智能JSON与YAML格式互转工具
支持命令行交互和API调用两种模式
"""

import json
import yaml
import sys
import base64
import argparse
from pathlib import Path
from typing import Any, Dict, Optional, Union


class JSONYAMLConverter:
    """JSON与YAML格式互转工具类"""
    
    SUPPORTED_FORMATS = ['json', 'yaml', 'yml']
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def detect_format(self, content: str) -> str:
        """自动检测输入格式"""
        content = content.strip()
        if content.startswith('{') or content.startswith('['):
            return 'json'
        elif content.startswith('---') or content.startswith('- ') or ':' in content.split('\n')[0]:
            return 'yaml'
        else:
            return 'json'
    
    def json_to_yaml(self, json_data: Union[str, Dict, Any]) -> str:
        """JSON转换为YAML"""
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        
        return yaml.dump(
            json_data, 
            indent=self.indent, 
            ensure_ascii=False,
            default_flow_style=False
        )
    
    def yaml_to_json(self, yaml_data: Union[str, Dict]) -> str:
        """YAML转换为JSON"""
        if isinstance(yaml_data, dict):
            return json.dumps(yaml_data, indent=self.indent, ensure_ascii=False)
        
        try:
            data = yaml.safe_load(yaml_data)
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
    
    def convert(self, content: str, target_format: str = 'yaml') -> str:
        """通用转换接口"""
        source_format = self.detect_format(content)
        
        if source_format == target_format:
            return content
        
        if target_format == 'yaml':
            return self.json_to_yaml(content)
        elif target_format == 'json':
            return self.yaml_to_json(content)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
    
    def convert_file(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        target_format: str = 'yaml'
    ) -> str:
        """转换文件"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        content = input_path.read_text(encoding='utf-8')
        result = self.convert(content, target_format)
        
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(result, encoding='utf-8')
            return str(output_path)
        
        suffix = '.yaml' if target_format == 'yaml' else '.json'
        output_path = input_path.with_suffix(suffix)
        output_path.write_text(result, encoding='utf-8')
        return str(output_path)


class InteractiveMode:
    """交互模式处理器"""
    
    def __init__(self):
        self.converter = JSONYAMLConverter()
    
    def run(self):
        """运行交互模式"""
        print("=== JSON/YAML Converter ===")
        print("Commands: 'quit' to exit, 'swap' to swap format")
        print()
        
        source_format = 'json'
        target_format = 'yaml'
        content = ""
        
        while True:
            print(f"[{source_format.upper()} -> {target_format.upper()}]")
            print("Enter your content (end with empty line, or 'quit' to exit):")
            
            lines = []
            while True:
                line = input()
                if line.lower() == 'quit':
                    print("Goodbye!")
                    return
                if line.lower() == 'swap':
                    source_format, target_format = target_format, source_format
                    print(f"Swapped! Now: {source_format} -> {target_format}")
                    break
                if line == '' and lines:
                    break
                lines.append(line)
            
            if not lines:
                continue
            
            content = '\n'.join(lines)
            
            try:
                result = self.converter.convert(content, target_format)
                print(f"\n=== {target_format.upper()} Result ===")
                print(result)
                print("=" * 30 + "\n")
            except Exception as e:
                print(f"Error: {e}\n")


def api_handler(data: Dict) -> Dict:
    """API处理器 - 兼容FastAPI/Flask"""
    converter = JSONYAMLConverter(indent=data.get('indent', 2))
    
    if 'content' not in data:
        return {'error': 'Missing "content" field'}
    
    content = data['content']
    target_format = data.get('target_format', 'yaml')
    
    if target_format not in JSONYAMLConverter.SUPPORTED_FORMATS:
        return {'error': f'Unsupported format: {target_format}'}
    
    try:
        result = converter.convert(content, target_format)
        return {
            'success': True,
            'source_format': converter.detect_format(content),
            'target_format': target_format,
            'result': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description='JSON/YAML Converter - 智能格式互转工具'
    )
    parser.add_argument(
        'input', 
        nargs='?', 
        help='Input file path'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'yaml', 'yml'],
        default='yaml',
        help='Target format (default: yaml)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    parser.add_argument(
        '-i', '--indent',
        type=int,
        default=2,
        help='Indentation spaces (default: 2)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='API mode (read JSON from stdin)'
    )
    
    args = parser.parse_args()
    
    if args.api:
        import sys
        data = json.load(sys.stdin)
        result = api_handler(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    if args.interactive or not args.input:
        InteractiveMode().run()
        return
    
    converter = JSONYAMLConverter(indent=args.indent)
    
    try:
        output_path = converter.convert_file(
            args.input,
            args.output,
            args.format
        )
        print(f"Converted: {args.input} -> {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
