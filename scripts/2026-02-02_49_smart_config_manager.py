#!/usr/bin/env python3
"""
智能配置文件管理器 - Smart Config Manager
功能：解析、验证和转换各种配置文件格式（JSON/YAML/TOML/INI）

作者：AI Assistant
日期：2026-02-02
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ConfigFormat(Enum):
    """支持的配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"


@dataclass
class ConfigValidationError:
    """配置验证错误"""
    path: str
    error_type: str
    message: str
    line: Optional[int] = None


@dataclass
class ConfigSection:
    """配置节（用于INI格式）"""
    name: str
    options: Dict[str, str] = field(default_factory=dict)


class ConfigManager:
    """智能配置文件管理器"""
    
    # 文件扩展名到格式的映射
    FORMAT_EXTENSIONS = {
        '.json': ConfigFormat.JSON,
        '.yaml': ConfigFormat.YAML,
        '.yml': ConfigFormat.YAML,
        '.toml': ConfigFormat.TOML,
        '.ini': ConfigFormat.INI,
        '.env': ConfigFormat.ENV,
    }
    
    def __init__(self):
        self.errors: List[ConfigValidationError] = []
    
    def detect_format(self, file_path: Union[str, Path]) -> ConfigFormat:
        """自动检测配置文件格式"""
        ext = Path(file_path).suffix.lower()
        return self.FORMAT_EXTENSIONS.get(ext, ConfigFormat.JSON)
    
    def load(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载配置文件"""
        format_type = self.detect_format(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse(content, format_type)
    
    def parse(self, content: str, format_type: ConfigFormat) -> Dict[str, Any]:
        """解析配置文件内容"""
        if format_type == ConfigFormat.JSON:
            return self._parse_json(content)
        elif format_type == ConfigFormat.YAML:
            return self._parse_yaml(content)
        elif format_type == ConfigFormat.TOML:
            return self._parse_toml(content)
        elif format_type == ConfigFormat.INI:
            return self._parse_ini(content)
        elif format_type == ConfigFormat.ENV:
            return self._parse_env(content)
        else:
            raise ValueError(f"不支持的格式: {format_type}")
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析JSON配置"""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.errors.append(ConfigValidationError(
                path="<content>",
                error_type="JSONParseError",
                message=str(e),
                line=e.lineno
            ))
            return {}
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """解析YAML配置"""
        try:
            import yaml
            return yaml.safe_load(content) or {}
        except ImportError:
            # 简单YAML解析（无PyYAML时）
            return self._simple_yaml_parse(content)
        except yaml.YAMLError as e:
            self.errors.append(ConfigValidationError(
                path="<content>",
                error_type="YAMLParseError",
                message=str(e)
            ))
            return {}
    
    def _simple_yaml_parse(self, content: str) -> Dict[str, Any]:
        """简单YAML解析（无依赖版本）"""
        result = {}
        current_section = None
        indent_stack = []
        
        for line_no, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 计算缩进
            indent = len(line) - len(line.lstrip())
            
            # 处理缩进变化
            while indent_stack and indent <= indent_stack[-1]:
                indent_stack.pop()
                current_section = None
            
            # 解析键值对
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if not value:  # 嵌套结构
                    indent_stack.append(indent)
                    current_section = key
                    if current_section not in result:
                        result[current_section] = {}
                else:
                    parsed_value = self._parse_value(value)
                    if current_section and isinstance(result.get(current_section), dict):
                        result[current_section][key] = parsed_value
                    else:
                        result[key] = parsed_value
        
        return result
    
    def _parse_value(self, value: str) -> Any:
        """解析YAML值"""
        value = value.strip()
        
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value == 'null' or value == '~':
            return None
        elif re.match(r'^-?\d+\.\d+$', value):
            return float(value)
        elif re.match(r'^-?\d+$', value):
            return int(value)
        elif (value.startswith('"') and value.endswith('"')) or \
             (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        elif value.startswith('[') and value.endswith(']'):
            items = [self._parse_value(v.strip()) for v in value[1:-1].split(',')]
            return items
        
        return value
    
    def _parse_toml(self, content: str) -> Dict[str, Any]:
        """解析TOML配置"""
        try:
            import tomllib
        except ImportError:
            try:
                import toml
                return toml.loads(content)
            except ImportError:
                return self._simple_toml_parse(content)
        
        try:
            return tomllib.loads(content)
        except Exception as e:
            self.errors.append(ConfigValidationError(
                path="<content>",
                error_type="TOMLParseError",
                message=str(e)
            ))
            return {}
    
    def _simple_toml_parse(self, content: str) -> Dict[str, Any]:
        """简单TOML解析（无依赖版本）"""
        result = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                result[current_section] = {}
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                parsed_value = self._parse_toml_value(value)
                
                if current_section:
                    result[current_section][key] = parsed_value
                else:
                    result[key] = parsed_value
        
        return result
    
    def _parse_toml_value(self, value: str) -> Any:
        """解析TOML值"""
        value = value.strip()
        
        if value in ('true', 'false'):
            return value == 'true'
        elif value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        elif '.' in value and all(c.isdigit() or c == '.' for c in value):
            return float(value)
        elif value.isdigit():
            return int(value)
        
        return value.strip('"')
    
    def _parse_ini(self, content: str) -> Dict[str, Any]:
        """解析INI配置"""
        result = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                result[current_section] = {}
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if current_section:
                    result[current_section][key] = value
                else:
                    result[key] = value
        
        return result
    
    def _parse_env(self, content: str) -> Dict[str, Any]:
        """解析.env配置"""
        result = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 去除引号
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                result[key] = value
        
        return result
    
    def validate(self, config: Dict[str, Any], schema: Optional[Dict] = None) -> bool:
        """验证配置是否符合Schema"""
        self.errors = []
        
        if schema:
            self._validate_against_schema(config, schema, '')
        
        return len(self.errors) == 0
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any], path: str):
        """根据Schema验证数据"""
        for field, rules in schema.items():
            if not isinstance(rules, dict):
                continue
            
            value = data.get(field) if isinstance(data, dict) else None
            
            # 类型检查
            if 'type' in rules:
                expected_type = rules['type']
                if value is not None and not isinstance(value, expected_type):
                    self.errors.append(ConfigValidationError(
                        path=f"{path}.{field}",
                        error_type="TypeMismatch",
                        message=f"期望类型 {expected_type.__name__}，实际 {type(value).__name__}"
                    ))
            
            # 必需字段检查
            if rules.get('required', False) and value is None:
                self.errors.append(ConfigValidationError(
                    path=f"{path}.{field}",
                    error_type="MissingRequired",
                    message=f"缺少必需的字段: {field}"
                ))
            
            # 枚举值检查
            if 'enum' in rules and value not in rules['enum']:
                self.errors.append(ConfigValidationError(
                    path=f"{path}.{field}",
                    error_type="InvalidEnum",
                    message=f"值必须是 {rules['enum']} 之一"
                ))
            
            # 范围检查
            if 'min' in rules and isinstance(value, (int, float)) and value < rules['min']:
                self.errors.append(ConfigValidationError(
                    path=f"{path}.{field}",
                    error_type="ValueTooSmall",
                    message=f"值必须 >= {rules['min']}"
                ))
            
            if 'max' in rules and isinstance(value, (int, float)) and value > rules['max']:
                self.errors.append(ConfigValidationError(
                    path=f"{path}.{field}",
                    error_type="ValueTooLarge",
                    message=f"值必须 <= {rules['max']}"
                ))
    
    def convert(self, config: Dict[str, Any], target_format: ConfigFormat) -> str:
        """转换配置到目标格式"""
        if target_format == ConfigFormat.JSON:
            return json.dumps(config, indent=2, ensure_ascii=False)
        elif target_format == ConfigFormat.YAML:
            return self._dict_to_yaml(config)
        elif target_format == ConfigFormat.TOML:
            return self._dict_to_toml(config)
        elif target_format == ConfigFormat.INI:
            return self._dict_to_ini(config)
        elif target_format == ConfigFormat.ENV:
            return self._dict_to_env(config)
        else:
            raise ValueError(f"不支持的格式: {target_format}")
    
    def _dict_to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """字典转YAML"""
        lines = []
        prefix = '  ' * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    lines.append(f"{prefix}  - {item}")
            elif isinstance(value, str):
                lines.append(f"{prefix}{key}: {value}")
            elif isinstance(value, bool):
                lines.append(f"{prefix}{key}: {str(value).lower()}")
            elif value is None:
                lines.append(f"{prefix}{key}: null")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return '\n'.join(lines)
    
    def _dict_to_toml(self, data: Dict[str, Any], section: str = None) -> str:
        """字典转TOML"""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"[{key}]")
                lines.append(self._dict_to_toml(value, key))
            elif isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f'{key} = {str(value).lower()}')
            elif isinstance(value, (int, float)):
                lines.append(f'{key} = {value}')
            elif isinstance(value, list):
                items = ', '.join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                lines.append(f'{key} = [{items}]')
        
        return '\n'.join(lines)
    
    def _dict_to_ini(self, data: Dict[str, Any], section: str = 'default') -> str:
        """字典转INI"""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"[{key}]")
                for k, v in value.items():
                    lines.append(f"{k} = {v}")
            else:
                lines.append(f"{key} = {value}")
        
        return '\n'.join(lines)
    
    def _dict_to_env(self, data: Dict[str, Any], prefix: str = '') -> str:
        """字典转ENV"""
        lines = []
        
        for key, value in data.items():
            env_key = f"{prefix}{key}".upper()
            if isinstance(value, dict):
                lines.append(self._dict_to_env(value, f"{env_key}_"))
            else:
                lines.append(f"{env_key}={value}")
        
        return '\n'.join(lines)
    
    def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置，override覆盖base"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_nested(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """获取嵌套配置值"""
        keys = path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set_nested(self, config: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
        """设置嵌套配置值"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return config


