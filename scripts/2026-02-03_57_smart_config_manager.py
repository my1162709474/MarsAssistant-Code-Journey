#!/usr/bin/env python3
"""
智能配置管理器 - Smart Configuration Manager
============================================

一个通用的配置管理工具，支持多种格式的配置文件处理。

功能特性:
- 多格式支持: JSON, YAML, TOML, INI, ENV
- 配置验证: JSON Schema 验证
- 环境切换: 开发/测试/生产环境配置隔离
- 敏感信息: 自动加密/解密敏感配置
- 配置合并: 智能合并多来源配置
- 热重载: 监听配置文件变更

使用示例:
    # 基本使用
    config = ConfigManager("config.json")
    value = config.get("database.host")

    # 多环境切换
    config = ConfigManager("config.yaml", env="production")

    # 带模式验证
    config = ConfigManager("config.json", schema="schema.json")

作者: MarsAssistant
日期: 2026-02-03
"""

import json
import os
import hashlib
import base64
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from cryptography.fernet import Fernet
import re


class ConfigFormat(Enum):
    """支持的配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"


class ConfigError(Exception):
    """配置相关错误"""
    pass


@dataclass
class ConfigValidationError:
    """验证错误详情"""
    path: str
    message: str
    value: Any
    expected: Optional[str] = None


@dataclass
class ConfigHistoryEntry:
    """配置变更历史条目"""
    timestamp: str
    path: str
    old_value: Any
    new_value: Any
    source: str = "manual"


class ConfigChangeCallback:
    """配置变更回调"""
    def __init__(self, path_pattern: str, callback: Callable):
        self.pattern = re.compile(path_pattern)
        self.callback = callback


class ConfigManager:
    """
    智能配置管理器主类
    
    Attributes:
        config_path: 配置文件路径
        config_data: 配置数据字典
        format: 配置文件格式
        env: 当前环境
        schema: JSON Schema 定义
        history: 配置变更历史
        _lock: 线程锁
        _watchers: 文件监听器列表
    """
    
    def __init__(
        self,
        config_path: str,
        env: str = "development",
        schema: Optional[Dict] = None,
        auto_save: bool = True,
        secret_key: Optional[str] = None
    ):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            env: 环境名称 (development/staging/production)
            schema: JSON Schema 验证定义
            auto_save: 是否自动保存
            secret_key: 加密密钥 (用于敏感信息)
        """
        self.config_path = Path(config_path)
        self.env = env
        self.auto_save = auto_save
        self.schema = schema
        self.history: List[ConfigHistoryEntry] = []
        self._lock = threading.RLock()
        self._watchers: List[threading.Thread] = []
        self._change_callbacks: List[ConfigChangeCallback] = []
        
        # 加密器设置
        self._secret_key = secret_key
        if secret_key:
            self._fernet = Fernet(secret_key.encode() if isinstance(secret_key, str) else secret_key)
        else:
            self._fernet = None
        
        # 检测文件格式
        self.format = self._detect_format()
        
        # 加载配置
        self.config_data: Dict[str, Any] = {}
        if self.config_path.exists():
            self._load()
        else:
            self._create_default()
        
        # 环境特定配置
        self._apply_env_overrides()
        
        # 应用敏感信息解密
        if self._fernet:
            self._decrypt_sensitive()
    
    def _detect_format(self) -> ConfigFormat:
        """检测配置文件格式"""
        suffix = self.config_path.suffix.lower()
        format_map = {
            ".json": ConfigFormat.JSON,
            ".yaml": ConfigFormat.YAML,
            ".yml": ConfigFormat.YAML,
            ".toml": ConfigFormat.TOML,
            ".ini": ConfigFormat.INI,
            ".env": ConfigFormat.ENV,
        }
        return format_map.get(suffix, ConfigFormat.JSON)
    
    def _load(self) -> None:
        """加载配置文件"""
        with self._lock:
            try:
                if self.format == ConfigFormat.JSON:
                    self._load_json()
                elif self.format == ConfigFormat.YAML:
                    self._load_yaml()
                elif self.format == ConfigFormat.TOML:
                    self._load_toml()
                elif self.format == ConfigFormat.INI:
                    self._load_ini()
                elif self.format == ConfigFormat.ENV:
                    self._load_env()
            except Exception as e:
                raise ConfigError(f"加载配置文件失败: {e}")
    
    def _load_json(self) -> None:
        """加载 JSON 配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config_data = json.load(f)
    
    def _load_yaml(self) -> None:
        """加载 YAML 配置文件"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except ImportError:
            raise ConfigError("需要安装 pyyaml: pip install pyyaml")
    
    def _load_toml(self) -> None:
        """加载 TOML 配置文件"""
        try:
            import toml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = toml.load(f)
        except ImportError:
            raise ConfigError("需要安装 toml: pip install toml")
    
    def _load_ini(self) -> None:
        """加载 INI 配置文件"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding='utf-8')
        self.config_data = {section: dict(parser[section]) for section in parser.sections()}
    
    def _load_env(self) -> None:
        """加载 ENV 配置文件"""
        self.config_data = {}
        with open(self.config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    self.config_data[key.strip()] = value.strip()
    
    def _create_default(self) -> None:
        """创建默认配置"""
        self.config_data = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "app_db"
            },
            "environments": {
                "development": {},
                "staging": {},
                "production": {}
            }
        }
        if self.auto_save:
            self._save()
    
    def _apply_env_overrides(self) -> None:
        """应用环境特定的配置覆盖"""
        if "environments" in self.config_data:
            env_config = self.config_data["environments"].get(self.env, {})
            self._merge_dict(self.config_data, env_config)
    
    def _merge_dict(self, base: Dict, override: Dict) -> None:
        """递归合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value
    
    def _save(self) -> None:
        """保存配置文件"""
        with self._lock:
            try:
                if self.format == ConfigFormat.JSON:
                    self._save_json()
                elif self.format == ConfigFormat.YAML:
                    self._save_yaml()
                elif self.format == ConfigFormat.TOML:
                    self._save_toml()
                elif self.format == ConfigFormat.INI:
                    self._save_ini()
                elif self.format == ConfigFormat.ENV:
                    self._save_env()
            except Exception as e:
                raise ConfigError(f"保存配置文件失败: {e}")
    
    def _save_json(self) -> None:
        """保存 JSON 配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)
    
    def _save_yaml(self) -> None:
        """保存 YAML 配置文件"""
        try:
            import yaml
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ConfigError("需要安装 pyyaml: pip install pyyaml")
    
    def _save_toml(self) -> None:
        """保存 TOML 配置文件"""
        try:
            import toml
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(self.config_data, f)
        except ImportError:
            raise ConfigError("需要安装 toml: pip install toml")
    
    def _save_ini(self) -> None:
        """保存 INI 配置文件"""
        import configparser
        parser = configparser.ConfigParser()
        for section, values in self.config_data.items():
            parser[section] = open(self.config_path values
        with, 'w', encoding='utf-8') as f:
            parser.write(f)
    
    def _save_env(self) -> None:
        """保存 ENV 配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            for key, value in self.config_data.items():
                f.write(f"{key}={value}\n")
    
    # ==================== 核心 API ====================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径 (如 "database.host")
            default: 默认值
            
        Returns:
            配置值
            
        Examples:
            config.get("database.host")
            config.get("app.debug", False)
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, source: str = "manual") -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
            source: 变更来源
            
        Examples:
            config.set("app.debug", True)
            config.set("database.port", 5432)
        """
        keys = key.split('.')
        target = self.config_data
        
        # 记录历史
        old_value = self.get(key)
        history_entry = ConfigHistoryEntry(
            timestamp=self._get_timestamp(),
            path=key,
            old_value=old_value,
            new_value=value,
            source=source
        )
        self.history.append(history_entry)
        
        # 设置值
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        
        # 自动保存
        if self.auto_save:
            self._save()
        
        # 触发回调
        self._trigger_callbacks(key, value)
    
    def delete(self, key: str) -> bool:
        """
        删除配置项
        
        Args:
            key: 配置键
            
        Returns:
            是否成功删除
        """
        keys = key.split('.')
        target = self.config_data
        
        for k in keys[:-1]:
            if k not in target:
                return False
            target = target[k]
        
        if keys[-1] in target:
            del target[keys[-1]]
            if self.auto_save:
                self._save()
            return True
        return False
    
    def has(self, key: str) -> bool:
        """
        检查配置项是否存在
        
        Args:
            key: 配置键
            
        Returns:
            是否存在
        """
        return self.get(key) is not None
    
    def keys(self, prefix: str = "") -> List[str]:
        """
        获取所有配置键
        
        Args:
            prefix: 键前缀过滤
            
        Returns:
            配置键列表
        """
        keys = []
        self._collect_keys(self.config_data, prefix, keys)
        return keys
    
    def _collect_keys(self, data: Any, prefix: str, keys: List[str]) -> None:
        """递归收集所有键"""
        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict) and v:
                    self._collect_keys(v, new_key, keys)
                else:
                    keys.append(new_key)
    
    def all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self.config_data.copy()
    
    def merge(self, other_config: Dict, overwrite: bool = False) -> None:
        """
        合并其他配置
        
        Args:
            other_config: 其他配置字典
            overwrite: 是否覆盖已有值
        """
        if overwrite:
            self.config_data.update(other_config)
        else:
            self._merge_dict(self.config_data, other_config)
        
        if self.auto_save:
            self._save()
    
    def reset(self) -> None:
        """重置为默认配置"""
        self.config_data = {}
        self.history = []
        self._create_default()
    
    # ==================== 环境管理 ====================
    
    def set_env(self, env: str) -> None:
        """
        切换环境
        
        Args:
            env: 环境名称
        """
        self.env = env
        self._apply_env_overrides()
        
        if self.auto_save:
            self._save()
    
    def get_env(self) -> str:
        """获取当前环境"""
        return self.env
    
    def get_available_envs(self) -> List[str]:
        """获取可用环境列表"""
        if "environments" in self.config_data:
            return list(self.config_data["environments"].keys())
        return ["development", "staging", "production"]
    
    # ==================== 验证功能 ====================
    
    def validate(self) -> List[ConfigValidationError]:
        """
        验证配置
        
        Returns:
            验证错误列表
        """
        errors = []
        
        if self.schema:
            errors.extend(self._validate_with_schema())
        
        return errors
    
    def _validate_with_schema(self) -> List[ConfigValidationError]:
        """使用 JSON Schema 验证"""
        errors = []
        
        if not self.schema:
            return errors
        
        def validate_object(data: Any, schema: Dict, path: str) -> None:
            """递归验证对象"""
            if not isinstance(data, dict):
                if schema.get("type") == "object" and data is not None:
                    errors.append(ConfigValidationError(
                        path=path,
                        message="类型不匹配",
                        value=data,
                        expected="object"
                    ))
                return
            
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            
            # 检查必需字段
            for field in required:
                if field not in data:
                    errors.append(ConfigValidationError(
                        path=f"{path}.{field}",
                        message="缺少必需字段",
                        value=None,
                        expected=field
                    ))
            
            # 验证各字段
            for key, value in data.items():
                if key in properties:
                    validate_object(value, properties[key], f"{path}.{key}")
        
        validate_object(self.config_data, self.schema, "root")
        return errors
    
    def load_schema(self, schema_path: Union[str, Dict]) -> None:
        """
        加载 JSON Schema
        
        Args:
            schema_path: Schema 文件路径或字典
        """
        if isinstance(schema_path, dict):
            self.schema = schema_path
        else:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
    
    # ==================== 敏感信息 ====================
    
    def encrypt_sensitive(self, key: str, value: str) -> str:
        """
        加密敏感信息
        
        Args:
            key: 配置键
            value: 原始值
            
        Returns:
            加密后的值
            
        Raises:
            ConfigError: 如果未设置密钥
        """
        if not self._fernet:
            raise ConfigError("未设置加密密钥，无法加密敏感信息")
        
        encrypted = self._fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_sensitive(self, key: str) -> str:
        """
        解密敏感信息
        
        Args:
            key: 配置键
            
        Returns:
            解密后的值
        """
        if not self._fernet:
            raise ConfigError("未设置加密密钥，无法解密敏感信息")
        
        encrypted = self.get(key)
        if not encrypted:
            return ""
        
        decoded = base64.b64decode(encrypted)
        decrypted = self._fernet.decrypt(decoded)
        return decrypted.decode()
    
    def _decrypt_sensitive(self) -> None:
        """自动解密所有敏感字段"""
        if not self._fernet:
            return
        
        for key in self.keys():
            if key.endswith("_encrypted") or key.endswith("_secret"):
                try:
                    decrypted = self.decrypt_sensitive(key)
                    clean_key = key.rsplit("_", 1)[0]
                    self.set(clean_key, decrypted)
                    self.delete(key)
                except Exception:
                    pass
    
    def mark_sensitive(self, key: str) -> None:
        """
        将配置项标记为敏感并加密
        
        Args:
            key: 配置键
        """
        value = self.get(key)
        if value is None:
            return
        
        encrypted = self.encrypt_sensitive(key, str(value))
        self.set(key, encrypted)
    
    # ==================== 变更历史 ====================
    
    def get_history(self, key: Optional[str] = None) -> List[ConfigHistoryEntry]:
        """
        获取配置变更历史
        
        Args:
            key: 可选，指定配置键的历史
            
        Returns:
            历史条目列表
        """
        if key:
            return [h for h in self.history if h.path == key]
        return self.history.copy()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history = []
    
    def export_history(self) -> str:
        """导出历史记录为 JSON"""
        return json.dumps(
            [{
                "timestamp": h.timestamp,
                "path": h.path,
                "old_value": str(h.old_value),
                "new_value": str(h.new_value),
                "source": h.source
            } for h in self.history],
            indent=2,
            ensure_ascii=False
        )
    
    # ==================== 监听功能 ====================
    
    def watch(self, callback: Callable[[str, Any], None], 
              path_pattern: Optional[str] = None) -> None:
        """
        注册配置变更回调
        
        Args:
            callback: 回调函数 (key, new_value)
            path_pattern: 匹配的路径模式
        """
        if path_pattern:
            self._change_callbacks.append(ConfigChangeCallback(path_pattern, callback))
        else:
            # 无模式匹配所有变更
            self._change_callbacks.append(ConfigChangeCallback(r".*", callback))
    
    def _trigger_callbacks(self, key: str, value: Any) -> None:
        """触发变更回调"""
        for cb in self._change_callbacks:
            if cb.pattern.match(key):
                try:
                    cb.callback(key, value)
                except Exception:
                    pass
    
    def start_watching(self, interval: float = 1.0) -> None:
        """
        开始监听配置文件变更
        
        Args:
            interval: 检查间隔（秒）
        """
        if self._watchers:
            return
        
        last_hash = self._get_file_hash()
        
        def watcher():
            while True:
                current_hash = self._get_file_hash()
                if current_hash != last_hash:
                    self._load()
                    last_hash = current_hash
                import time
                time.sleep(interval)
        
        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()
        self._watchers.append(thread)
    
    def stop_watching(self) -> None:
        """停止监听"""
        self._watchers.clear()
    
    def _get_file_hash(self) -> str:
        """获取文件哈希"""
        if not self.config_path.exists():
            return ""
        with open(self.config_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    # ==================== 工具方法 ====================
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def export(self, format: str = "json") -> str:
        """
        导出配置为指定格式
        
        Args:
            format: 导出格式 (json/yaml/env)
            
        Returns:
            导出的配置字符串
        """
        if format == "json":
            return json.dumps(self.config_data, indent=2, ensure_ascii=False)
        elif format == "yaml":
            try:
                import yaml
                return yaml.dump(self.config_data, default_flow_style=False, allow_unicode=True)
            except ImportError:
                raise ConfigError("需要安装 pyyaml")
        elif format == "env":
            lines = []
            self._export_env(self.config_data, "", lines)
            return "\n".join(lines)
        else:
            raise ConfigError(f"不支持的格式: {format}")
    
    def _export_env(self, data: Dict, prefix: str, lines: List[str]) -> None:
        """递归导出为 ENV 格式"""
        for key, value in data.items():
            full_key = f"{prefix}_{key}".upper()
            if isinstance(value, dict):
                self._export_env(value, full_key, lines)
            else:
                lines.append(f"{full_key}={value}")
    
    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path}, env={self.env}, format={self.format.value})"


class ConfigBuilder:
    """配置构建器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self._configs: Dict[str, ConfigManager] = {}
        self._default_env = "development"
    
    def add_config(self, name: str, config_path: str, 
                   env: Optional[str] = None, **kwargs) -> 'ConfigBuilder':
        """
        添加配置文件
        
        Args:
            name: 配置名称
            config_path: 配置文件路径
            env: 默认环境
            **kwargs: 其他 ConfigManager 参数
        """
        config = ConfigManager(
            config_path=str(self.base_path / config_path),
            env=env or self._default_env,
            **kwargs
        )
        self._configs[name] = config
        return self
    
    def set_default_env(self, env: str) -> 'ConfigBuilder':
        """设置默认环境"""
        self._default_env = env
        return self
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if config_name not in self._configs:
            raise ConfigError(f"配置不存在: {config_name}")
        return self._configs[config_name].get(key, default)
    
    def set(self, config_name: str, key: str, value: Any, **kwargs) -> None:
        """设置配置值"""
        if config_name not in self._configs:
            raise ConfigError(f"配置不存在: {config_name}")
        self._configs[config_name].set(key, value, **kwargs)
    
    def switch_env(self, env: str) -> None:
        """切换所有配置的环境"""
        for config in self._configs.values():
            config.set_env(env)
    
    def validate_all(self) -> Dict[str, List[ConfigValidationError]]:
        """验证所有配置"""
        results = {}
        for name, config in self._configs.items():
            errors = config.validate()
            if errors:
                results[name] = errors
        return results


