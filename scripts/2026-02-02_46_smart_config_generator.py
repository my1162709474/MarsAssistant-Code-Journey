#!/usr/bin/env python3
"""
智能配置生成器 - Smart Config Generator
=========================================
自动生成多种格式的配置文件，支持模板、验证和智能默认值。

支持格式: JSON, YAML, TOML, INI, .env, XML, Properties

功能特点:
- 🎯 多种格式支持
- 📝 模板快速生成
- ✅ 配置验证
- 🧠 智能默认值
- 💻 交互式命令行
- 📖 详细帮助系统
"""

import json
import os
import sys
import base64
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import re


class ConfigGenerator:
    """智能配置生成器核心类"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.validators = self._load_validators()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载内置模板"""
        return {
            "python": {
                "description": "Python项目配置",
                "format": "json",
                "data": {
                    "project_name": "my-project",
                    "version": "1.0.0",
                    "description": "项目描述",
                    "author": "Your Name",
                    "email": "your.email@example.com",
                    "license": "MIT",
                    "python_requires": ">=3.8",
                    "dependencies": [],
                    "dev_dependencies": ["pytest", "black", "flake8"],
                    "entry_point": "src/main.py",
                    "test_dir": "tests/",
                    "src_dir": "src/",
                    "data_dir": "data/",
                    "log_level": "INFO"
                }
            },
            "web": {
                "description": "Web应用配置",
                "format": "json",
                "data": {
                    "app_name": "MyWebApp",
                    "version": "1.0.0",
                    "debug": True,
                    "host": "0.0.0.0",
                    "port": 8080,
                    "secret_key": "your-secret-key-here",
                    "allowed_hosts": ["*"],
                    "database": {
                        "host": "localhost",
                        "port": 5432,
                        "name": "app_db",
                        "user": "postgres",
                        "password": "your-password"
                    },
                    "redis": {
                        "host": "localhost",
                        "port": 6379,
                        "db": 0
                    },
                    "cors_origins": []
                }
            },
            "docker": {
                "description": "Docker Compose配置",
                "format": "yaml",
                "data": {
                    "version": "3.8",
                    "services": {
                        "app": {
                            "image": "python:3.9-slim",
                            "container_name": "my_app",
                            "ports": ["8080:8080"],
                            "volumes": ["./:/app"],
                            "command": "python main.py",
                            "environment": ["PYTHONPATH=/app"]
                        },
                        "redis": {
                            "image": "redis:alpine",
                            "ports": ["6379:6379"]
                        }
                    },
                    "networks": {
                        "default": {
                            "name": "app_network"
                        }
                    }
                }
            },
            "database": {
                "description": "数据库连接配置",
                "format": "env",
                "data": {
                    "DB_TYPE": "postgresql",
                    "DB_HOST": "localhost",
                    "DB_PORT": "5432",
                    "DB_NAME": "mydb",
                    "DB_USER": "postgres",
                    "DB_PASSWORD": "your-password",
                    "DB_POOL_SIZE": "10",
                    "DB_MAX_OVERFLOW": "20"
                }
            },
            "api": {
                "description": "RESTful API配置",
                "format": "yaml",
                "data": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "My API",
                        "version": "1.0.0",
                        "description": "API描述"
                    },
                    "servers": [
                        {"url": "http://localhost:8000", "description": "本地开发"}
                    ],
                    "paths": {},
                    "components": {
                        "schemas": {},
                        "securitySchemes": {
                            "bearerAuth": {
                                "type": "http",
                                "scheme": "bearer"
                            }
                        }
                    }
                }
            },
            "logging": {
                "description": "日志配置",
                "format": "json",
                "data": {
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "standard": {
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                        },
                        "simple": {
                            "format": "%(levelname)s - %(message)s"
                        }
                    },
                    "handlers": {
                        "console": {
                            "class": "logging.StreamHandler",
                            "formatter": "simple"
                        },
                        "file": {
                            "class": "logging.FileHandler",
                            "filename": "logs/app.log",
                            "formatter": "standard"
                        }
                    },
                    "root": {
                        "level": "INFO",
                        "handlers": ["console", "file"]
                    }
                }
            },
            "ml": {
                "description": "机器学习项目配置",
                "format": "yaml",
                "data": {
                    "project": "ml-project",
                    "version": "1.0.0",
                    "data": {
                        "train_path": "data/train.csv",
                        "val_path": "data/val.csv",
                        "test_path": "data/test.csv",
                        "batch_size": 32,
                        "num_workers": 4
                    },
                    "model": {
                        "name": "resnet50",
                        "pretrained": True,
                        "num_classes": 10
                    },
                    "training": {
                        "epochs": 100,
                        "learning_rate": 0.001,
                        "optimizer": "adam",
                        "scheduler": "cosine",
                        "early_stopping_patience": 10
                    },
                    "experiment": {
                        "save_dir": "experiments/",
                        "log_dir": "logs/",
                        "seed": 42
                    }
                }
            }
        }
    
    def _load_validators(self) -> Dict[str, Dict[str, str]]:
        """加载验证规则"""
        return {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "url": r"^https?://[^\s]+$",
            "port": r"^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$",
            "version": r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?(\+[a-zA-Z0-9]+)?$",
            "ip": r"^(\d{1,3}\.){3}\d{1,3}$",
            "boolean": r"^(true|false|True|False|0|1|yes|no)$",
            "integer": r"^-?\d+$",
            "positive_integer": r"^\d+$"
        }
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定模板"""
        return self.templates.get(name)
    
    def generate(self, template_name: str, output_path: str, 
                 overrides: Optional[Dict[str, Any]] = None) -> str:
        """生成配置文件"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"未知模板: {template_name}")
        
        # 深度复制数据
        data = self._deep_copy(template["data"])
        
        # 应用覆盖
        if overrides:
            data = self._apply_overrides(data, overrides)
        
        # 格式化为字符串
        format_type = template["format"]
        content = self._format_content(data, format_type)
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return content
    
    def _deep_copy(self, obj: Any) -> Any:
        """深度复制对象"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def _apply_overrides(self, data: Any, overrides: Dict[str, Any]) -> Any:
        """应用覆盖值"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in overrides:
                    result[key] = overrides[key]
                elif isinstance(value, (dict, list)):
                    result[key] = self._apply_overrides(value, overrides)
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return data
        else:
            return data
    
    def _format_content(self, data: Any, format_type: str) -> str:
        """格式化内容为指定格式"""
        if format_type == "json":
            return self._to_json(data)
        elif format_type == "yaml":
            return self._to_yaml(data)
        elif format_type == "env":
            return self._to_env(data)
        elif format_type == "xml":
            return self._to_xml(data)
        elif format_type == "properties":
            return self._to_properties(data)
        else:
            return str(data)
    
    def _to_json(self, data: Any) -> str:
        """转换为JSON格式"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _to_yaml(self, data: Any) -> str:
        """转换为YAML格式"""
        try:
            import yaml
            return yaml.dump(data, allow_unicode=True, sort_keys=False)
        except ImportError:
            # 如果PyYAML未安装，使用简单格式
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _to_env(self, data: Any, prefix: str = "") -> str:
        """转换为.env格式"""
        lines = []
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}_{key}".upper() if prefix else key.upper()
                if isinstance(value, dict):
                    lines.append(f"# {key}配置")
                    lines.extend(self._to_env(value, full_key).split("\n"))
                elif isinstance(value, list):
                    lines.append(f"{full_key}={','.join(str(v) for v in value)}")
                else:
                    lines.append(f"{full_key}={value}")
        return "\n".join(lines)
    
    def _to_xml(self, data: Any, root_name: str = "config") -> str:
        """转换为XML格式"""
        lines = [f'<?xml version="1.0" encoding="UTF-8"?>', f"<{root_name}>"]
        
        def _add_element(obj: Any, indent: int = 2):
            indent_str = " " * indent
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict):
                        lines.append(f"{indent_str}<{key}>")
                        _add_element(value, indent + 2)
                        lines.append(f"{indent_str}</{key}>")
                    elif isinstance(value, list):
                        for item in value:
                            lines.append(f"{indent_str}<{key}>")
                            _add_element(item, indent + 2)
                            lines.append(f"{indent_str}</{key}>")
                    else:
                        lines.append(f"{indent_str}<{key}>{value}</{key}>")
            elif isinstance(obj, list):
                for item in obj:
                    _add_element(item, indent)
        
        _add_element(data)
        lines.append(f"</{root_name}>")
        return "\n".join(lines)
    
    def _to_properties(self, data: Any, prefix: str = "") -> str:
        """转换为Java Properties格式"""
        lines = []
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    lines.extend(self._to_properties(value, full_key))
                else:
                    lines.append(f"{full_key}={value}")
        return lines
    
    def validate(self, config_data: Dict[str, Any], 
                 rules: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """验证配置数据"""
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated": {}
        }
        
        if not rules:
            rules = self.validators
        
        for key, value in config_data.items():
            if key in rules:
                pattern = rules[key]
                if isinstance(value, str) and not re.match(pattern, str(value)):
                    results["valid"] = False
                    results["errors"].append(f"{key}: 值'{value}'不匹配规则{pattern}")
                else:
                    results["validated"][key] = {"valid": True, "value": value}
            else:
                results["validated"][key] = {"valid": None, "value": value}
        
        return results
    
    def interactive_mode(self):
        """交互式生成模式"""
        print("🎯 智能配置生成器 - 交互模式")
        print("=" * 40)
        
        # 选择模板
        print("\n可用模板:")
        for i, name in enumerate(self.list_templates(), 1):
            template = self.get_template(name)
            print(f"  {i}. {name} - {template['description']}")
        
        choice = input("\n请选择模板编号 (1-{0}): ".format(len(self.templates)))
        try:
            choice = int(choice) - 1
            template_names = list(self.templates.keys())
            template_name = template_names[choice]
        except (ValueError, IndexError):
            template_name = "python"
        
        # 自定义值
        print(f"\n📝 自定义配置 (直接回车使用默认值):")
        template = self.get_template(template_name)
        overrides = {}
        
        def ask_values(obj: Any, prefix: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, dict):
                        print(f"\n📂 {full_key}:")
                        ask_values(value, full_key)
                    elif isinstance(value, list):
                        print(f"  {full_key}: {value}")
                    else:
                        user_input = input(f"  {full_key} [{value}]: ").strip()
                        if user_input:
                            overrides[full_key] = user_input
        
        ask_values(template["data"])
        
        # 生成文件
        output_path = input(f"\n输出路径 [config.{template['format']}]: ").strip()
        if not output_path:
            output_path = f"config.{template['format']}"
        
        # 生成
        content = self.generate(template_name, output_path, overrides)
        print(f"\n✅ 配置已生成: {output_path}")
        print("\n预览:")
        print("-" * 40)
        print(content[:500])
        if len(content) > 500:
            print("... (内容截断)")
        print("-" * 40)


class GitHubSubmitter:
    """GitHub提交器"""
    
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.api_base = "https://api.github.com"
    
    def submit_file(self, file_path: str, content: str, 
                    message: str, branch: str = "main") -> Dict:
        """提交文件到GitHub"""
        import requests
        
        url = f"{self.api_base}/repos/{self.repo}/contents/{file_path}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # 检查文件是否存在
        response = requests.get(url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get("sha")
        
        # 编码内容
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        # 提交数据
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        if sha:
            data["sha"] = sha
        
        # 发送请求
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    
    def update_readme(self, readme_path: str, new_entry: str,
                      message: str) -> Dict:
        """更新README.md"""
        import requests
        
        # 获取当前README内容
        url = f"{self.api_base}/repos/{self.repo}/contents/{readme_path}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"success": False, "error": "无法获取README文件"}
        
        sha = response.json().get("sha")
        current_content = base64.b64decode(
            response.json().get("content", "")
        ).decode("utf-8")
        
        # 在指定位置插入新条目（今日提交部分后）
        lines = current_content.split("\n")
        new_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # 在第一个标题后插入
            if not inserted and line.startswith("## "):
                new_lines.append("")
                new_lines.append(new_entry)
                new_lines.append("")
                inserted = True
        
        if not inserted:
            new_lines.append(new_entry)
        
        updated_content = "\n".join(new_lines)
        encoded_content = base64.b64encode(
            updated_content.encode("utf-8")
        ).decode("utf-8")
        
        # 提交更新
        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha
        }
        
        response = requests.put(url, json=data, headers=headers)
        return {"success": response.status_code in [200, 201], "data": response.json()}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能配置生成器 - 生成多种格式的配置文件"
    )
    parser.add_argument(
        "-t", "--template", 
        choices=["python", "web", "docker", "database", "api", "logging", "ml"],
        default="python",
        help="选择配置模板"
    )
    parser.add_argument(
        "-o", "--output",
        default="config.json",
        help="输出文件路径"
    )
    parser.add_argument(
        "-k", "--key",
        action="append",
        help="覆盖配置值，格式: key=value"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="列出所有可用模板"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="启动交互式模式"
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "env", "xml", "properties"],
        help="指定输出格式"
    )
    
    args = parser.parse_args()
    
    generator = ConfigGenerator()
    
    # 交互模式
    if args.interactive:
        generator.interactive_mode()
        return
    
    # 列出模板
    if args.list:
        print("可用模板:")
        for name in generator.list_templates():
            template = generator.get_template(name)
            print(f"  • {name}: {template['description']}")
        return
    
    # 处理覆盖值
    overrides = {}
    if args.key:
        for kv in args.key:
            if "=" in kv:
                key, value = kv.split("=", 1)
                overrides[key] = value
    
    # 生成配置
    try:
        content = generator.generate(args.template, args.output, overrides)
        print(f"✅ 配置文件已生成: {args.output}")
        print("\n内容预览:")
        print("-" * 40)
        print(content[:300])
        if len(content) > 300:
            print("... (更多内容)")
        print("-" * 40)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
