#!/usr/bin/env python3
"""
API Documentation Generator
==========================
Auto-generate documentation from code comments and function signatures.

Usage:
    python3 api_doc_generator.py <source_file> [--output OUTPUT] [--format FORMAT]

Supported formats: markdown, html, json

Author: AI Code Journey
Date: 2026-02-03
"""

import ast
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    signature: str
    docstring: str
    args: List[Dict[str, str]]
    returns: Optional[Dict[str, str]]
    decorators: List[str]
    line_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "signature": self.signature,
            "docstring": self.docstring,
            "args": self.args,
            "returns": self.returns,
            "decorators": self.decorators,
            "line_number": self.line_number
        }


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    docstring: str
    methods: List[FunctionDoc]
    attributes: List[Dict[str, str]]
    bases: List[str]
    line_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "methods": [m.to_dict() for m in self.methods],
            "attributes": self.attributes,
            "bases": self.bases,
            "line_number": self.line_number
        }


class APIDocumentationGenerator:
    """Generate API documentation from Python source code."""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.classes: List[ClassDoc] = []
        self.functions: List[FunctionDoc] = []
    
    def extract_docstring(self, node: ast.AST) -> str:
        """Extract docstring from a node."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant):
                    return child.value.s
        return ""
    
    def parse_type_annotation(self, annotation: ast.AST) -> str:
        """Parse a type annotation to string."""
        if annotation is None:
            return "Any"
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{self.parse_type_annotation(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            base = self.parse_type_annotation(annotation.value)
            if isinstance(annotation.slice, ast.Tuple):
                args = ", ".join(self.parse_type_annotation(a) for a in annotation.slice.elts)
                return f"{base}[{args}]"
            else:
                return f"{base}[{self.parse_type_annotation(annotation.slice)}]"
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.BinOp):
            return "Any"  # Simplified
        else:
            return "Any"
    
    def parse_args_from_signature(self, node: ast.FunctionDef) -> List[Dict[str, str]]:
        """Extract function arguments with types."""
        args_info = []
        
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "type": "Any",
                "default": ""
            }
            
            # Find type annotation
            for annotation in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                if annotation.arg == arg.arg and annotation.annotation:
                    arg_info["type"] = self.parse_type_annotation(annotation.annotation)
                    break
            
            # Find default value
            defaults = node.args.defaults + node.args.kw_defaults
            for i, default_arg in enumerate(node.args.args[-(len(defaults) or 1):]):
                if default_arg.arg == arg.arg and defaults:
                    try:
                        default = defaults[-(len(node.args.args) - i)]
                        if default:
                            arg_info["default"] = ast.unparse(default)
                    except:
                        pass
            
            args_info.append(arg_info)
        
        return args_info
    
    def parse_returns(self, node: ast.FunctionDef) -> Optional[Dict[str, str]]:
        """Extract return type annotation."""
        if node.returns:
            return {
                "type": self.parse_type_annotation(node.returns),
                "description": ""
            }
        return None
    
    def extract_decorators(self, node: ast.FunctionDef) -> List[str]:
        """Extract decorator names."""
        return [d.id if isinstance(d, ast.Name) else ast.unparse(d) for d in node.decorator_list]
    
    def generate_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate a readable function signature."""
        args = []
        for arg in node.args.args:
            arg_type = "Any"
            if arg.annotation:
                arg_type = self.parse_type_annotation(arg.annotation)
            args.append(f"{arg.arg}: {arg_type}")
        
        args_str = ", ".join(args)
        
        if node.returns:
            ret_type = self.parse_type_annotation(node.returns)
            return f"def {node.name}({args_str}) -> {ret_type}"
        return f"def {node.name}({args_str})"
    
    def visit_class(self, node: ast.ClassDef):
        """Visit and document a class."""
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("_"):
                if item.name == "__init__":
                    # Extract __init__ attributes
                    for arg in item.args.args:
                        if arg.arg != "self":
                            attr_info = {
                                "name": arg.arg,
                                "type": "Any",
                                "docstring": ""
                            }
                            if arg.annotation:
                                attr_info["type"] = self.parse_type_annotation(arg.annotation)
                            attributes.append(attr_info)
            
            if isinstance(item, ast.FunctionDef):
                func_doc = self._create_function_doc(item)
                if func_doc:
                    methods.append(func_doc)
        
        class_doc = ClassDoc(
            name=node.name,
            docstring=self.extract_docstring(node),
            methods=methods,
            attributes=attributes,
            bases=[self.parse_type_annotation(base) for base in node.bases],
            line_number=node.lineno
        )
        self.classes.append(class_doc)
    
    def visit_function(self, node: ast.FunctionDef):
        """Visit and document a function."""
        func_doc = self._create_function_doc(node)
        if func_doc:
            self.functions.append(func_doc)
    
    def _create_function_doc(self, node: ast.FunctionDef) -> Optional[FunctionDoc]:
        """Create a FunctionDoc from a FunctionDef node."""
        return FunctionDoc(
            name=node.name,
            signature=self.generate_function_signature(node),
            docstring=self.extract_docstring(node),
            args=self.parse_args_from_signature(node),
            returns=self.parse_returns(node),
            decorators=self.extract_decorators(node),
            line_number=node.lineno
        )
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the source code and generate documentation."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.visit_class(node)
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions
                if isinstance(node.parent, ast.Module):
                    self.visit_function(node)
        
        return {
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
            "summary": {
                "total_classes": len(self.classes),
                "total_functions": len(self.functions),
                "total_methods": sum(len(c.methods) for c in self.classes)
            }
        }
    
    def generate_markdown(self, title: str = "API Documentation") -> str:
        """Generate markdown documentation."""
        self.analyze()
        
        md = []
        md.append(f"# {title}\n")
        md.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        md.append("## Summary\n")
        md.append(f"- **Classes**: {len(self.classes)}")
        md.append(f"- **Functions**: {len(self.functions)}")
        md.append(f"- **Methods**: {sum(len(c.methods) for c in self.classes)}\n\n")
        
        if self.classes:
            md.append("## Classes\n\n")
            for cls in self.classes:
                md.append(f"### `{cls.name}`\n")
                if cls.bases:
                    md.append(f"*Inherits from: {', '.join(cls.bases)}*\n\n")
                if cls.docstring:
                    md.append(f"{cls.docstring}\n\n")
                
                if cls.attributes:
                    md.append("**Attributes:**\n")
                    for attr in cls.attributes:
                        md.append(f"- `{attr['name']}`: {attr['type']}\n")
                    md.append("\n")
                
                if cls.methods:
                    md.append("**Methods:**\n")
                    for method in cls.methods:
                        md.append(f"- `{method.name}`: {method.signature}\n")
                    md.append("\n")
                
                md.append("---\n\n")
        
        if self.functions:
            md.append("## Functions\n\n")
            for func in self.functions:
                md.append(f"### `{func.name}`\n")
                md.append(f"```python\n{func.signature}\n```\n\n")
                if func.docstring:
                    md.append(f"{func.docstring}\n\n")
                
                if func.args:
                    md.append("**Parameters:**\n")
                    for arg in func.args:
                        default_str = f" = `{arg['default']}`" if arg['default'] else ""
                        md.append(f"- `{arg['name']}`: {arg['type']}{default_str}\n")
                    md.append("\n")
                
                if func.returns:
                    md.append(f"**Returns**: `{returns['type']}`\n\n")
                
                md.append("---\n\n")
        
        return "".join(md)
    
    def generate_json(self, title: str = "API Documentation") -> str:
        """Generate JSON documentation."""
        data = self.analyze()
        data["title"] = title
        data["generated_at"] = datetime.now().isoformat()
        return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate API documentation from Python source code"
    )
    parser.add_argument("source_file", help="Python source file to analyze")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument("--title", default="API Documentation", help="Document title")
    
    args = parser.parse_args()
    
    # Read source file
    source_path = Path(args.source_file)
    if not source_path.exists():
        print(f"Error: File '{source_path}' not found")
        return 1
    
    source_code = source_path.read_text()
    
    # Generate documentation
    generator = APIDocumentationGenerator(source_code)
    
    if args.format == "markdown":
        output = generator.generate_markdown(args.title)
    elif args.format == "json":
        output = generator.generate_json(args.title)
    elif args.format == "html":
        # Simple HTML conversion
        md = generator.generate_markdown(args.title)
        output = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{args.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: Consolas, monospace; }}
        .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <pre>{md}</pre>
</body>
</html>"""
    
    # Output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Documentation written to: {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    exit(main())