# ==================== 使用示例 ====================

def demo():
    """演示配置管理器的使用"""
    print("=" * 60)
    print("智能配置管理器 - 使用演示")
    print("=" * 60)
    
    # 创建示例配置文件
    config_content = {
        "app": {
            "name": "MyApplication",
            "version": "1.0.0",
            "debug": True,
            "log_level": "INFO"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "admin",
            "password": "secret123"
        },
        "redis": {
            "host": "127.0.0.1",
            "port": 6379
        },
        "environments": {
            "development": {
                "database": {
                    "host": "dev-db.example.com",
                    "debug": True
                }
            },
            "production": {
                "database": {
                    "host": "prod-db.example.com",
                    "port": 5432
                }
            }
        }
    }
    
    # 写入示例配置
    config_file = Path("demo_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_content, f, indent=2, ensure_ascii=False)
    
    # 创建配置管理器
    print("\n1. 创建配置管理器")
    config = ConfigManager("demo_config.json", env="development")
    print(f"   {config}")
    
    # 获取配置值
    print("\n2. 获取配置值")
    print(f"   app.name: {config.get('app.name')}")
    print(f"   database.host: {config.get('database.host')}")
    print(f"   database.port: {config.get('database.port', 3306)}")
    
    # 切换环境
    print("\n3. 切换到生产环境")
    config.set_env("production")
    print(f"   database.host: {config.get('database.host')}")
    
    # 设置配置值
    print("\n4. 设置配置值")
    config.set("app.debug", False, source="demo")
    print(f   "app.debug: {config.get('app.debug')}")
    
    # 验证配置
    print("\n5. 验证配置")
    schema = {
        "type": "object",
        "required": ["app", "database"],
        "properties": {
            "app": {
                "type": "object",
                "required": ["name", "version"]
            },
            "database": {
                "type": "object",
                "required": ["host", "port"]
            }
        }
    }
    config.load_schema(schema)
    errors = config.validate()
    if errors:
        print(f"   发现 {len(errors)} 个验证错误")
        for e in errors:
            print(f"   - {e.path}: {e.message}")
    else:
        print("   验证通过！")
    
    # 查看所有配置键
    print("\n6. 查看所有配置键")
    for key in config.keys():
        print(f"   - {key}")
    
    # 查看变更历史
    print("\n7. 查看变更历史")
    for entry in config.get_history():
        print(f"   - {entry.timestamp}: {entry.path} = {entry.new_value}")
    
    # 使用配置构建器
    print("\n8. 使用配置构建器管理多个配置")
    builder = ConfigBuilder()
    builder.add_config("main", "demo_config.json")
    print(f"   app.name: {builder.get('main', 'app.name')}")
    
    # 清理
    print("\n9. 清理演示文件")
    config_file.unlink()
    print("   已删除 demo_config.json")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


def api_example():
    """API 使用示例"""
    print("\nAPI 使用示例:")
    print("-" * 40)
    
    # 从环境变量读取
    import os
    
    # 创建配置
    config = ConfigManager("settings.json", auto_save=False)
    
    # 基础操作
    config.set("app.host", "0.0.0.0")
    config.set("app.port", 8080)
    config.set("app.debug", True)
    
    # 批量设置
    config.merge({
        "database": {
            "host": "localhost",
            "port": 3306
        }
    })
    
    # 获取值
    host = config.get("app.host")
    port = config.get("app.port")
    db_host = config.get("database.host")
    
    print(f"App: {host}:{port}")
    print(f"Database: {db_host}")
    
    # 检查存在性
    if config.has("app.debug"):
        print(f"Debug mode: {config.get('app.debug')}")
    
    # 获取全部配置
    all_config = config.all()
    print(f"All config keys: {len(all_config)}")


if __name__ == "__main__":
    demo()
    api_example()
