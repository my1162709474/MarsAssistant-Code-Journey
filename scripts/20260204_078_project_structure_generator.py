#!/usr/bin/env python3
"""
Project Structure Generator
自动生成项目目录结构和初始化文件
支持 15+ 编程语言和框架
"""

import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class ProjectStructureGenerator:
    """项目结构生成器"""
    
    # 支持的项目模板
    TEMPLATES = {
        "python": {
            "name": "Python Package",
            "dirs": ["src/{project_name}", "tests", "docs"],
            "files": {
                "src/{project_name}/__init__.py": "# {project_name} package",
                "src/{project_name}/main.py": "# Main module",
                "tests/__init__.py": "# Tests package",
                "tests/test_main.py": "import unittest\nfrom {project_name} import main\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n",
                "docs/README.md": "# {project_name} Documentation",
                "requirements.txt": "# Dependencies\n",
                "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name="{project_name}",\n    version="0.1.0",\n    packages=find_packages(),\n    install_requires=[],\n)",
                ".gitignore": "__pycache__/\n*.pyc\n*.egg-info/\ndist/\nbuild/",
            }
        },
        "javascript": {
            "name": "Node.js Project",
            "dirs": ["src", "tests", "docs"],
            "files": {
                "src/index.js": "// Entry point\nconsole.log('Hello, World!');\n",
                "package.json": "{\n  \"name\": \"{project_name}\",\n  \"version\": \"1.0.0\",\n  \"main\": \"src/index.js\",\n  \"scripts\": {\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {},\n  \"devDependencies\": {}\n}",
                ".gitignore": "node_modules/\nnpm-debug.log\ndist/",
            }
        },
        "react": {
            "name": "React Project",
            "dirs": ["src/components", "src/hooks", "src/utils", "public"],
            "files": {
                "src/App.jsx": "import React from 'react';\n\nfunction App() {\n  return <div>Hello, React!</div>;\n}\nexport default App;\n",
                "package.json": "{\n  \"name\": \"{project_name}\",\n  \"version\": \"1.0.0\",\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"vite build\"\n  }\n}",
                ".gitignore": "node_modules/\ndist/",
            }
        },
        "fastapi": {
            "name": "FastAPI Project",
            "dirs": ["app/api", "app/models", "app/schemas", "app/db", "tests"],
            "files": {
                "app/__init__.py": "# FastAPI application\n",
                "app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\nasync def root():\n    return {{"message": "Hello, World!"}}\n",
                "requirements.txt": "fastapi\nuvicorn[standard]\npydantic\n",
                ".gitignore": "__pycache__/\n*.pyc\n",
            }
        },
        "go": {
            "name": "Go Module",
            "dirs": ["cmd", "internal", "pkg", "tests"],
            "files": {
                "cmd/main.go": "package main\n\nfunc main() {\n    println("Hello, World!")\n}\n",
                "go.mod": "module {project_name}\n\ngo 1.21\n",
                ".gitignore": "*.exe\n*.test\n*.out\n",
            }
        },
        "rust": {
            "name": "Rust Project",
            "dirs": ["src", "tests", "benches"],
            "files": {
                "src/main.rs": "fn main() {\n    println!("Hello, World!");\n}\n",
                "Cargo.toml": "[package]\nname = \"{project_name}\"\nversion = \"0.1.0\"\nedition = "2021"\n\n[dependencies]",
                ".gitignore": "target/\n*.exe\n",
            }
        },
        "java": {
            "name": "Java Project",
            "dirs": ["src/main/java/{package_path}", "src/test/java/{package_path}", "docs"],
            "files": {
                "src/main/java/{package_path}/Main.java": "package {package_name};\n\npublic class Main {{ public static void main(String[] args) {{ System.out.println(\"Hello, World!\"); }}}}",
                "pom.xml": "<?xml version=\"1.0\"?>\n<project>\n  <modelVersion>4.0.0</modelVersion>\n  <groupId>{package_name}</groupId>\n  <artifactId>{project_name}</artifactId>\n  <version>1.0.0</version>\n</project>",
                ".gitignore": "target/\n*.class\n",
            }
        },
        "cpp": {
            "name": "C++ Project",
            "dirs": ["include", "src", "lib", "tests", "build"],
            "files": {
                "src/main.cpp": "#include <iostream>\n\nint main() {{ std::cout << \"Hello, World!\" << std::endl; return 0; }}\n",
                "CMakeLists.txt": "cmake_minimum_required(VERSION 3.10)\nproject({project_name})\n\nset(CMAKE_CXX_STANDARD 17)\nadd_executable(app src/main.cpp)\n",
                ".gitignore": "build/\n*.o\n*.exe\n",
            }
        },
        "csharp": {
            "name": "C# Project",
            "dirs": ["src", "tests", "docs"],
            "files": {
                "src/Program.cs": "using System;\n\nclass Program {{ static void Main() {{ Console.WriteLine(\"Hello, World!\"); }}}}",
                "{project_name}.csproj": "<Project Sdk=\"Microsoft.NET.Sdk\">\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net8.0</TargetFramework>\n  </PropertyGroup>\n</Project>",
                ".gitignore": "bin/\nobj/\n*.user\n",
            }
        },
        "docker": {
            "name": "Docker Project",
            "dirs": ["app", "docker"],
            "files": {
                "Dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"app/main.py\"]\n",
                "docker-compose.yml": "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - \"8000:8000\"\n",
                ".dockerignore": "venv/\n__pycache__/\n*.pyc\n",
            }
        },
        "fullstack": {
            "name": "Full Stack Project",
            "dirs": ["frontend", "backend", "shared", "docker"],
            "files": {
                "README.md": "# {project_name}\n\nFull Stack Application\n\n## Structure\n- frontend/: React/Vue application\n- backend/: API server\n- shared/: Shared types and utilities\n",
                "docker-compose.yml": "version: '3.8'\nservices:\n  frontend:\n    build: ./frontend\n    ports:\n      - \"3000:3000\"\n  backend:\n    build: ./backend\n    ports:\n      - \"8080:8080\"\n",
            }
        },
        "ml": {
            "name": "Machine Learning Project",
            "dirs": ["data", "models", "notebooks", "src", "tests"],
            "files": {
                "src/train.py": "import numpy as np\n\ndef train_model():\n    print(\"Training model...\")\n    return None\n\nif __name__ == \"__main__\":\n    train_model()\n",
                "requirements.txt": "numpy\npandas\nscikit-learn\ntorch\ntensorflow\n",
                ".gitignore": "data/raw/\nmodels/*.h5\n*.pth\n__pycache__/",
            }
        },
        "api": {
            "name": "REST API Project",
            "dirs": ["routes", "controllers", "models", "middleware", "utils", "tests"],
            "files": {
                "app.js": "const express = require('express');\nconst app = express();\n\napp.use(express.json());\n\napp.get('/api/health', (req, res) => {{\n  res.json({{ status: 'ok' }});\n}});\n\nmodule.exports = app;\n",
                "package.json": "{\n  \"name\": \"{project_name}-api\",\n  \"version\": \"1.0.0\",\n  \"main\": \"app.js\"\n}",
                ".env.example": "PORT=3000\nDATABASE_URL=\nAPI_KEY=\n",
            }
        },
        "cli": {
            "name": "CLI Tool",
            "dirs": ["src", "commands", "utils"],
            "files": {
                "src/cli.py": "#!/usr/bin/env python3\nimport argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description='CLI Tool')\n    parser.add_argument('--name', default='World', help='Name to greet')\n    args = parser.parse_args()\n    print(f'Hello, {{args.name}}!')\n\nif __name__ == '__main__':\n    main()\n",
                "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name="{project_name}",\n    version="0.1.0",\n    py_modules=['src.cli'],\n    entry_points={{\n        'console_scripts': [\n            '{project_name}=src.cli:main',\n        ],\n    }},\n)",
                "requirements.txt": "argparse-logging\n",
            }
        },
        "library": {
            "name": "Reusable Library",
            "dirs": ["src", "docs", "examples", "tests"],
            "files": {
                "src/__init__.py": "# {project_name}\n\n__version__ = '0.1.0'\n",
                "src/core.py": "class Core:\n    \"\"\"Core functionality.\"\"\"\n    pass\n",
                "examples/usage.py": "from {project_name} import Core\n\nc = Core()\nprint('Library loaded!')",
                "README.md": "# {project_name}\n\nA reusable library.\n\n## Install\npip install {project_name}\n\n## Usage\n```python\nfrom {project_name} import Core\nc = Core()\n```\n",
            }
        },
    }
    
    def __init__(self):
        self.created_files = []
    
    def generate(self, project_name: str, template: str = "python", 
                 package_name: Optional[str] = None) -> List[str]:
        """生成项目结构"""
        if template not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template}. Available: {list(self.TEMPLATES.keys())}")
        
        template_config = self.TEMPLATES[template]
        package_name = package_name or project_name.lower().replace("-", "_")
        package_path = package_name.replace(".", "/")
        
        for directory in template_config["dirs"]:
            dir_path = Path(directory.format(
                project_name=project_name,
                package_name=package_name,
                package_path=package_path
            ))
            dir_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        for file_path, content in template_config["files"].items():
            full_path = Path(file_path.format(
                project_name=project_name,
                package_name=package_name,
                package_path=package_path
            ))
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            formatted_content = content.format(
                project_name=project_name,
                package_name=package_name,
                package_path=package_path
            )
            
            full_path.write_text(formatted_content)
            files_created.append(str(full_path))
        
        self.created_files = files_created
        return files_created
    
    def get_available_templates(self) -> Dict[str, str]:
        """获取可用的项目模板"""
        return {name: config["name"] for name, config in self.TEMPLATES.items()}


