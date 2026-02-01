#!/usr/bin/env python3
"""
JSON Schema 验证器 - Day 14
用于验证JSON数据是否符合预定义的Schema规范

功能:
- 支持Draft-07 JSON Schema
- 递归验证嵌套对象
- 详细的错误报告
- 支持自定义校验规则
"""

import json
import re
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class SchemaType(Enum):
    """JSON Schema类型"""
    NULL = "null"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NUMBER = "number"
    INTEGER = "integer"
    STRING = "string"


@dataclass
class ValidationError:
    """验证错误"""
    path: str
    message: str
    schema_path: str = ""
    
    def __str__(self) -> str:
        return f"[{self.path}] {self.message}"


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    
    def add_error(self, error: ValidationError):
        self.errors.append(error)
        self.valid = False


class JSONSchemaValidator:
    """JSON Schema 验证器"""
    
    def __init__(self):
        self.custom_validators: Dict[str, Callable] = {}
    
    def register_validator(self, name: str, validator: Callable):
        """注册自定义验证器"""
        self.custom_validators[name] = validator
    
    def validate(self, data: Any, schema: Dict) -> ValidationResult:
        """验证数据是否符合Schema"""
        result = ValidationResult(valid=True)
        self._validate_recursive(data, schema, [], result, "")
        return result
    
    def _validate_recursive(
        self, 
        data: Any, 
        schema: Dict, 
        path: List[str], 
        result: ValidationResult,
        schema_path: str
    ):
        current_path = ".".join(path) if path else "(root)"
        
        # 处理 $ref
        if "$ref" in schema:
            ref_path = schema["$ref"]
            # 简化的ref处理，实际应该解析完整的JSON Schema $ref
            result.add_error(ValidationError(
                current_path, 
                f"$ref not fully supported: {ref_path}",
                schema_path
            ))
            return
        
        # 处理 anyOf, oneOf, allOf
        if "anyOf" in schema:
            errors = []
            for i, subschema in enumerate(schema["anyOf"]):
                sub_result = self.validate(data, subschema)
                if sub_result.valid:
                    return
                errors.extend(sub_result.errors)
            result.add_error(ValidationError(
                current_path,
                f"Data must match any of the schemas (tried {len(schema['anyOf'])})",
                schema_path
            ))
        
        if "oneOf" in schema:
            matches = 0
            errors = []
            for subschema in schema["oneOf"]:
                sub_result = self.validate(data, subschema)
                if sub_result.valid:
                    matches += 1
                else:
                    errors.extend(sub_result.errors)
            if matches == 0:
                result.add_error(ValidationError(
                    current_path,
                    f"Data must match exactly one schema (0 matches)",
                    schema_path
                ))
            elif matches > 1:
                result.add_error(ValidationError(
                    current_path,
                    f"Data matches {matches} schemas (should match exactly one)",
                    schema_path
                ))
        
        if "allOf" in schema:
            for subschema in schema["allOf"]:
                self._validate_recursive(data, subschema, path, result, schema_path)
        
        # 处理 type
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "null":
                if data is not None:
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected null, got {type(data).__name__}",
                        schema_path
                    ))
            elif expected_type == "boolean":
                if not isinstance(data, bool):
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected boolean, got {type(data).__name__}",
                        schema_path
                    ))
            elif expected_type == "object":
                if not isinstance(data, dict):
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected object, got {type(data).__name__}",
                        schema_path
                    ))
            elif expected_type == "array":
                if not isinstance(data, list):
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected array, got {type(data).__name__}",
                        schema_path
                    ))
            elif expected_type in ("number", "integer"):
                if not isinstance(data, (int, float)):
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected number, got {type(data).__name__}",
                        schema_path
                    ))
                    return
                if expected_type == "integer" and isinstance(data, float) and not data.is_integer():
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected integer, got float",
                        schema_path
                    ))
            elif expected_type == "string":
                if not isinstance(data, str):
                    result.add_error(ValidationError(
                        current_path,
                        f"Expected string, got {type(data).__name__}",
                        schema_path
                    ))
        
        # 处理 enum
        if "enum" in schema:
            if data not in schema["enum"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value must be one of {schema['enum']}, got {data}",
                    schema_path
                ))
        
        # 处理 const
        if "const" in schema:
            if data != schema["const"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value must be exactly {schema['const']}, got {data}",
                    schema_path
                ))
        
        # 处理 string 类型特有的验证
        if isinstance(data, str) and "string" in schema.get("type", ""):
            if "minLength" in schema and len(data) < schema["minLength"]:
                result.add_error(ValidationError(
                    current_path,
                    f"String length {len(data)} < minLength {schema['minLength']}",
                    schema_path
                ))
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                result.add_error(ValidationError(
                    current_path,
                    f"String length {len(data)} > maxLength {schema['maxLength']}",
                    schema_path
                ))
            if "pattern" in schema:
                if not re.match(schema["pattern"], data):
                    result.add_error(ValidationError(
                        current_path,
                        f"String does not match pattern: {schema['pattern']}",
                        schema_path
                    ))
            if "format" in schema:
                self._validate_format(data, schema["format"], current_path, result, schema_path)
        
        # 处理 number/integer 类型特有的验证
        if isinstance(data, (int, float)) and "number" in schema.get("type", ""):
            if "minimum" in schema and data < schema["minimum"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value {data} < minimum {schema['minimum']}",
                    schema_path
                ))
            if "maximum" in schema and data > schema["maximum"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value {data} > maximum {schema['maximum']}",
                    schema_path
                ))
            if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value {data} <= exclusiveMinimum {schema['exclusiveMinimum']}",
                    schema_path
                ))
            if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Value {data} >= exclusiveMaximum {schema['exclusiveMaximum']}",
                    schema_path
                ))
            if "multipleOf" in schema and data % schema["multipleOf"] != 0:
                result.add_error(ValidationError(
                    current_path,
                    f"Value {data} is not a multiple of {schema['multipleOf']}",
                    schema_path
                ))
        
        # 处理 array 类型特有的验证
        if isinstance(data, list):
            if "minItems" in schema and len(data) < schema["minItems"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Array length {len(data)} < minItems {schema['minItems']}",
                    schema_path
                ))
            if "maxItems" in schema and len(data) > schema["maxItems"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Array length {len(data)} > maxItems {schema['maxItems']}",
                    schema_path
                ))
            if "uniqueItems" in schema and schema["uniqueItems"]:
                if len(data) != len(set(json.dumps(item) for item in data)):
                    result.add_error(ValidationError(
                        current_path,
                        "Array items must be unique",
                        schema_path
                    ))
            
            # 验证 items
            if "items" in schema:
                if isinstance(schema["items"], dict):
                    # Single schema for all items
                    for i, item in enumerate(data):
                        new_path = path + [f"[{i}]"]
                        self._validate_recursive(item, schema["items"], new_path, result, schema_path)
                elif isinstance(schema["items"], list):
                    # Tuple validation
                    min_items = len(schema["items"])
                    if len(data) < min_items:
                        result.add_error(ValidationError(
                            current_path,
                            f"Array length {len(data)} < items length {min_items}",
                            schema_path
                        ))
                    for i, item_schema in enumerate(schema["items"]):
                        if i < len(data):
                            new_path = path + [f"[{i}]"]
                            self._validate_recursive(data[i], item_schema, new_path, result, schema_path)
        
        # 处理 object 类型特有的验证
        if isinstance(data, dict):
            if "minProperties" in schema and len(data) < schema["minProperties"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Object has {len(data)} properties, min is {schema['minProperties']}",
                    schema_path
                ))
            if "maxProperties" in schema and len(data) > schema["maxProperties"]:
                result.add_error(ValidationError(
                    current_path,
                    f"Object has {len(data)} properties, max is {schema['maxProperties']}",
                    schema_path
                ))
            
            # 验证 required
            if "required" in schema:
                for required_field in schema["required"]:
                    if required_field not in data:
                        new_path = path + [required_field]
                        result.add_error(ValidationError(
                            ".".join(new_path),
                            f"Missing required property '{required_field}'",
                            schema_path
                        ))
            
            # 验证 properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    if prop_name in data:
                        new_path = path + [prop_name]
                        self._validate_recursive(data[prop_name], prop_schema, new_path, result, schema_path)
            
            # 验证 additionalProperties
            if "additionalProperties" in schema:
                if isinstance(schema["additionalProperties"], bool):
                    if not schema["additionalProperties"]:
                        for prop_name in data:
                            if prop_name not in schema.get("properties", {}):
                                result.add_error(ValidationError(
                                    ".".join(path + [prop_name]),
                                    f"Additional property '{prop_name}' not allowed",
                                    schema_path
                                ))
                else:
                    for prop_name in data:
                        if prop_name not in schema.get("properties", {}):
                            new_path = path + [prop_name]
                            self._validate_recursive(data[prop_name], schema["additionalProperties"], new_path, result, schema_path)
            
            # 验证 patternProperties
            if "patternProperties" in schema:
                for pattern, prop_schema in schema["patternProperties"].items():
                    for prop_name in data:
                        if re.match(pattern, prop_name):
                            new_path = path + [prop_name]
                            self._validate_recursive(data[prop_name], prop_schema, new_path, result, schema_path)
            
            # 验证 propertyNames
            if "propertyNames" in schema:
                for prop_name in data:
                    self._validate_recursive(prop_name, schema["propertyNames"], path + [prop_name], result, schema_path)
        
        # 处理 dependencies
        if "dependencies" in schema:
            for dep_property, deps in schema["dependencies"].items():
                if dep_property in data:
                    if isinstance(deps, list):
                        for dep in deps:
                            if dep not in data:
                                result.add_error(ValidationError(
                                    current_path,
                                    f"Property '{dep}' is required when '{dep_property}' is present",
                                    schema_path
                                ))
                    else:
                        self._validate_recursive(data, deps, path, result, schema_path)
    
    def _validate_format(
        self, 
        data: str, 
        format_type: str, 
        path: str, 
        result: ValidationResult,
        schema_path: str
    ):
        """验证字符串格式"""
        patterns = {
            "date-time": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "time": r"^\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "hostname": r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
            "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            "ipv6": r"^(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",
            "uri": r"^[a-zA-Z][a-zA-Z0-9+.-]*:[^\s]*$",
            "uri-reference": r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:[^\s]*|#[^\s]*|/[^\s]*|\\[^\\s]*|[^\s]*)$",
        }
        
        if format_type in patterns:
            if not re.match(patterns[format_type], data):
                result.add_error(ValidationError(
                    path,
                    f"String does not match format '{format_type}'",
                    schema_path
                ))


def demo():
    """演示JSON Schema验证器"""
    validator = JSONSchemaValidator()
    
    # 示例Schema: 用户信息
    user_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 50
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1
            }
        },
        "required": ["name", "email"],
        "additionalProperties": False
    }
    
    # 测试数据
    valid_user = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "tags": ["developer", "python"]
    }
    
    invalid_user = {
        "email": "invalid-email",
        "age": 200,
        "tags": []
    }
    
    # 验证
    print("=" * 60)
    print("JSON Schema Validator Demo - Day 14")
    print("=" * 60)
    
    print("\n[1] 验证有效数据:")
    result = validator.validate(valid_user, user_schema)
    print(f"   有效: {result.valid}")
    if result.valid:
        print("   ✓ 数据符合Schema规范")
    
    print("\n[2] 验证无效数据:")
    result = validator.validate(invalid_user, user_schema)
    print(f"   有效: {result.valid}")
    for error in result.errors:
        print(f"   ✗ {error}")
    
    # 嵌套对象验证
    print("\n[3] 嵌套对象验证:")
    nested_schema = {
        "type": "object",
        "properties": {
            "company": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "employees": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"}
                            },
                            "required": ["id", "name"]
                        }
                    }
                },
                "required": ["name"]
            }
        }
    }
    
    nested_data = {
        "company": {
            "name": "Tech Corp",
            "employees": [
                {"id": 1, "name": "Alice"},
                {"id": 2}  # 缺少name
            ]
        }
    }
    
    result = validator.validate(nested_data, nested_schema)
    print(f"   有效: {result.valid}")
    for error in result.errors:
        print(f"   ✗ {error}")
    
    print("\n" + "=" * 60)
    print("验证完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
