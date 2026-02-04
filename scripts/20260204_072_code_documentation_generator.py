#!/usr/bin/env python3
"""
Code Documentation Generator
============================
Auto-generate documentation for code files using AST parsing.

Features:
- Extract function/class signatures with docstrings
- Support for Python, JavaScript, Java, C++, Go, Rust
- Generate Markdown/JSON/HTML output formats
- Parse type annotations and complex signatures
"""

import ast
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


@dataclass
class FunctionDoc:
    """Documentation for a function/method."""
    name: str
    signature: str
    docstring: str = ""
    parameters: List[Dict[str, str]] = field(default_factory=list)
    return_type: str = "void"
    line_number: int = 0
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    signature: str
    docstring: str = ""
    base_classes: List[str] = field(default_factory=list)
    methods: List[FunctionDoc] = field(default_factory=list)
    attributes: List[Dict[str, str]] = field(default_factory=list)
    line_number: int = 0


@dataclass
class ImportDoc:
    """Documentation for imports."""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from: bool = False


class CodeDocumentationGenerator:
    """Generate documentation from source code using AST parsing."""
    
    SUPPORTED_EXTENSIONS = {
        '.py', '.pyw',  # Python
        '.js', '.mjs', '.jsx',  # JavaScript
        '.ts', '.tsx',  # TypeScript
        '.java',  # Java
        '.cpp', '.cc', '.cxx', '.hpp', '.h',  # C/C++
        '.go',  # Go
        '.rs',  # Rust
        '.c',  # C
    }
    
    def __init__(self, output_format: str = 'markdown'):
        """Initialize the documentation generator.
        
        Args:
            output_format: 'markdown', 'json', or 'html'
        """
        self.output_format = output_format.lower()
        self.imports: List[ImportDoc] = []
        self.classes: List[ClassDoc] = []
        self.functions: List[FunctionDoc] = []
        self.modules: List[str] = []
        self.file_path: Optional[str] = None
        self.file_content: Optional[str] = None
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a source code file and extract documentation.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Dictionary containing parsed documentation
        """
        self.file_path = file_path
        self.imports = []
        self.classes = []
        self.functions = []
        self.modules = []
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {path.suffix}")
        
        content = path.read_text(encoding='utf-8')
        self.file_content = content
        
        if path.suffix == '.py':
            return self._parse_python(content)
        else:
            return self._parse_generic(content)
    
    def _parse_python(self, content: str) -> Dict[str, Any]:
        """Parse Python source code using AST."""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in Python file: {e}")
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(ImportDoc(
                        module=alias.name,
                        names=[alias.asname] if alias.asname else [alias.name]
                    ))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        self.imports.append(ImportDoc(
                            module=node.module,
                            names=[alias.name],
                            alias=alias.asname,
                            is_from=True
                        ))
        
        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self._parse_class(node)
                self.classes.append(class_doc)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_doc = self._parse_function(node)
                if not self._is_method(func_doc.name):
                    self.functions.append(func_doc)
        
        return self._generate_output()
    
    def _parse_class(self, node: ast.ClassDef) -> ClassDoc:
        """Parse a class definition."""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_attribute_name(base))
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                methods.append(self._parse_function(item))
        
        # Get class signature
        signature = self._get_class_signature(node)
        
        return ClassDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            base_classes=base_classes,
            methods=methods,
            line_number=node.lineno
        )
    
    def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> FunctionDoc:
        """Parse a function/method definition."""
        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(f"@{decorator.id}")
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"@{self._get_attribute_name(decorator)}")
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Get parameters
        parameters = []
        for arg in node.args.args:
            param_type = self._get_annotation_type(arg.annotation)
            parameters.append({
                'name': arg.arg,
                'type': param_type,
                'description': ''
            })
        
        # Handle *args and **kwargs
        if node.args.vararg:
            parameters.append({
                'name': f"*{node.args.vararg.arg}",
                'type': 'varargs',
                'description': 'Variable length arguments'
            })
        if node.args.kwarg:
            parameters.append({
                'name': f"**{node.args.kwarg.arg}",
                'type': 'kwargs',
                'description': 'Keyword arguments'
            })
        
        # Get return type
        return_type = self._get_annotation_type(node.returns)
        
        # Get signature
        signature = self._get_function_signature(node)
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            line_number=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators
        )
    
    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Generate a class signature string."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))
        
        if bases:
            return f"class {node.name}({', '.join(bases)})"
        return f"class {node.name}"
    
    def _get_function_signature(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
        """Generate a function signature string."""
        async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        params = []
        
        for arg in node.args.args:
            param_type = self._get_annotation_type(arg.annotation)
            if param_type:
                params.append(f"{arg.arg}: {param_type}")
            else:
                params.append(arg.arg)
        
        if node.args.vararg:
            vararg_name = node.args.vararg.arg
            vararg_type = self._get_annotation_type(node.args.vararg.annotation)
            if vararg_type:
                params.append(f"*{vararg_name}: {vararg_type}")
            else:
                params.append(f"*{vararg_name}")
        
        if node.args.kwarg:
            kwarg_name = node.args.kwarg.arg
            kwarg_type = self._get_annotation_type(node.args.kwarg.annotation)
            if kwarg_type:
                params.append(f"**{kwarg_name}: {kwarg_type}")
            else:
                params.append(f"**{kwarg_name}")
        
        params_str = ", ".join(params)
        
        return f"{async_prefix}def {node.name}({params_str})"
    
    def _get_annotation_type(self, annotation: Optional[ast.AST]) -> str:
        """Extract type information from an annotation."""
        if annotation is None:
            return ""
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return self._get_attribute_name(annotation)
        elif isinstance(annotation, ast.Subscript):
            base = self._get_annotation_type(annotation.value)
            if isinstance(annotation.slice, ast.Tuple):
                slices = [self._get_annotation_type(s) for s in annotation.slice.elts]
                return f"{base}[{', '.join(slices)}]"
            else:
                slice_val = self._get_annotation_type(annotation.slice)
                return f"{base}[{slice_val}]"
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.BinOp):
            left = self._get_annotation_type(annotation.left)
            right = self._get_annotation_type(annotation.right)
            op = self._get_binop_op(annotation.op)
            return f"({left} {op} {right})"
        
        return ""
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute node."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    
    def _get_binop_op(self, op: ast.AST) -> str:
        """Get the operator symbol for a binary operation."""
        op_map = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.FloorDiv: '//', ast.Mod: '%', ast.Pow: '**',
            ast.LShift: '<<', ast.RShift: '>>', ast.BitOr: '|',
            ast.BitXor: '^', ast.BitAnd: '&', ast.MatMult: '@'
        }
        return op_map.get(type(op), '?')
    
    def _is_method(self, name: str) -> bool:
        """Check if a function is likely a method (starts with _ or is in a class)."""
        return name.startswith('_') or len(self.classes) > 0
    
    def _parse_generic(self, content: str) -> Dict[str, Any]:
        """Parse non-Python files using regex patterns."""
        # Extract imports
        import_pattern = re.compile(r'(?:from|import)\s+([\w.]+)', re.MULTILINE)
        self.modules = import_pattern.findall(content)
        
        # Extract function patterns (generic)
        func_pattern = re.compile(
            r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)|'
            r'(?:async\s+)?(?:const|let|var|def)\s+(\w+)\s*=\s*(?:async\s+)?function',
            re.MULTILINE
        )
        for match in func_pattern.finditer(content):
            func_name = match.group(1) or match.group(2)
            if func_name and not func_name.startswith('_'):
                self.functions.append(FunctionDoc(
                    name=func_name,
                    signature=match.group(0).strip()
                ))
        
        # Extract class patterns
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE)
        for match in class_pattern.finditer(content):
            self.classes.append(ClassDoc(
                name=match.group(1),
                signature=match.group(0).strip(),
                base_classes=[match.group(2)] if match.group(2) else []
            ))
        
        return self._generate_output()
    
    def _generate_output(self) -> Dict[str, Any]:
        """Generate the output in the specified format."""
        result = {
            'file': self.file_path,
            'generated_at': datetime.now().isoformat(),
            'imports': [
                {'module': imp.module, 'names': imp.names, 'alias': imp.alias}
                for imp in self.imports
            ],
            'classes': [],
            'functions': []
        }
        
        for cls in self.classes:
            result['classes'].append({
                'name': cls.name,
                'signature': cls.signature,
                'docstring': cls.docstring,
                'base_classes': cls.base_classes,
                'line_number': cls.line_number,
                'methods': [
                    {
                        'name': m.name,
                        'signature': m.signature,
                        'docstring': m.docstring,
                        'parameters': m.parameters,
                        'return_type': m.return_type,
                        'is_async': m.is_async,
                        'decorators': m.decorators
                    }
                    for m in cls.methods
                ]
            })
        
        for func in self.functions:
            result['functions'].append({
                'name': func.name,
                'signature': func.signature,
                'docstring': func.docstring,
                'parameters': func.parameters,
                'return_type': func.return_type,
                'line_number': func.line_number,
                'is_async': func.is_async,
                'decorators': func.decorators
            })
        
        return result
    
    def generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        data = self._generate_output()
        
        lines = [
            f"# Documentation for {Path(data['file']).name}",
            f"*Generated at: {data['generated_at']}*\n",
            "---",
            "## Table of Contents",
            "- [Imports](#imports)",
            "- [Classes](#classes)",
            "- [Functions](#functions)",
            "\n---"
        ]
        
        # Imports
        if data['imports']:
            lines.extend(["## Imports", ""])
            for imp in data['imports']:
                if imp['alias']:
                    lines.append(f"- `{imp['module']}` as `{imp['alias']}`")
                else:
                    lines.append(f"- `{imp['module']}`")
            lines.append("")
        
        # Classes
        if data['classes']:
            lines.extend(["## Classes", ""])
            for cls in data['classes']:
                lines.append(f"### `{cls['name']}`")
                if cls['docstring']:
                    lines.append(f"\n{cls['docstring']}\n")
                if cls['base_classes']:
                    lines.append(f"*Extends: {', '.join(cls['base_classes'])}*\n")
                lines.append(f"**Signature:** ```{cls['signature']}```\n")
                
                if cls['methods']:
                    lines.append("#### Methods")
                    for method in cls['methods']:
                        lines.append(f"- `{method['name']}`")
                    lines.append("")
        
        # Functions
        if data['functions']:
            lines.extend(["## Functions", ""])
            for func in data['functions']:
                lines.append(f"### `{func['name']}`")
                if func['docstring']:
                    lines.append(f"\n{func['docstring']}\n")
                lines.append(f"**Signature:** ```{func['signature']}```\n")
                if func['parameters']:
                    lines.append("**Parameters:**")
                    for param in func['parameters']:
                        lines.append(f"- `{param['name']}`: {param['type']}")
                    lines.append("")
                if func['return_type']:
                    lines.append(f"**Returns:** `{func['return_type']}`\n")
        
        return '\n'.join(lines)
    
    def generate_html(self) -> str:
        """Generate HTML documentation."""
        data = self._generate_output()
        md = self.generate_markdown()
        
        html_content = md.replace('\n', '<br>').replace('```', '')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }}
        .docstring {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Documentation</h1>
    <pre>{html_content}</pre>
</body>
</html>'''
    
    def save_documentation(self, output_path: Optional[str] = None) -> str:
        """Save documentation to a file.
        
        Args:
            output_path: Path for output file (optional)
            
        Returns:
            Path to the generated documentation file
        """
        if output_path is None:
            if self.file_path:
                base = Path(self.file_path).stem
                ext = '.md' if self.output_format == 'markdown' else f'.{self.output_format}'
                output_path = f"{base}_docs{ext}"
            else:
                output_path = f"documentation.{self.output_format}"
        
        if self.output_format == 'json':
            content = json.dumps(self._generate_output(), indent=2, ensure_ascii=False)
        elif self.output_format == 'html':
            content = self.generate_html()
        else:
            content = self.generate_markdown()
        
        Path(output_path).write_text(content, encoding='utf-8')
        return output_path


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate documentation from code files')
    parser.add_argument('files', nargs='+', help='Source code files to document')
    parser.add_argument('-f', '--format', choices=['markdown', 'json', 'html'], 
                        default='markdown', help='Output format')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    for file_path in args.files:
        try:
            generator = CodeDocumentationGenerator(output_format=args.format)
            data = generator.parse_file(file_path)
            output = generator.save_documentation(args.output)
            
            if args.verbose:
                print(f"[OK] Generated documentation for {file_path}")
                print(f"  - Classes: {len(data['classes'])}")
                print(f"  - Functions: {len(data['functions'])}")
                print(f"  - Output: {output}")
            else:
                print(output)
                
        except Exception as e:
            print(f"[ERROR] Error processing {file_path}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    import sys
    main()
