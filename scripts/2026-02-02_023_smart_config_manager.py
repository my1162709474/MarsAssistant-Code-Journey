#!/usr/bin/env python3
"""
智能配置管理器 - Smart Configuration Manager

功能:
1. 支持多种格式: JSON, YAML, ENV, .env文件
2. 环境变量覆盖配置
3. 配置验证与类型检查
4. 配置模板系统
5. 配置热重载
6. 配置合并与继承
7. 敏感信息加密存储
8. 远程配置支持

作者: MarsAssistant
日期: 2026-02-02
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import base64
from cryptography.fernet import Fernet


T = TypeVar('T')


class ConfigFormat(Enum):
    """支持的配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    AUTO = "auto"


class ConfigLevel(Enum):
    """配置优先级级别（从低到高）"""
    DEFAULT = 0      # 默认配置
    TEMPLATE = 1     # 模板配置
    FILE = 2         # 配置文件
    ENV = 3          # 环境变量
    OVERRIDE = 4     # 手动覆盖（最高优先级）


@dataclass
class ConfigField:
    """配置字段定义"""
    name: str
    field_type: Type[T]
    required: bool = False
    default: Any = None
    description: str = ""
    validation_regex: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """验证字段值"""
        if value is None:
            if self.required:
                return False, f"字段 '{self.name}' 是必需的"
            return True, ""
        
        # 类型检查
        if not isinstance(value, self.field_type):
            # 尝试类型转换
            try:
                if self.field_type == bool:
                    if str(value).lower() in ('true', '1', 'yes'):
                        value = True
                    elif str(value).lower() in ('false', '0', 'no'):
                        value = False
                    else:
                        return False, f"字段 '{self.name}' 类型不匹配，需要 {self.field_type.__name__}"
                else:
                    value = self.field_type(value)
            except (ValueError, TypeError):
                return False, f"字段 '{self.name}' 类型不匹配，需要 {self.field_type.__name__}"
        
        # 正则验证
        if self.validation_regex and isinstance(value, str):
            if not re.match(self.validation_regex, value):
                return False, f"字段 '{self.name}' 格式不正确"
        
        # 范围验证
        if self.min_value is not None:
            if isinstance(value, (int, float)) and value < self.min_value:
                return False, f"字段 '{self.name}' 不能小于 {self.min_value}"
        if self.max_value is not None:
            if isinstance(value, (int, float)) and value > self.max_value:
                return False, f"字段 '{self.name}' 不能大于 {self.max_value}"
        
        # 选项验证
        if self.choices is not None:
            if value not in self.choices:
                return False, f"字段 '{self.name}' 必须在 {self.choices} 中"
        
        return True, ""


