"""
AI Prompt Template Manager
============================
A professional tool for managing, organizing, and optimizing AI prompts.

Features:
- Create, edit, and delete prompt templates
- Categorize and tag prompts
- Test prompts with different AI models
- Export/import prompts in various formats
- Analyze prompt effectiveness
- Version control for prompt iterations

Author: AI Code Journey
Date: 2026-02-04
"""

import json
import hashlib
import re
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import os


class PromptCategory(Enum):
    WRITING = "writing"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    UTILITY = "utility"
    CUSTOM = "custom"


class PromptPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PromptVariable:
    """Represents a variable in a prompt template."""
    name: str
    description: str
    default_value: Optional[str] = None
    required: bool = True
    validation_pattern: Optional[str] = None
    
    def validate(self, value: Any) -> bool:
        if self.required and not value:
            return False
        if self.validation_pattern and value:
            if not re.match(self.validation_pattern, str(value)):
                return False
        return True


@dataclass
class PromptTemplate:
    """Represents an AI prompt template."""
    id: str
    name: str
    content: str
    category: PromptCategory
    description: str = ""
    tags: List[str] = field(default_factory=list)
    variables: List[PromptVariable] = field(default_factory=list)
    priority: PromptPriority = PromptPriority.MEDIUM
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def generate(self, **kwargs) -> str:
        """Generate a prompt by filling in variables."""
        prompt = self.content
        for var in self.variables:
            value = kwargs.get(var.name, var.default_value or "")
            if var.required and not value:
                raise ValueError(f"Required variable '{var.name}' is missing")
            prompt = prompt.replace(f"{{{{{var.name}}}}}", str(value))
        return prompt
    
    def get_hash(self) -> str:
        """Get a unique hash for the prompt content."""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"{self.id[:8]}-{content_hash[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        data['category'] = PromptCategory(data['category'])
        data['priority'] = PromptPriority(data['priority'])
        data['variables'] = [PromptVariable(**v) for v in data.get('variables', [])]
        return cls(**data)


@dataclass
class PromptTestResult:
    """Result of testing a prompt."""
    prompt_id: str
    test_input: Dict[str, Any]
    generated_prompt: str
    model_response: str
    rating: int  # 1-5
    feedback: str = ""
    test_date: str = field(default_factory=lambda: datetime.now().isoformat())


