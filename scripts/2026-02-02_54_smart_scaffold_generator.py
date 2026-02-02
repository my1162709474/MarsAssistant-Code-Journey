#!/usr/bin/env python3
"""
智能项目脚手架生成器
Smart Project Scaffold Generator

根据模板快速生成项目结构，支持多种编程语言和框架。

功能特性:
- 🎯 多语言支持: Python/JavaScript/Go/Rust/Java/C++
- 🏗️ 多种框架模板: Flask/Django/React/Vue/FastAPI/ Gin/Spring Boot
- 📁 标准项目结构: 符合行业最佳实践
- ⚡ 快速生成: 一键创建完整项目骨架
- 🔧 自定义配置: 灵活调整项目参数

使用方式:
    python smart_scaffold_generator.py my_project --type python --framework flask --author "Mars"
    python smart_scaffold_generator.py web_app --type js --framework react
    python smart_scaffold_generator.py api_service --type go --framework gin
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ScaffoldGenerator:
    """智能项目脚手架生成器"""
    
    # 项目模板定义
    TEMPLATES = {
        'python': {
            'flask': {
                'name': 'Flask Web 应用',
                'structure': {
                    '{{project_name}}/': {
                        'app/': {
                            '__init__.py': '''"""应用包初始化"""
from flask import Flask

def create_app(config_class=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    if config_class:
        app.config.from_object(config_class)
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
''',
                            'routes/': {
                                '__init__.py': '"""路由模块"""',
                                'main.py': '''"""主路由"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/health')
def health():
    return {'status': 'healthy'}
'''
                            },
                            'models/': {
                                '__init__.py': '"""数据模型"""'
                            },
                            'templates/': {
                                'base.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}默认标题{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>''',
                                'index.html': '''{% extends "base.html" %}
{% block title %}首页{% endblock %}
{% block content %}
<h1>欢迎使用 Flask 应用!</h1>
{% endblock %}'''
                            },
                            'static/': {
                                'style.css': '''/* 样式文件 */
body {
    font-family: Arial, sans-serif;
    margin: 20px;
}'''
                            }
                        },
                        'tests/': {
                            '__init__.py': '',
                            'test_main.py': '''"""主路由测试"""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200

def test_health(client):
    """测试健康检查"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
'''
                        },
                        'requirements.txt': '''flask==3.0.0
pytest==7.4.0
flask-sqlalchemy==3.1.0
''',
                        'config.py': '''"""配置文件"""
import os


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
'''
                    }
                }
            },
            'django': {
                'name': 'Django Web 应用',
                'structure': {
                    '{{project_name}}/': {
                        '{{project_name}}/': {
                            '__init__.py': '',
                            'settings.py': '''"""Django 设置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{{project_name}}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '{{project_name}}.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
''',
                            'urls.py': '''"""URL 配置"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]''',
                            'wsgi.py': '''"""WSGI 配置"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{project_name}}.settings')
application = get_wsgi_application()
'''
                        },
                        'apps/': {
                            '__init__.py': ''
                        },
                        'templates/': {
                            'base.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Django 应用{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>'''
                        },
                        'manage.py': '''#!/usr/bin/env python
"""Django 管理的命令行入口"""
import os
import sys


def main():
    """运行管理命令"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{project_name}}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''
                    }
                }
            },
            'fastapi': {
                'name': 'FastAPI Web 应用',
                'structure': {
                    '{{project_name}}/': {
                        'app/': {
                            '__init__.py': '''"""FastAPI 应用"""
from fastapi import FastAPI
from app.routers import users, items

app = FastAPI(title="{{project_name}}", version="1.0.0")

# 注册路由
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
''',
                            'routers/': {
                                '__init__.py': '"""路由模块"""',
                                'users.py': '''"""用户路由"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_users():
    return [{"id": 1, "name": "用户1"}, {"id": 2, "name": "用户2"}]


@router.get("/{user_id}")
def read_user(user_id: int):
    return {"id": user_id, "name": f"用户{user_id}"}
''',
                                'items.py': '''"""物品路由"""
from fastapi import APIRouter
from pydantic import BaseItem

router = APIRouter()
items_db = {}


@router.get("/")
def read_items():
    return list(items_db.values())


@router.post("/")
def create_item(item: BaseItem):
    items_db[item.id] = item
    return item
'''
                            },
                            'models/': {
                                '__init__.py': '"""数据模型"""',
                                'schemas.py': '''"""Pydantic 模型"""
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    description: str | None = None


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
'''
                            },
                            'database.py': '''"""数据库连接"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./{{project_name}}.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
'''
                        },
                        'requirements.txt': '''fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.0
pydantic==2.5.0
''',
                        'main.py': '''"""应用入口"""
import uvicorn
from app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
                    }
                }
            }
        },
        'javascript': {
            'react': {
                'name': 'React 前端应用',
                'structure': {
                    '{{project_name}}/': {
                        'public/': {
                            'index.html': '''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{project_name}}</title>
  </head>
  <body>
    <noscript>需要启用 JavaScript</noscript>
    <div id="root"></div>
  </body>
</html>''',
                            'favicon.ico': ''
                        },
                        'src/': {
                            'App.js': '''"""主应用组件"""
import React, { useState } from 'react';
import './App.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <header className="App-header">
        <h1>{{project_name}}</h1>
        <p>
          Learn React
        </p>
        <button onClick={() => setCount(count + 1)}>
          点击次数: {count}
        </button>
      </header>
    </div>
  );
}

export default App;
''',
                            'App.css': '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
''',
                            'index.js': '''"""入口文件"""
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
                        },
                        'package.json': '''{
  "name": "{{project_name}}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}'''
                    }
                }
            },
            'vue': {
                'name': 'Vue 3 前端应用',
                'structure': {
                    '{{project_name}}/': {
                        'public/': {
                            'index.html': '''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{project_name}}</title>
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>'''
                        },
                        'src/': {
                            'App.vue': '''<template>
  <div id="app">
    <h1>{{project_name}}</h1>
    <p>Vue 3 应用</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const msg = ref('Hello Vue!')
</script>

<style>
#app {
  text-align: center;
  margin-top: 60px;
}
</style>
''',
                            'main.js': '''import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
'''
                        },
                        'package.json': '''{
  "name": "{{project_name}}",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}''',
                        'vite.config.js': '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000
  }
})
'''
                    }
                }
            }
        },
        'go': {
            'gin': {
                'name': 'Gin Web 服务',
                'structure': {
                    '{{project_name}}/': {
                        'main.go': '''package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "Welcome to Gin!",
        })
    })
    
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "status": "healthy",
        })
    })
    
    r.Run(":8080")
}
''',
                        'go.mod': '''module {{project_name}}