def main():
    parser = argparse.ArgumentParser(
        description="Project Structure Generator - 自动生成项目结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python project_generator.py my-python-app python
  python project_generator.py my-react-app react
  python project_generator.py my-api api
  python project_generator.py --list-templates
        """
    )
    
    parser.add_argument("project_name", nargs="?", help="项目名称")
    parser.add_argument("template", nargs="?", default="python", help="项目模板")
    parser.add_argument("--package", "-p", help="包名 (Java/Go)")
    parser.add_argument("--list-templates", "-l", action="store_true", 
                        help="列出所有可用的模板")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览但不创建文件")
    
    args = parser.parse_args()
    
    generator = ProjectStructureGenerator()
    
    if args.list_templates:
        templates = generator.get_available_templates()
        print("\nAvailable Templates:\n")
        for name, desc in templates.items():
            print(f"  {name:15} - {desc}")
        return
    
    if not args.project_name:
        parser.print_help()
        print("\nError: Project name is required (or use --list-templates)")
        return
    
    if args.dry_run:
        print(f"Dry run - would create project '{args.project_name}' with template '{args.template}'")
        return
    
    try:
        files = generator.generate(args.project_name, args.template, args.package)
        print(f"\n✅ Project '{args.project_name}' created successfully!\n")
        print("Created files:")
        for f in files:
            print(f"  📄 {f}")
        print("\nNext steps:")
        print(f"  cd {args.project_name}")
        print("  git init")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
