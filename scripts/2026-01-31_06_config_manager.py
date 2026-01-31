#!/usr/bin/env python3
"""
📁 Config Manager - 配置文件管理器
=================================
支持 JSON 和 YAML 格式的配置文件的读取、创建和合并。

功能特性:
- ✅ JSON/YAML 格式支持
- 🔄 配置合并（支持嵌套）
- 📋 配置验证
- 💾 备份和恢复
- 🎨 美化输出

使用示例:
    from config_manager import ConfigManager
    config = ConfigManager.load("config.json")
    config.set("database.host", "localhost")
    config.save("config.json")
"""

import json
import yaml
import os
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class ConfigManager:
    """配置文件管理器类"""
    
    def __init__(self, data: Optional[Dict] = None):
        """初始化配置管理器"""
        self._data = data or {}
        self._history = []  # 操作历史
        
    @staticmethod
    def load(file_path: str, encoding: str = 'utf-8') -> 'ConfigManager':
        """
        从文件加载配置
        
        Args:
            file_path: 配置文件路径
            encoding: 文件编码
            
        Returns:
            ConfigManager 实例
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的格式
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
            
        if file_path.endswith('.json'):
            data = json.loads(content)
        elif file_path.endswith(('.yaml', '.yml')):
            data = yaml.safe_load(content)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")
        
        return ConfigManager(data)
    
    @staticmethod
    def create(file_path: str, data: Optional[Dict] = None, 
               encoding: str = 'utf-8') -> 'ConfigManager':
        """
        创建新配置文件
        
        Args:
            file_path: 配置文件路径
            data: 初始数据
            encoding: 文件编码
            
        Returns:
            ConfigManager 实例
        """
        manager = ConfigManager(data or {})
        manager.save(file_path, encoding=encoding)
        return manager
    
    def save(self, file_path: str, encoding: str = 'utf-8') -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 目标文件路径
            encoding: 文件编码
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            if file_path.endswith('.json'):
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            elif file_path.endswith(('.yaml', '.yml')):
                yaml.dump(self._data, f, allow_unicode=True, default_flow_style=False)
            else:
                raise ValueError(f"不支持的文件格式: {file_path}")
        
        self._history.append({
            'action': 'save',
            'file': file_path,
            'time': datetime.now().isoformat()
        })
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取嵌套配置值
        
        Args:
            key_path: 点分隔的路径，如 "database.host"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> 'ConfigManager':
        """
        设置嵌套配置值
        
        Args:
            key_path: 点分隔的路径
            value: 要设置的值
            
        Returns:
            self (支持链式调用)
        """
        keys = key_path.split('.')
        data = self._data
        
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        
        data[keys[-1]] = value
        self._history.append({
            'action': 'set',
            'key': key_path,
            'value': value,
            'time': datetime.now().isoformat()
        })
        
        return self
    
    def delete(self, key_path: str) -> bool:
        """
        删除配置项
        
        Args:
            key_path: 点分隔的路径
            
        Returns:
            是否成功删除
        """
        keys = key_path.split('.')
        data = self._data
        
        try:
            for key in keys[:-1]:
                data = data[key]
            del data[keys[-1]]
            self._history.append({
                'action': 'delete',
                'key': key_path,
                'time': datetime.now().isoformat()
            })
            return True
        except (KeyError, TypeError):
            return False
    
    def merge(self, other_config: Union['ConfigManager', Dict], 
              overwrite: bool = False) -> 'ConfigManager':
        """
        合并配置
        
        Args:
            other_config: 另一个配置管理器或字典
            overwrite: 是否覆盖已有值
            
        Returns:
            self
        """
        other_data = other_config._data if isinstance(other_config, ConfigManager) else other_config
        
        def _merge_dict(base: Dict, override: Dict, overwrite: bool) -> Dict:
            result = copy.deepcopy(base)
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = _merge_dict(result[key], value, overwrite)
                elif overwrite or key not in result:
                    result[key] = copy.deepcopy(value)
            return result
        
        self._data = _merge_dict(self._data, other_data, overwrite)
        self._history.append({
            'action': 'merge',
            'source': 'external',
            'overwrite': overwrite,
            'time': datetime.now().isoformat()
        })
        
        return self
    
    def validate(self, schema: Dict) -> tuple[bool, List[str]]:
        """
        验证配置是否符合模式
        
        Args:
            schema: JSON Schema 风格的模式
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        def _validate(data: Any, schema: Dict, path: str) -> None:
            # 必需字段检查
            if 'required' in schema:
                for required_field in schema['required']:
                    if required_field not in data:
                        errors.append(f"{path}: 缺少必需字段 '{required_field}'")
            
            # 类型检查
            if 'type' in schema and data is not None:
                expected_type = schema['type']
                type_map = {
                    'string': str,
                    'integer': int,
                    'number': (int, float),
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }
                if expected_type in type_map and not isinstance(data, type_map[expected_type]):
                    errors.append(f"{path}: 期望类型 {expected_type}，实际 {type(data).__name__}")
            
            # 枚举检查
            if 'enum' in schema and data not in schema['enum']:
                errors.append(f"{path}: 值必须在 {schema['enum']} 中")
        
        # 简化验证（仅验证顶层）
        for key, value in schema.get('properties', {}).items():
            if key in self._data:
                _validate(self._data[key], value, key)
        
        return len(errors) == 0, errors
    
    def backup(self, backup_dir: str = 'backups') -> str:
        """
        创建配置备份
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        path = Path(backup_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = path / f"config_backup_{timestamp}.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        
        self._history.append({
            'action': 'backup',
            'file': str(backup_path),
            'time': datetime.now().isoformat()
        })
        
        return str(backup_path)
    
    def to_dict(self) -> Dict:
        """返回配置的字典副本"""
        return copy.deepcopy(self._data)
    
    def to_json(self, indent: int = 2) -> str:
        """返回 JSON 格式的字符串"""
        return json.dumps(self._data, ensure_ascii=False, indent=indent)
    
    def to_yaml(self) -> str:
        """返回 YAML 格式的字符串"""
        return yaml.dump(self._data, allow_unicode=True, default_flow_style=False)
    
    def pretty_print(self) -> None:
        """美化打印配置"""
        print("📋 当前配置:")
        print("=" * 50)
        print(self.to_json())
        print("=" * 50)
    
    def get_history(self) -> List[Dict]:
        """获取操作历史"""
        return copy.deepcopy(self._history)


# ====== 使用示例 ======

if __name__ == "__main__":
    print("🔧 Config Manager - 配置文件管理器演示")
    print("=" * 50)
    
    # 创建配置
    config = ConfigManager()
    config.set("app.name", "MyApp")
    config.set("app.version", "1.0.0")
    config.set("database.host", "localhost")
    config.set("database.port", 3306)
    config.set("features.dark_mode", True)
    config.set("features.notifications", True)
    
    # 保存到文件
    config.save("example_config.json")
    print("✅ 已创建配置文件: example_config.json")
    
    # 读取配置
    loaded_config = ConfigManager.load("example_config.json")
    print(f"\n📖 读取的配置:")
    print(f"   应用名称: {loaded_config.get('app.name')}")
    print(f"   数据库主机: {loaded_config.get('database.host')}")
    
    # 修改配置
    loaded_config.set("database.port", 5432)
    loaded_config.save("example_config.json")
    print(f"\n✏️ 已更新数据库端口为 5432")
    
    # 合并配置
    new_config = ConfigManager({
        "database": {
            "password": "secret123"
        },
        "logging": {
            "level": "INFO"
        }
    })
    loaded_config.merge(new_config)
    loaded_config.save("example_config.json")
    print(f"\n🔄 已合并新配置")
    
    # 验证配置
    schema = {
        "type": "object",
        "required": ["app.name", "database.host"],
        "properties": {
            "app.name": {"type": "string"},
            "database.host": {"type": "string"}
        }
    }
    is_valid, errors = loaded_config.validate(schema)
    if is_valid:
        print(f"✅ 配置验证通过")
    else:
        print(f"❌ 配置验证失败: {errors}")
    
    # 创建备份
    backup_path = loaded_config.backup()
    print(f"\n💾 已创建备份: {backup_path}")
    
    # 显示最终配置
    print(f"\n📊 最终配置内容:")
    loaded_config.pretty_print()
    
    print("\n✨ 演示完成!")