go 1.21

require github.com/gin-gonic/gin v1.9.1
''',
                        'handlers/': {
                            'handlers.go': '''package handlers

import (
    "github.com/gin-gonic/gin"
)

// HealthHandler 健康检查
func HealthHandler(c *gin.Context) {
    c.JSON(200, gin.H{
        "status": "healthy",
    })
}

// APIHandler API 处理器
func APIHandler(c *gin.Context) {
    id := c.Param("id")
    c.JSON(200, gin.H{
        "id":      id,
        "message": "API Response",
    })
}
'''
                    }
                }
            }
        },
        'rust': {
            'actix': {
                'name': 'Actix Web 服务',
                'structure': {
                    '{{project_name}}/': {
                        'Cargo.toml': '''[package]
name = "{{project_name}}"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = "1"
''',
                        'src/': {
                            'main.rs': '''use actix_web::{get, App, HttpResponse, HttpServer, Responder};

#[get("/")]
async fn index() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "message": "Welcome to Actix!"
    }))
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy"
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(index)
            .service(health)
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
'''
                    }
                }
            }
        }
    }
    
    def __init__(self, project_name: str, project_type: str = 'python', 
                 framework: str = 'flask', author: str = 'Mars'):
        self.project_name = project_name
        self.project_type = project_type
        self.framework = framework
        self.author = author
        self.template = self._get_template()
        
    def _get_template(self) -> dict:
        """获取项目模板"""
        type_templates = self.TEMPLATES.get(self.project_type, {})
        return type_templates.get(self.framework, {})
    
    def _replace_vars(self, content: str) -> str:
        """替换模板变量"""
        replacements = {
            '{{project_name}}': self.project_name,
            '{{author}}': self.author,
            '{{date}}': datetime.now().strftime('%Y-%m-%d')
        }
        result = content
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    
    def _create_structure(self, structure: dict, base_path: Path) -> list:
        """递归创建目录结构"""
        created_files = []
        
        for name, content in structure.items():
            path = base_path / self._replace_vars(name)
            
            if isinstance(content, dict):
                # 目录
                path.mkdir(parents=True, exist_ok=True)
                created_files.extend(self._create_structure(content, path))
            else:
                # 文件
                path.parent.mkdir(parents=True, exist_ok=True)
                final_content = self._replace_vars(content)
                path.write_text(final_content)
               (path))
        
        created_files.append(str return created_files
    
    def generate(self, output_dir: str = '.') -> list:
        """生成项目脚手架"""
        if not self.template:
            print(f"❌ 不支持的类型组合: {self.project_type}/{self.framework}")
            print(f"   支持的类型: {', '.join(self.TEMPLATES.keys())}")
            return []
        
        output_path = Path(output_dir) / self.project_name
        
        print(f"🚀 正在生成项目: {self.project_name}")
        print(f"   类型: {self.project_type}/{self.framework}")
        print(f"   输出目录: {output_path}")
        
        created_files = self._create_structure(self.template['structure'], output_path)
        
        print(f"✅ 项目创建成功! 共创建 {len(created_files)} 个文件")
        for f in created_files[:5]:
            print(f"   - {f}")
        if len(created_files) > 5:
            print(f"   ... 还有 {len(created_files) - 5} 个文件")
        
        return created_files
    
    def get_supported_types(self) -> dict:
        """获取支持的类型列表"""
        result = {}
        for lang, frameworks in self.TEMPLATES.items():
            result[lang] = list(frameworks.keys())
        return result


def list_templates():
    """列出所有可用模板"""
    generator = ScaffoldGenerator('demo')
    templates = generator.get_supported_types()
    
    print("📦 支持的项目模板:")
    print()
    
    for lang, frameworks in templates.items():
        lang_names = {
            'python': '🐍 Python',
            'javascript': '🟨 JavaScript',
            'go': '🐹 Go',
            'rust': '🦀 Rust'
        }
        
        print(f"{lang_names.get(lang, lang)}:")
        
        for fw in frameworks:
            template = generator.TEMPLATES[lang][fw]
            print(f"   • {fw:12} - {template['name']}")
        print()


def demo():
    """运行演示"""
    print("=" * 60)
    print("🎯 智能项目脚手架生成器 - 演示")
    print("=" * 60)
    print()
    
    # 列出模板
    list_templates()
    
    # 创建示例项目
    print("📝 创建示例项目...")
    print()
    
    generator = ScaffoldGenerator(
        project_name='demo_api',
        project_type='python',
        framework='fastapi',
        author='Demo'
    )
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        files = generator.generate(output_dir=tmpdir)
        
        print()
        print("📂 项目结构:")
        for f in sorted(files):
            depth = f.count('/') - 2
            indent = '  ' * depth
            print(f"{indent}📄 {f.split('/')[-1]}")
    
    print()
    print("✅ 演示完成!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='智能项目脚手架生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s my_project --type python --framework flask
  %(prog)s web_app --type js --framework react
  %(prog)s api_service --type go --framework gin
  %(prog)s --list  # 列出所有模板
  %(prog)s --demo  # 运行演示
        """
    )
    
    parser.add_argument('project_name', nargs='?', help='项目名称')
    parser.add_argument('--type', '-t', choices=['python', 'javascript', 'go', 'rust'],
                        default='python', help='项目类型')
    parser.add_argument('--framework', '-f', 
                        choices=['flask', 'django', 'fastapi', 'react', 'vue', 'gin', 'actix'],
                        default='flask', help='框架类型')
    parser.add_argument('--author', '-a', default='Mars', help='作者名称')
    parser.add_argument('--output', '-o', default='.', help='输出目录')
    parser.add_argument('--list', action='store_true', help='列出所有模板')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    if args.list:
        list_templates()
    elif args.demo:
        demo()
    elif args.project_name:
        generator = ScaffoldGenerator(
            project_name=args.project_name,
            project_type=args.type,
            framework=args.framework,
            author=args.author
        )
        generator.generate(output_dir=args.output)
    else:
        parser.print_help()