class PromptManager:
    """Main class for managing AI prompt templates."""
    
    def __init__(self, storage_path: str = "./prompts"):
        self.storage_path = storage_path
        self.templates: Dict[str, PromptTemplate] = {}
        self.test_results: List[PromptTestResult] = []
        os.makedirs(storage_path, exist_ok=True)
        self._load_all()
    
    def create_template(
        self,
        name: str,
        content: str,
        category: PromptCategory,
        description: str = "",
        tags: Optional[List[str]] = None,
        variables: Optional[List[PromptVariable]] = None,
        priority: PromptPriority = PromptPriority.MEDIUM,
        **kwargs
    ) -> PromptTemplate:
        """Create a new prompt template."""
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id_hash = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:12]
        template_id = f"prompt_{id_hash}"
        
        template = PromptTemplate(
            id=template_id,
            name=name,
            content=content,
            category=category,
            description=description,
            tags=tags or [],
            variables=variables or [],
            priority=priority,
            **kwargs
        )
        
        self.templates[template_id] = template
        self._save(template)
        return template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieve a template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(
        self,
        category: Optional[PromptCategory] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None
    ) -> List[PromptTemplate]:
        """List templates with optional filtering."""
        results = list(self.templates.values())
        
        if category:
            results = [t for t in results if t.category == category]
        
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
        
        if search_query:
            query = search_query.lower()
            results = [
                t for t in results 
                if query in t.name.lower() or query in t.description.lower()
            ]
        
        # Sort by priority and usage
        results.sort(key=lambda t: (-t.priority.value, -t.usage_count))
        return results
    
    def update_template(
        self,
        template_id: str,
        **updates
    ) -> Optional[PromptTemplate]:
        """Update an existing template."""
        template = self.templates.get(template_id)
        if not template:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(template, key) and key not in ['id', 'created_at']:
                setattr(template, key, value)
        
        template.version += 1
        template.updated_at = datetime.now().isoformat()
        
        self._save(template)
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self.templates:
            del self.templates[template_id]
            file_path = os.path.join(self.storage_path, f"{template_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        return False
    
    def record_usage(self, template_id: str, success: bool = True):
        """Record template usage and update success rate."""
        template = self.templates.get(template_id)
        if template:
            template.usage_count += 1
            if success:
                template.success_rate = (
                    (template.success_rate * (template.usage_count - 1) + 1) 
                    / template.usage_count
                )
            self._save(template)
    
    def add_test_result(self, result: PromptTestResult):
        """Record a test result for a prompt."""
        self.test_results.append(result)
        template = self.templates.get(result.prompt_id)
        if template:
            # Update success rate based on ratings
            prompt_results = [
                r for r in self.test_results if r.prompt_id == result.prompt_id
            ]
            avg_rating = sum(r.rating for r in prompt_results) / len(prompt_results)
            template.success_rate = avg_rating / 5.0
            self._save(template)
    
    def export_templates(
        self,
        template_ids: Optional[List[str]] = None,
        format: str = "json"
    ) -> str:
        """Export templates to a string."""
        if template_ids is None:
            templates = list(self.templates.values())
        else:
            templates = [
                self.templates[tid] for tid in template_ids 
                if tid in self.templates
            ]
        
        if format == "json":
            return json.dumps(
                [t.to_dict() for t in templates],
                indent=2,
                ensure_ascii=False
            )
        elif format == "markdown":
            lines = ["# Prompt Templates Export\n"]
            for t in templates:
                lines.append(f"## {t.name} (`{t.id}`)\n")
                lines.append(f"- Category: {t.category.value}")
                lines.append(f"- Tags: {', '.join(t.tags)}")
                lines.append(f"- Usage: {t.usage_count} times")
                lines.append(f"- Success Rate: {t.success_rate*100:.1f}%\n")
                lines.append("```\n" + t.content + "\n```\n")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_templates(self, data: str, format: str = "json") -> int:
        """Import templates from a string."""
        if format == "json":
            templates_data = json.loads(data)
            count = 0
            for t_data in templates_data:
                if 'id' in t_data:
                    # Update existing
                    if t_data['id'] in self.templates:
                        self.update_template(t_data['id'], **t_data)
                else:
                    # Create new
                    self.create_template(**t_data)
                    count += 1
            return count
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def analyze_usage(self) -> Dict[str, Any]:
        """Analyze template usage statistics."""
        templates = list(self.templates.values())
        
        if not templates:
            return {"error": "No templates found"}
        
        total_usage = sum(t.usage_count for t in templates)
        avg_success = sum(t.success_rate for t in templates) / len(templates)
        
        # Category breakdown
        category_stats = {}
        for cat in PromptCategory:
            cat_templates = [t for t in templates if t.category == cat]
            if cat_templates:
                category_stats[cat.value] = {
                    "count": len(cat_templates),
                    "total_usage": sum(t.usage_count for t in cat_templates),
                    "avg_success": sum(t.success_rate for t in cat_templates) / len(cat_templates)
                }
        
        # Top templates
        top_templates = sorted(
            templates,
            key=lambda t: t.usage_count,
            reverse=True
        )[:5]
        
        return {
            "total_templates": len(templates),
            "total_usage": total_usage,
            "average_success_rate": avg_success,
            "category_breakdown": category_stats,
            "top_templates": [
                {"id": t.id, "name": t.name, "usage": t.usage_count}
                for t in top_templates
            ]
        }
    
    def _save(self, template: PromptTemplate):
        """Save template to file."""
        file_path = os.path.join(self.storage_path, f"{template.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load_all(self):
        """Load all templates from storage."""
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        template = PromptTemplate.from_dict(data)
                        self.templates[template.id] = template
                except Exception as e:
                    print(f"Error loading {filename}: {e}")


# Pre-built Template Examples
class BuiltInTemplates:
    """Collection of pre-built prompt templates."""
    
    @staticmethod
    def code_review_template() -> PromptTemplate:
        return PromptTemplate(
            id="builtin_code_review",
            name="Code Review Assistant",
            content="""Review the following code for:
1. Bug detection
2. Performance issues
3. Security vulnerabilities
4. Code style and best practices
5. Potential improvements

Code to review:
```
{code_snippet}
```

Language: {language}
Focus areas: {focus_areas}

Provide a detailed review with specific line numbers and suggestions.""",
            category=PromptCategory.CODING,
            description="Comprehensive code review assistant",
            tags=["review", "quality", "security"],
            variables=[
                PromptVariable(
                    name="code_snippet",
                    description="The code to review",
                    required=True,
                    validation_pattern=r".+"
                ),
                PromptVariable(
                    name="language",
                    description="Programming language",
                    default_value="python",
                    required=False
                ),
                PromptVariable(
                    name="focus_areas",
                    description="Specific areas to focus on",
                    default_value="all",
                    required=False
                )
            ],
            priority=PromptPriority.HIGH
        )
    
    @staticmethod
    def writing_helper_template() -> PromptTemplate:
        return PromptTemplate(
            id="builtin_writing_helper",
            name="Writing Assistant",
            content="""Help me improve the following text:

Original text:
```
{original_text}
```

Writing style: {style}
Target audience: {audience}
Purpose: {purpose}

Please provide:
1. Improved version
2. Explanation of changes
3. Alternative suggestions""",
            category=PromptCategory.WRITING,
            description="General writing improvement assistant",
            tags=["writing", "improvement", "editing"],
            variables=[
                PromptVariable(
                    name="original_text",
                    description="Text to improve",
                    required=True,
                    validation_pattern=r".+"
                ),
                PromptVariable(
                    name="style",
                    description="Desired writing style",
                    default_value="professional",
                    required=False
                ),
                PromptVariable(
                    name="audience",
                    description="Target audience",
                    default_value="general",
                    required=False
                ),
                PromptVariable(
                    name="purpose",
                    description="Purpose of the text",
                    default_value="inform",
                    required=False
                )
            ],
            priority=PromptPriority.MEDIUM
        )
    
    @staticmethod
    def data_analysis_template() -> PromptTemplate:
        return PromptTemplate(
            id="builtin_data_analysis",
            name="Data Analysis Assistant",
            content="""Analyze the following dataset:

Dataset description:
{description}

Data format:
```
{data_format}
```

Questions to answer:
{questions}

Please provide:
1. Summary statistics
2. Key insights and patterns
3. Visualization recommendations
4. Potential correlations""",
            category=PromptCategory.ANALYSIS,
            description="Data analysis and insights assistant",
            tags=["analysis", "data", "statistics"],
            variables=[
                PromptVariable(
                    name="description",
                    description="Description of the dataset",
                    required=True,
                    validation_pattern=r".+"
                ),
                PromptVariable(
                    name="data_format",
                    description="Format of the data (CSV, JSON, etc.)",
                    default_value="CSV",
                    required=False
                ),
                PromptVariable(
                    name="questions",
                    description="Analysis questions",
                    required=True,
                    validation_pattern=r".+"
                )
            ],
            priority=PromptPriority.HIGH
        )


def demo():
    """Demonstrate the Prompt Manager."""
    print("=" * 60)
    print("AI Prompt Template Manager - Demo")
    print("=" * 60)
    
    # Initialize manager
    manager = PromptManager("./demo_prompts")
    
    # Create a custom template
    print("\n1. Creating custom templates...")
    template = manager.create_template(
        name="SQL Query Generator",
        content="""Generate a {dialect} SQL query to {task}.

Requirements:
- Table: {table}
- Conditions: {conditions}
- Sort by: {sort_order}
- Limit: {limit}

Output only the SQL query, nothing else.""",
        category=PromptCategory.CODING,
        description="Generate SQL queries from requirements",
        tags=["sql", "database", "generator"],
        priority=PromptPriority.HIGH
    )
    print(f"   Created: {template.name} ({template.id})")
    
    # Use built-in templates
    print("\n2. Using built-in templates...")
    code_review = BuiltInTemplates.code_review_template()
    print(f"   Loaded: {code_review.name}")
    
    # Generate a prompt
    print("\n3. Generating a prompt...")
    generated = template.generate(
        dialect="PostgreSQL",
        task="find all users who logged in within the last 7 days",
        table="users",
        conditions="last_login > NOW() - INTERVAL '7 days' AND is_active = true",
        sort_order="last_login DESC",
        limit="100"
    )
    print("   Generated SQL Query:")
    print("   " + "\n   ".join(generated.split("\n")))
    
    # List templates
    print("\n4. Listing all templates...")
    all_templates = manager.list_templates()
    print(f"   Total templates: {len(all_templates)}")
    
    # Analyze usage
    print("\n5. Usage analysis...")
    stats = manager.analyze_usage()
    print(f"   Total templates: {stats['total_templates']}")
    print(f"   Total usage: {stats['total_usage']}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