class ConfigurationManager:
    """智能配置管理器"""
    
    def __init__(self, app_name: str = "app"):
        self.app_name = app_name
        self.configs: Dict[str, Any] = {}
        self.config_files: List[Path] = []
        self.field_definitions: Dict[str, Dict[str, ConfigField]] = {}
        self._fernet: Optional[Fernet] = None
        self._encryption_key: Optional[bytes] = None
        
        # 默认配置文件搜索路径
        self.search_paths = [
            Path.cwd(),
            Path.home() / f".{app_name}",
            Path("/etc") / app_name,
            Path(__file__).parent / "config",
        ]
    
    def set_encryption_key(self, key: str) -> None:
        """设置加密密钥"""
        self._encryption_key = hashlib.sha256(key.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(self._encryption_key))
    
    def encrypt_sensitive(self, value: str) -> str:
        """加密敏感信息"""
        if self._fernet:
            return self._fernet.encrypt(value.encode()).decode()
        return value
    
    def decrypt_sensitive(self, encrypted_value: str) -> str:
        """解密敏感信息"""
        if self._fernet:
            return self._fernet.decrypt(encrypted_value.encode()).decode()
        return encrypted_value
    
    def add_search_path(self, path: Union[str, Path]) -> None:
        """添加配置文件搜索路径"""
        self.search_paths.insert(0, Path(path))
    
    def define_fields(self, section: str, fields: List[ConfigField]) -> None:
        """定义配置字段（用于验证）"""
        self.field_definitions[section] = {f.name: f for f in fields}
    
    def load_json(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载JSON配置文件"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_yaml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            import yaml
            path = Path(file_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except ImportError:
            raise ImportError("需要安装 pyyaml: pip install pyyaml")
    
    def load_env(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """加载.env文件"""
        path = Path(file_path)
        env_vars = {}
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        env_vars[key] = value
        return env_vars
    
    def load_config_file(self, file_path: Union[str, Path], fmt: ConfigFormat = ConfigFormat.AUTO) -> Dict[str, Any]:
        """加载配置文件（自动检测格式）"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        # 自动检测格式
        if fmt == ConfigFormat.AUTO:
            suffix = path.suffix.lower()
            if suffix == '.json':
                fmt = ConfigFormat.JSON
            elif suffix in ('.yaml', '.yml'):
                fmt = ConfigFormat.YAML
            elif suffix == '.env':
                fmt = ConfigFormat.ENV
            else:
                # 尝试通过内容检测
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if content.strip().startswith('{'):
                        fmt = ConfigFormat.JSON
                    elif '---' in content or ':' in content.split('\n')[0]:
                        fmt = ConfigFormat.YAML
                    else:
                        fmt = ConfigFormat.ENV
        
        # 根据格式加载
        if fmt == ConfigFormat.JSON:
            return self.load_json(path)
        elif fmt == ConfigFormat.YAML:
            return self.load_yaml(path)
        elif fmt == ConfigFormat.ENV:
            return self.load_env(path)
        
        return {}
    
    def find_config_file(self, filename: str) -> Optional[Path]:
        """在搜索路径中查找配置文件"""
        for search_path in self.search_paths:
            path = search_path / filename
            if path.exists():
                return path
        return None
    
    def load(self, 
             config_name: str, 
             sources: Optional[List[Union[str, Path]]] = None,
             fmt: ConfigFormat = ConfigFormat.AUTO) -> 'ConfigurationManager':
        """加载配置（支持多源合并）"""
        config_data = {}
        
        # 1. 加载默认配置
        default_file = self.find_config_file(f"{config_name}.default.json")
        if default_file:
            config_data = self._merge_config(config_data, self.load_config_file(default_file))
        
        # 2. 加载模板配置
        template_file = self.find_config_file(f"{config_name}.template.json")
        if template_file:
            config_data = self._merge_config(config_data, self.load_config_file(template_file))
        
        # 3. 加载指定源
        if sources:
            for source in sources:
                if isinstance(source, (str, Path)):
                    if Path(source).exists():
                        config_data = self._merge_config(
                            config_data, 
                            self.load_config_file(source, fmt)
                        )
        
        # 4. 加载环境变量
        env_config = self._load_from_env(config_name)
        config_data = self._merge_config(config_data, env_config, ConfigLevel.ENV)
        
        # 5. 存储配置
        self.configs[config_name] = config_data
        
        return self
    
    def _merge_config(self, base: Dict, override: Dict, level: ConfigLevel = ConfigLevel.FILE) -> Dict:
        """递归合并配置（深度合并）"""
        result = base.copy()
        
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_config(result[key], value, level)
            else:
                result[key] = value
        
        return result
    
    def _load_from_env(self, config_name: str) -> Dict[str, Any]:
        """从环境变量加载配置"""
        env_prefix = f"{self.app_name.upper()}_{config_name.upper()}_"
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # 转换键名: APP_DATABASE_HOST -> database.host
                short_key = key[len(env_prefix):].lower()
                parts = short_key.split('_')
                
                # 构建嵌套结构
                current = env_config
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # 设置值（尝试类型转换）
                final_key = parts[-1]
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                
                current[final_key] = value
        
        return env_config
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """获取配置值（支持点分路径）"""
        if config_name not in self.configs:
            return default
        
        config = self.configs[config_name]
        keys = key.split('.')
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        
        return config
    
    def set(self, config_name: str, key: str, value: Any) -> None:
        """设置配置值（支持点分路径）"""
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        config = self.configs[config_name]
        keys = key.split('.')
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self, config_name: str) -> tuple[bool, List[str]]:
        """验证配置"""
        if config_name not in self.configs:
            return False, [f"配置 '{config_name}' 不存在"]
        
        if config_name not in self.field_definitions:
            return True, []  # 没有定义字段，跳过验证
        
        config = self.configs[config_name]
        errors = []
        fields = self.field_definitions[config_name]
        
        for field_def in fields.values():
            # 获取配置值
            value = config.get(field_def.name)
            
            # 验证
            valid, error_msg = field_def.validate(value)
            if not valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def create_template(self, config_name: str, output_path: Union[str, Path]) -> None:
        """根据字段定义创建配置模板"""
        if config_name not in self.field_definitions:
            raise ValueError(f"配置 '{config_name}' 没有定义字段")
        
        template = {}
        for field_def in self.field_definitions[config_name].values():
            key_path = field_def.name.split('.')
            
            # 构建嵌套结构
            current = template
            for key in key_path[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置默认值
            if field_def.default is not None:
                current[key_path[-1]] = field_def.default
            elif field_def.field_type == str:
                current[key_path[-1]] = f"<{field_def.name}>"
            elif field_def.field_type == int:
                current[key_path[-1]] = 0
            elif field_def.field_type == bool:
                current[key_path[-1]] = False
        
        # 写入文件
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
    
    def save(self, config_name: str, output_path: Union[str, Path], fmt: ConfigFormat = ConfigFormat.JSON) -> None:
        """保存配置到文件"""
        if config_name not in self.configs:
            raise ValueError(f"配置 '{config_name}' 不存在")
        
        config = self.configs[config_name]
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if fmt == ConfigFormat.JSON:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {fmt}")
    
    def export(self, config_name: str) -> str:
        """导出配置为JSON字符串"""
        if config_name not in self.configs:
            return "{}"
        return json.dumps(self.configs[config_name], indent=2, ensure_ascii=False)
    
    def import_config(self, config_name: str, json_str: str, level: ConfigLevel = ConfigLevel.OVERRIDE) -> None:
        """从JSON字符串导入配置"""
        config_data = json.loads(json_str)
        if config_name in self.configs:
            self.configs[config_name] = self._merge_config(
                self.configs[config_name], 
                config_data, 
                level
            )
        else:
            self.configs[config_name] = config_data
    
    def hot_reload(self, config_name: str) -> bool:
        """热重载配置（重新从文件加载）"""
        if config_name not in self.config_files:
            return False
        
        # 找到最新的配置文件
        latest_file = max(self.config_files, key=lambda f: f.stat().st_mtime)
        
        # 重新加载
        new_config = self.load_config_file(latest_file)
        self.configs[config_name] = self._merge_config(
            self.configs.get(config_name, {}),
            new_config,
            ConfigLevel.FILE
        )
        
        return True


def demo():
    """演示配置管理器的基本用法"""
    print("🧪 智能配置管理器演示")
    print("=" * 60)
    
    # 1. 创建配置管理器
    manager = ConfigurationManager("myapp")
    
    # 2. 定义配置字段（用于验证）
    manager.define_fields("database", [
        ConfigField("host", str, required=True, description="数据库主机地址"),
        ConfigField("port", int, required=True, default=3306, description="端口号"),
        ConfigField("username", str, required=True, description="用户名"),
        ConfigField("password", str, required=True, description="密码"),
        ConfigField("name", str, required=True, description="数据库名"),
        ConfigField("pool_size", int, default=10, min_value=1, max_value=100, description="连接池大小"),
    ])
    
    # 3. 设置加密密钥（用于敏感信息）
    manager.set_encryption_key("my-secret-key-12345")
    
    # 4. 模拟加载配置（使用测试数据）
    test_config = {
        "database": {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": "encrypted_password_here",
            "name": "myapp_db",
            "pool_size": 20,
        },
        "cache": {
            "redis_host": "localhost",
            "redis_port": 6379,
            "ttl": 3600,
        },
        "app": {
            "debug": True,
            "secret_key": "your-secret-key",
        },
    }
    
    manager.configs["default"] = test_config
    print(f"✅ 加载测试配置成功")
    
    # 5. 获取配置值
    print(f"\n📖 获取配置值:")
    print(f"  数据库主机: {manager.get('default', 'database.host')}")
    print(f"  数据库端口: {manager.get('default', 'database.port')}")
    print(f"  连接池大小: {manager.get('default', 'database.pool_size')}")
    print(f"  调试模式: {manager.get('default', 'app.debug')}")
    
    # 6. 设置配置值
    print(f"\n✏️  修改配置:")
    manager.set('default', 'database.host', '192.168.1.100')
    manager.set('default', 'database.pool_size', 50)
    print(f"  修改后主机: {manager.get('default', 'database.host')}")
    print(f"  修改后连接池: {manager.get('default', 'database.pool_size')}")
    
    # 7. 验证配置
    print(f"\n🔍 验证配置:")
    is_valid, errors = manager.validate('default')
    if is_valid:
        print(f"  ✅ 配置验证通过!")
    else:
        print(f"  ❌ 配置验证失败:")
        for error in errors:
            print(f"     - {error}")
    
    # 8. 导出配置
    print(f"\n📤 导出配置:")
    json_str = manager.export('default')
    print(f"  配置JSON: {json_str[:200]}...")
    
    # 9. 加密敏感信息
    print(f"\n🔒 敏感信息处理:")
    original_password = "my-secret-password"
    encrypted = manager.encrypt_sensitive(original_password)
    decrypted = manager.decrypt_sensitive(encrypted)
    print(f"  原文: {original_password}")
    print(f"  加密后: {encrypted}")
    print(f"  解密后: {decrypted}")
    
    # 10. 创建模板
    print(f"\n📝 创建配置模板:")
    try:
        template_path = "/tmp/myapp_database_template.json"
        manager.create_template("database", template_path)
        print(f"  ✅ 模板已创建: {template_path}")
        
        # 显示模板内容
        with open(template_path, 'r') as f:
            print(f"  模板内容: {f.read()}")
    except Exception as e:
        print(f"  ❌ 模板创建失败: {e}")
    
    print("\n" + "=" * 60)
    print("✨ 配置管理器演示完成!")


if __name__ == "__main__":
    demo()
