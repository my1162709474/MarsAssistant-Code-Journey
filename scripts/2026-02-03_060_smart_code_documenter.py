#!/usr/bin/env python3
"""
Smart Code Documenter - Day 60
Automatically generate documentation, comments, and API docs for code
"""

import ast
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json


class DocType(Enum):
    """Document type"""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    METHOD = "method"
    ATTRIBUTE = "attribute"


@dataclass
class CodeElement:
    """Code element"""
    name: str
    doc_type: DocType
    content: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: List[Dict] = None
    returns: Optional[str] = None
    examples: List[str] = None
    decorators: List[str] = None


class SmartCodeDocumenter:
    """Smart code documentation generator"""
    
    def __init__(self):
        self.elements: List[CodeElement] = []
        self.source_code = ""
        
    def parse_code(self, code: str) -> List[CodeElement]:
        """Parse code structure"""
        self.source_code = code
        tree = ast.parse(code)
        self.elements = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._extract_function(node)
            elif isinstance(node, ast.ClassDef):
                self._extract_class(node)
                
        return self.elements
    
    def _extract_function(self, node: ast.FunctionDef):
        """Extract function information"""
        docstring = ast.get_docstring(node)
        params = []
        
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": self._get_type_annotation(arg.annotation),
                "default": self._get_default_value(arg)
            }
            params.append(param_info)
        
        returns = self._get_type_annotation(node.returns)
        
        element = CodeElement(
            name=node.name,
            doc_type=DocType.FUNCTION if not node.name.startswith('_') else DocType.METHOD,
            content=ast.get_source_segment(self.source_code, node) or "",
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            docstring=docstring,
            parameters=params,
            returns=returns,
            decorators=[d.id for d in node.decorator_list if isinstance(d, ast.Name)]
        )
        self.elements.append(element)
    
    def _extract_class(self, node: ast.ClassDef):
        """Extract class information"""
        docstring = ast.get_docstring(node)
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._extract_function(item)
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes.append({
                    "name": item.target.id,
                    "type": self._get_type_annotation(item.annotation)
                })
        
        element = CodeElement(
            name=node.name,
            doc_type=DocType.CLASS,
            content=ast.get_source_segment(self.source_code, node) or "",
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            docstring=docstring,
            parameters=attributes
        )
        self.elements.append(element)
    
    def _get_type_annotation(self, annotation) -> str:
        """Get type annotation"""
        if annotation is None:
            return "Any"
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            base = self._get_type_annotation(annotation.value)
            sub = self._get_type_annotation(annotation.slice)
            return f"{base}[{sub}]"
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return "Any"
    
    def _get_default_value(self, arg) -> str:
        """Get default value"""
        if not hasattr(arg, 'default') or arg.default is None:
            return None
        if isinstance(arg.default, ast.Constant):
            return repr(arg.default.value)
        return "..."
    
    def generate_markdown(self, module_name: str = "Module") -> str:
        """Generate Markdown documentation"""
        md = []
        md.append(f"# {module_name}\n")
        md.append("> Auto-generated documentation\n")
        
        for element in self.elements:
            md.append(f"\n## {element.name}\n")
            
            if element.docstring:
                md.append(f"\n{element.docstring}\n")
            
            if element.parameters:
                md.append("\n### Parameters\n")
                md.append("| Name | Type | Default |\n")
                md.append("|------|------|---------|\n")
                for param in element.parameters:
                    default = param.get("default") or "None"
                    md.append(f"| {param['name']} | {param['type']} | {default} |\n")
            
            if element.returns:
                md.append(f"\n### Returns\n\n`{element.returns}`\n")
        
        return "".join(md)
    
    def generate_api_json(self, module_name: str) -> Dict:
        """Generate API JSON documentation"""
        api = {
            "module": module_name,
            "version": "1.0.0",
            "functions": [],
            "classes": []
        }
        
        for elem in self.elements:
            if elem.doc_type == DocType.FUNCTION:
                api["functions"].append({
                    "name": elem.name,
                    "description": elem.docstring,
                    "parameters": elem.parameters,
                    "returns": elem.returns,
                    "decorators": elem.decorators
                })
            elif elem.doc_type == DocType.CLASS:
                api["classes"].append({
                    "name": elem.name,
                    "description": elem.docstring,
                    "methods": [e.name for e in self.elements if e.doc_type == DocType.METHOD]
                })
        
        return api


def demo():
    """Demo"""
    documenter = SmartCodeDocumenter()
    
    # Sample code
    sample_code = '''
def calculate_metrics(values, weights=None):
    """Calculate weighted average and other metrics from a list of values.
    
    Args:
        values: List of numeric values
        weights: Optional weights for each value
    
    Returns:
        Dictionary containing mean, median, and std
    """
    if not values:
        return {"mean": 0, "median": 0, "std": 0}
    
    mean = sum(values) / len(values)
    median = sorted(values)[len(values) // 2]
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    
    return {
        "mean": mean,
        "median": median,
        "std": variance ** 0.5
    }


class DataProcessor:
    """Process and transform data collections efficiently."""
    
    def __init__(self, config=None):
        """Initialize processor with optional configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.cache = {}
    
    def transform(self, data):
        """Apply transformations to each item in the data list.
        
        Args:
            data: List of dictionaries to transform
            
        Returns:
            Transformed data list
        """
        return [{**item, "processed": True} for item in data]
'''
    
    # Parse and generate docs
    elements = documenter.parse_code(sample_code)
    
    print("=== Parsed Elements ===")
    for elem in elements:
        print(f"- {elem.name} ({elem.doc_type.value})")
        if elem.docstring:
            desc = elem.docstring[:50].replace('\n', ' ')
            print(f"  Description: {desc}...")
        if elem.parameters:
            print(f"  Parameters: {[p['name'] for p in elem.parameters]}")
        if elem.returns:
            print(f"  Returns: {elem.returns}")
    
    print("\n=== Markdown Documentation ===")
    print(documenter.generate_markdown("Example Module"))
    
    print("\n=== API JSON ===")
    print(json.dumps(documenter.generate_api_json("example"), indent=2))


if __name__ == "__main__":
    demo()
