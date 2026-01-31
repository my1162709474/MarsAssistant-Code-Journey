"""
JSON处理工具集合 - Day 4
功能：JSON格式化、验证、转换、查询
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class JsonUtils:
    """JSON处理工具类"""
    
    @staticmethod
    def format_json(json_str: str, indent: int = 2) -> str:
        """格式化JSON字符串"""
        try:
            data = json.loads(json_str)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def minify_json(json_str: str) -> str:
        """压缩JSON字符串"""
        try:
            data = json.loads(json_str)
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def validate_json(json_str: str) -> tuple[bool, str]:
        """验证JSON是否有效"""
        try:
            json.loads(json_str)
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON at position {e.pos}: {e.msg}"
    
    @staticmethod
    def json_to_csv(json_data: Union[list, dict], 
                   csv_path: str,
                   flatten: bool = True) -> None:
        """JSON转CSV"""
        if isinstance(json_data, dict):
            json_data = [json_data]
        
        def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep).items())
                elif isinstance(v, list):
                    items.append((new_key, json.dumps(v)))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if flatten:
            flat_data = [flatten_dict(item) for item in json_data]
        else:
            flat_data = json_data
        
        if not flat_data:
            return
        
        columns = set()
        for item in flat_data:
            columns.update(item.keys())
        columns = sorted(columns)
        
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(flat_data)
    
    @staticmethod
    def csv_to_json(csv_path: str, 
                   output_path: Optional[str] = None,
                   list_columns: Optional[List[str]] = None) -> List[Dict]:
        """CSV转JSON"""
        import csv
        result = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if list_columns:
                    for col in list_columns:
                        if col in row and row[col]:
                            try:
                                row[col] = json.loads(row[col])
                            except json.JSONDecodeError:
                                pass
                result.append(row)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        return result
    
    @staticmethod
    def query_json(json_data: Any, 
                  query: str,
                  default: Any = None) -> Any:
        """JSON路径查询（简化版）"""
        try:
            if query.startswith('..'):
                return JsonUtils._recursive_find(json_data, query[2:])
            
            result = json_data
            parts = re.split(r'\[|\]|\.', query.replace(']', '').split('.'))
            parts = [p for p in parts if p]
            
            for part in parts:
                if part.startswith('?') and isinstance(result, list):
                    match = re.match(r'\?@\.(\w+)(==|!=|>|<)(.+)', part)
                    if match:
                        key, op, val = match.groups()
                        val = json.loads(val) if val in ('true', 'false', 'null') or val.isdigit() else val
                        result = [item for item in result if JsonUtils._compare(item.get(key), op, val)]
                elif result is None:
                    return default
                elif isinstance(result, list):
                    result = result[int(part)] if part.isdigit() else result
                elif isinstance(result, dict):
                    result = result.get(part, default)
                else:
                    return default
            return result
        except Exception:
            return default
    
    @staticmethod
    def _compare(val1: Any, op: str, val2: Any) -> bool:
        if op == '==':
            return val1 == val2
        elif op == '!=':
            return val1 != val2
        elif op == '>':
            return val1 > val2
        elif op == '<':
            return val1 < val2
        return False
    
    @staticmethod
    def _recursive_find(obj: Any, key: str) -> List[Any]:
        results = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    results.append(v)
                if isinstance(v, (dict, list)):
                    results.extend(JsonUtils._recursive_find(v, key))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(JsonUtils._recursive_find(item, key))
        return results
    
    @staticmethod
    def diff_json(json1: Union[str, dict], 
                  json2: Union[str, dict]) -> Dict[str, Any]:
        """比较两个JSON对象的差异"""
        if isinstance(json1, str):
            data1 = json.loads(json1)
        else:
            data1 = json1
        
        if isinstance(json2, str):
            data2 = json.loads(json2)
        else:
            data2 = json2
        
        return JsonUtils._diff_recursive(data1, data2)
    
    @staticmethod
    def _diff_recursive(obj1: Any, obj2: Any, path: str = '') -> Dict:
        result = {'added': {}, 'removed': {}, 'changed': {}}
        
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in all_keys:
                current_path = f"{path}.{key}" if path else key
                if key not in obj1:
                    result['added'][current_path] = obj2[key]
                elif key not in obj2:
                    result['removed'][current_path] = obj1[key]
                elif obj1[key] != obj2[key]:
                    if isinstance(obj1[key], (dict, list)) and isinstance(obj2[key], (dict, list)):
                        nested = JsonUtils._diff_recursive(obj1[key], obj2[key], current_path)
                        result['added'].update(nested['added'])
                        result['removed'].update(nested['removed'])
                        result['changed'].update(nested['changed'])
                    else:
                        result['changed'][current_path] = {'old': obj1[key], 'new': obj2[key]}
        
        return result


def demo():
    print("=" * 60)
    print("JSON处理工具 - Day 4")
    print("=" * 60)
    
    sample = '{"name": "test", "data": [1, 2, 3]}'
    print(f"原始JSON: {sample}")
    print(f"格式化: {JsonUtils.format_json(sample)}")
    print(f"验证: {JsonUtils.validate_json(sample)}")
    print("=" * 60)


if __name__ == "__main__":
    demo()
