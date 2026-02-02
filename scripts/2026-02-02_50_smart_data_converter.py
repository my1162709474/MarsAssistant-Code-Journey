#!/usr/bin/env python3
"""
智能数据转换器 - Smart Data Converter
支持多种数据格式（CSV/JSON/XML/YAML/TOML）之间的转换
日期: 2026-02-02
"""

import json
import csv
import xml.etree.ElementTree as ET
import yaml
import toml
import os
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class DataFormat(Enum):
    """支持的数据格式"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"
    TOML = "toml"


@dataclass
class ConversionResult:
    """转换结果"""
    success: bool
    data: Any
    error: Optional[str] = None


class SmartDataConverter:
    """智能数据转换器"""
    
    # CSV分隔符候选
    CSV_DELIMITERS = [',', ';', '\t', '|', ':']
    
    def __init__(self):
        self.conversion_history = []
    
    def detect_format(self, content: str) -> DataFormat:
        """自动检测数据格式"""
        content = content.strip()
        
        if not content:
            return DataFormat.JSON
        
        # 检测JSON
        try:
            json.loads(content)
            return DataFormat.JSON
        except:
            pass
        
        # 检测YAML
        try:
            yaml.safe_load(content)
            return DataFormat.YAML
        except:
            pass
        
        # 检测TOML
        try:
            toml.loads(content)
            return DataFormat.TOML
        except:
            pass
        
        # 检测XML
        try:
            ET.fromstring(content)
            return DataFormat.XML
        except:
            pass
        
        # 默认CSV
        return DataFormat.CSV
    
    def json_to_csv(self, data: List[Dict], 
                    output_path: Optional[str] = None,
                    delimiter: str = ',') -> ConversionResult:
        """JSON转换为CSV"""
        try:
            if not isinstance(data, list):
                data = [data]
            
            if not data:
                return ConversionResult(success=False, data=None, 
                                       error="Empty data")
            
            # 获取所有字段
            fields = set()
            for item in data:
                fields.update(item.keys())
            fields = sorted(fields)
            
            # 写入CSV
            result = []
            if output_path:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fields, 
                                           delimiter=delimiter)
                    writer.writeheader()
                    writer.writerows(data)
                result = f"CSV saved to {output_path}"
            else:
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=fields,
                                       delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
                result = output.getvalue()
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def csv_to_json(self, content: str,
                    output_path: Optional[str] = None) -> ConversionResult:
        """CSV转换为JSON"""
        try:
            # 检测分隔符
            delimiter = self._detect_csv_delimiter(content)
            
            import io
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            data = list(reader)
            
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                result = f"JSON saved to {output_path}"
            else:
                result = json.dumps(data, ensure_ascii=False, indent=2)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def json_to_xml(self, data: Any,
                    output_path: Optional[str] = None,
                    root_element: str = "root") -> ConversionResult:
        """JSON转换为XML"""
        try:
            if isinstance(data, dict):
                data = [data]
            
            root = ET.Element(root_element)
            
            for i, item in enumerate(data):
                item_elem = ET.SubElement(root, f"item_{i}")
                self._dict_to_xml(item, item_elem)
            
            result = None
            if output_path:
                tree = ET.ElementTree(root)
                tree.write(output_path, encoding='utf-8', 
                          xml_declaration=True)
                result = f"XML saved to {output_path}"
            else:
                result = ET.tostring(root, encoding='unicode')
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def xml_to_json(self, content: str,
                    output_path: Optional[str] = None) -> ConversionResult:
        """XML转换为JSON"""
        try:
            root = ET.fromstring(content)
            data = self._xml_to_dict(root)
            
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                result = f"JSON saved to {output_path}"
            else:
                result = json.dumps(data, ensure_ascii=False, indent=2)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def json_to_yaml(self, data: Any,
                     output_path: Optional[str] = None) -> ConversionResult:
        """JSON转换为YAML"""
        try:
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, 
                             default_flow_style=False)
                result = f"YAML saved to {output_path}"
            else:
                result = yaml.dump(data, allow_unicode=True,
                                  default_flow_style=False)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def yaml_to_json(self, content: str,
                     output_path: Optional[str] = None) -> ConversionResult:
        """YAML转换为JSON"""
        try:
            data = yaml.safe_load(content)
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                result = f"JSON saved to {output_path}"
            else:
                result = json.dumps(data, ensure_ascii=False, indent=2)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def json_to_toml(self, data: Any,
                     output_path: Optional[str] = None) -> ConversionResult:
        """JSON转换为TOML"""
        try:
            # TOML只支持字典，不支持嵌套结构
            def flatten_dict(d, parent_key=''):
                items = {}
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.update(flatten_dict(v, new_key))
                    else:
                        items[new_key] = v
                return items
            
            if isinstance(data, list) and data:
                data = {f"item_{i}": item for i, item in enumerate(data)}
            elif isinstance(data, dict):
                data = flatten_dict(data)
            
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    toml.dump(data, f)
                result = f"TOML saved to {output_path}"
            else:
                result = toml.dumps(data)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def toml_to_json(self, content: str,
                     output_path: Optional[str] = None) -> ConversionResult:
        """TOML转换为JSON"""
        try:
            data = toml.loads(content)
            result = None
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                result = f"JSON saved to {output_path}"
            else:
                result = json.dumps(data, ensure_ascii=False, indent=2)
            
            return ConversionResult(success=True, data=result)
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def convert(self, content: str, from_format: DataFormat, 
                to_format: DataFormat,
                output_path: Optional[str] = None) -> ConversionResult:
        """通用转换接口"""
        try:
            # 解析输入数据
            if from_format == DataFormat.JSON:
                data = json.loads(content)
            elif from_format == DataFormat.YAML:
                data = yaml.safe_load(content)
            elif from_format == DataFormat.TOML:
                data = toml.loads(content)
            elif from_format == DataFormat.XML:
                data = self.xml_to_json(content).data
            elif from_format == DataFormat.CSV:
                result = self.csv_to_json(content)
                if not result.success:
                    return result
                data = json.loads(result.data)
            else:
                return ConversionResult(success=False, data=None,
                                       error="Unsupported format")
            
            # 转换为目标格式
            if to_format == DataFormat.JSON:
                result = ConversionResult(success=True, 
                                         data=json.dumps(data, ensure_ascii=False, indent=2))
            elif to_format == DataFormat.YAML:
                result = self.json_to_yaml(data, output_path)
            elif to_format == DataFormat.TOML:
                result = self.json_to_toml(data, output_path)
            elif to_format == DataFormat.XML:
                result = self.json_to_xml(data, output_path)
            elif to_format == DataFormat.CSV:
                result = self.json_to_csv(data, output_path)
            
            if output_path and result.success and result.data:
                result.data = f"Saved to {output_path}"
            
            return result
        except Exception as e:
            return ConversionResult(success=False, data=None, 
                                   error=str(e))
    
    def _detect_csv_delimiter(self, content: str) -> str:
        """检测CSV分隔符"""
        if not content:
            return ','
        
        first_line = content.split('\n')[0]
        for delimiter in self.CSV_DELIMITERS:
            if delimiter in first_line:
                return delimiter
        return ','
    
    def _dict_to_xml(self, d: Dict, parent_elem):
        """字典转换为XML元素"""
        for key, value in d.items():
            child = ET.SubElement(parent_elem, str(key))
            if isinstance(value, dict):
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(child, f"item_{i}")
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem.text = str(item)
            else:
                child.text = str(value)
    
    def _xml_to_dict(self, elem) -> Dict:
        """XML元素转换为字典"""
        result = {}
        for child in elem:
            value = self._xml_to_dict(child)
            if child.text and not value:
                value = child.text.strip()
            result[child.tag] = value
        return result
    
    def batch_convert(self, files: List[str], to_format: DataFormat,
                      output_dir: str = "./output") -> List[ConversionResult]:
        """批量转换"""
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for file_path in files:
            if not os.path.exists(file_path):
                results.append(ConversionResult(success=False, data=None,
                                               error=f"File not found: {file_path}"))
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            from_format = self.detect_format(content)
            output_path = os.path.join(output_dir, 
                os.path.splitext(os.path.basename(file_path))[0] + 
                f".{to_format.value}")
            
            result = self.convert(content, from_format, to_format, output_path)
            results.append(result)
        
        return results


def demo():
    """演示"""
    print("=== 智能数据转换器演示 ===\n")
    
    converter = SmartDataConverter()
    
    # 示例JSON数据
    json_data = json.dumps([
        {"name": "张三", "age": 25, "city": "北京"},
        {"name": "李四", "age": 30, "city": "上海"},
        {"name": "王五", "age": 28, "city": "广州"}
    ], ensure_ascii=False)
    
    print("原始JSON数据:")
    print(json_data)
    print()
    
    # JSON转CSV
    print("1. JSON → CSV:")
    result = converter.json_to_csv(json.loads(json_data))
    print(result.data if result.success else f"错误: {result.error}")
    print()
    
    # JSON转YAML
    print("2. JSON → YAML:")
    result = converter.json_to_yaml(json.loads(json_data))
    print(result.data if result.success else f"错误: {result.error}")
    print()
    
    # JSON转XML
    print("3. JSON → XML:")
    result = converter.json_to_xml(json.loads(json_data))
    print(result.data if result.success else f"错误: {result.error}")
    print()
    
    # JSON转TOML
    print("4. JSON → TOML:")
    result = converter.json_to_toml(json.loads(json_data))
    print(result.data if result.success else f"错误: {result.error}")
    print()
    
    # 演示格式检测
    csv_content = """name,age,city
张三,25,北京
李四,30,上海"""
    
    print("5. 自动格式检测:")
    detected = converter.detect_format(csv_content)
    print(f"CSV内容检测结果: {detected.value}")
    print()
    
    print("=== 演示完成 ===")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        print("使用方式:")
        print("  python smart_data_converter.py --demo  # 运行演示")
        print("  python converter.py input.json csv output.csv  # 格式转换")
        print()
        print("支持的格式: json, csv, xml, yaml, toml")
        print()
        demo()