def demo():
    """演示函数"""
    print("🛠️  智能配置文件管理器演示")
    print("=" * 50)
    
    manager = ConfigManager()
    
    # 演示JSON解析
    json_config = '''
    {
        "database": {
            "host": "localhost",
            "port": 5432,
            "enabled": true
        },
        "logging": {
            "level": "INFO",
            "output": "/var/log/app.log"
        }
    }
    '''
    print("\n📄 解析JSON配置:")
    config = manager.parse(json_config, ConfigFormat.JSON)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 演示YAML解析
    yaml_config = '''
    app:
      name: MyApp
      version: 1.0.0
      features:
        - auth
        - cache
        - logging
      
    database:
      host: db.example.com
      port: 3306
      pool_size: 10
    '''
    print("\n📄 解析YAML配置:")
    config = manager.parse(yaml_config, ConfigFormat.YAML)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 演示格式转换
    print("\n🔄 JSON → YAML 转换:")
    yaml_output = manager.convert(config, ConfigFormat.YAML)
    print(yaml_output)
    
    # 演示INI解析
    ini_config = '''
    [database]
    host = localhost
    port = 5432
    name = myapp
    
    [redis]
    host = localhost
    port = 6379
    '''
    print("\n📄 解析INI配置:")
    config = manager.parse(ini_config, ConfigFormat.INI)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 演示.env解析
    env_config = '''
    # 数据库配置
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=myapp
    
    # Redis配置
    REDIS_HOST=localhost
    REDIS_PORT=6379
    '''
    print("\n📄 解析.env配置:")
    config = manager.parse(env_config, ConfigFormat.ENV)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 演示验证
    print("\n✅ 配置验证:")
    test_config = {
        "host": "localhost",
        "port": 5432,
        "debug": True
    }
    schema = {
        "host": {"type": str, "required": True},
        "port": {"type": int, "required": True, "min": 1, "max": 65535},
        "debug": {"type": bool}
    }
    is_valid = manager.validate(test_config, schema)
    print(f"验证结果: {'通过 ✅' if is_valid else '失败 ❌'}")
    for error in manager.errors:
        print(f"  - {error.path}: {error.message}")
    
    # 演示嵌套值获取
    print("\n🔍 嵌套值获取:")
    nested_config = {
        "database": {
            "primary": {
                "host": "db1.example.com",
                "port": 5432
            }
        }
    }
    host = manager.get_nested(nested_config, "database.primary.host")
    print(f"database.primary.host = {host}")
    
    # 演示配置合并
    print("\n🔀 配置合并:")
    base = {"app": {"name": "MyApp", "version": "1.0.0"}}
    override = {"app": {"version": "2.0.0", "debug": True}}
    merged = manager.merge(base, override)
    print(f"合并结果: {json.dumps(merged, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    demo()
