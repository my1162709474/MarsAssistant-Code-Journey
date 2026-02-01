#!/usr/bin/env python3
"""
Data Cleaner - 数据清洗工具
支持CSV/JSON格式，处理缺失值，数据格式转换，基础统计
"""

import csv
import json
import re
from typing import Any, Dict, List, Optional, Union
from statistics import mean, median


class DataCleaner:
    """数据清洗主类"""
    
    def __init__(self, data: Optional[Union[List[Dict], Dict]] = None):
        self.data = data or []
        self.stats = {}
    
    @classmethod
    def from_csv(cls, filepath: str, encoding: str = 'utf-8') -> 'DataCleaner':
        """从CSV文件加载数据"""
        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return cls(data)
    
    @classmethod
    def from_json(cls, filepath: str, encoding: str = 'utf-8') -> 'DataCleaner':
        """从JSON文件加载数据"""
        with open(filepath, 'r', encoding=encoding) as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        return cls(data)
    
    def to_json(self, filepath: str = None) -> str:
        """导出为JSON格式"""
        result = json.dumps(self.data, ensure_ascii=False, indent=2)
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result)
        return result
    
    def handle_missing(self, strategy: str = 'remove', 
                       fill_value: Any = None, 
                       columns: List[str] = None) -> 'DataCleaner':
        """
        处理缺失值
        - remove: 删除包含缺失值的行
        - fill: 填充指定值
        - fill_mean: 数值列填充平均值
        """
        columns = columns or []
        
        if strategy == 'remove':
            self.data = [row for row in self.data 
                        if all(row.get(col) for col in columns)] if columns else                        [row for row in self.data if any(row.values())]
        
        elif strategy == 'fill':
            self.data = [{col: (row.get(col) if row.get(col) else fill_value) 
                         for col in (columns or row.keys())} for row in self.data]
        
        elif strategy == 'fill_mean':
            num_cols = columns or [k for k in self.data[0].keys() 
                                   if self.data[0].get(k, '').replace('.','').replace('-','').isdigit()]
            for col in num_cols:
                values = [float(row[col]) for row in self.data if row.get(col)]
                if values:
                    avg = mean(values)
                    for row in self.data:
                        if not row.get(col):
                            row[col] = str(round(avg, 2))
        return self
    
    def normalize_text(self, columns: List[str] = None, 
                       lowercase: bool = True,
                       remove_special: bool = True) -> 'DataCleaner':
        """文本标准化"""
        columns = columns or []
        
        for row in self.data:
            for col in columns or row.keys():
                if isinstance(row.get(col), str):
                    text = row[col]
                    if lowercase:
                        text = text.lower()
                    if remove_special:
                        text = re.sub(r'[^\w\s]', '', text)
                    row[col] = text.strip()
        return self
    
    def remove_duplicates(self, key: str = None) -> 'DataCleaner':
        """删除重复项"""
        if key:
            seen = set()
            self.data = [row for row in self.data 
                        if not (row.get(key) in seen or seen.add(row.get(key)))]
        else:
            seen = set()
            self.data = [row for row in self.data 
                        if not (json.dumps(sorted(row.items())) in seen or 
                               seen.add(json.dumps(sorted(row.items()))))]
        return self
    
    def basic_stats(self) -> Dict[str, Any]:
        """基础统计分析"""
        if not self.data:
            return {}
        
        self.stats = {
            'total_rows': len(self.data),
            'columns': list(self.data[0].keys()) if self.data else [],
            'numeric_columns': [],
            'missing_values': {}
        }
        
        for col in self.stats['columns']:
            values = [row.get(col) for row in self.data if row.get(col)]
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass
            
            if len(numeric_values) > len(values) * 0.5:
                self.stats['numeric_columns'].append(col)
                if numeric_values:
                    self.stats[col] = {
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'mean': round(mean(numeric_values), 2),
                        'median': round(median(numeric_values), 2)
                    }
            
            missing = sum(1 for row in self.data if not row.get(col))
            if missing > 0:
                self.stats['missing_values'][col] = missing
        
        return self.stats
    
    def filter_by_value(self, column: str, 
                       operator: str, 
                       value: Any) -> 'DataCleaner':
        """按值过滤数据"""
        operators = {
            '>': lambda x, y: float(x) > float(y),
            '<': lambda x, y: float(x) < float(y),
            '>=': lambda x, y: float(x) >= float(y),
            '<=': lambda x, y: float(x) <= float(y),
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            'contains': lambda x, y: y.lower() in x.lower() if isinstance(x, str) else False
        }
        
        op_func = operators.get(operator, operators['=='])
        self.data = [row for row in self.data if op_func(row.get(column), value)]
        return self


def clean_csv(input_path: str, output_path: str = None, **kwargs) -> DataCleaner:
    """一键清洗CSV"""
    cleaner = DataCleaner.from_csv(input_path)
    if 'missing_strategy' in kwargs:
        cleaner.handle_missing(kwargs['missing_strategy'], kwargs.get('fill_value'))
    if 'normalize_columns' in kwargs:
        cleaner.normalize_text(kwargs['normalize_columns'])
    if 'dedup_key' in kwargs:
        cleaner.remove_duplicates(kwargs['dedup_key'])
    
    result = cleaner.to_json(output_path)
    cleaner.basic_stats()
    return cleaner, result


if __name__ == '__main__':
    print("🧹 Data Cleaner - 数据清洗工具")
    print("=" * 40)
    
    # 创建示例数据
    sample_data = [
        {"name": "Alice", "age": "25", "city": "Beijing"},
        {"name": "Bob", "age": "", "city": "shanghai"},
        {"name": "Alice", "age": "25", "city": "beijing"},
        {"name": "Charlie", "age": "30", "city": "Guangzhou"},
    ]
    
    cleaner = DataCleaner(sample_data)
    print(f"原始数据: {len(cleaner.data)} 条")
    
    # 处理缺失值
    cleaner.handle_missing('fill_mean', '0', ['age'])
    print(f"缺失值处理后: {len(cleaner.data)} 条")
    
    # 文本标准化
    cleaner.normalize_text(['city'], lowercase=True)
    print(f"城市标准化: {cleaner.data[0]['city']}")
    
    # 去重
    cleaner.remove_duplicates('name')
    print(f"去重后: {len(cleaner.data)} 条")
    
    # 统计
    stats = cleaner.basic_stats()
    print(f"\n统计信息: {json.dumps(stats, indent=2)}")
