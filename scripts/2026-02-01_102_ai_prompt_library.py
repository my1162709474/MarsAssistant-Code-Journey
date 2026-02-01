"""
AI Prompt Engineering Template Library
======================================

A collection of reusable, high-quality prompt templates for various AI tasks.
Inspired by prompt engineering best practices and research papers.

Author: MarsAssistant
Date: 2026-02-01
License: MIT
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class TaskType(Enum):
    """Types of AI tasks"""
    CODE_GENERATION = "code_generation"
    TEXT_SUMMARIZATION = "text_summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    TRANSLATION = "translation"
    EXPLANATION = "explanation"
    CODE_REVIEW = "code_review"
    PROBLEM_SOLVING = "problem_solving"
    INSTRUCTION_FOLLOWING = "instruction_following"


@dataclass
class PromptTemplate:
    """
    A structured prompt template with metadata.
    
    Attributes:
        name: Unique identifier for the template
        task_type: Type of AI task this template is for
        template: The actual prompt template with placeholders
        description: Brief description of what this template does
        examples: Optional list of input-output examples
        best_for: Specific use cases where this template excels
    """
    name: str
    task_type: TaskType
    template: str
    description: str
    examples: Optional[List[Dict[str, str]]] = None
    best_for: Optional[List[str]] = None
    
    def format(self, **kwargs) -> str:
        """Format the template with provided values."""
        return self.template.format(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "task_type": self.task_type.value,
            "template": self.template,
            "description": self.description,
            "examples": self.examples,
            "best_for": self.best_for
        }


class PromptLibrary:
    """
    A comprehensive library of AI prompt engineering templates.
    
    Features:
    - Pre-optimized templates for common tasks
    - Template chaining capabilities
    - Easy customization and extension
    - Version tracking for template evolution
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize the library with core templates."""
        
        # ===== CODE GENERATION TEMPLATES =====
        
        self.templates["code_generation_basic"] = PromptTemplate(
            name="code_generation_basic",
            task_type=TaskType.CODE_GENERATION,
            template="""Write a Python function that {description}.

Requirements:
- Function name: `{function_name}`
- Parameters: {parameters}
- Return type: {return_type}
- Include docstring with parameters and return value explanation
- Add type hints for all parameters and return value

{constraints}

Example output format:
```python
def {function_name}({param_types}) -> {return_type}:
    \"\"\"{description}\"\"\"
    # Your code here
    pass
```""",
            description="Basic code generation with clear requirements",
            best_for=["simple functions", "utility scripts", "learning exercises"]
        )
        
        self.templates["code_generation_advanced"] = PromptTemplate(
            name="code_generation_advanced",
            task_type=TaskType.CODE_GENERATION,
            template="""You are an expert software engineer. Implement a {language} solution for the following problem:

**Problem Description:**
{problem_description}

**Requirements:**
1. **Functional Requirements:**
{functional_requirements}

2. **Non-Functional Requirements:**
- Time Complexity: {time_complexity}
- Space Complexity: {space_complexity}
- Code Style: {code_style} (e.g., PEP8, Google Style)

3. **Edge Cases to Handle:**
{edge_cases}

4. **Testing Strategy:**
{testing_strategy}

**Output Format:**
Provide:
1. Complete, runnable code
2. Unit tests (at least 3 test cases)
3. Usage example
4. Complexity analysis

```python
# Code here
```""",
            description="Advanced code generation with comprehensive requirements",
            examples=[
                {
                    "input": "Implement a rate limiter",
                    "context": "Time complexity: O(1), Space complexity: O(n)"
                }
            ],
            best_for=["complex algorithms", "production code", "system design"]
        )
        
        # ===== PROBLEM SOLVING TEMPLATES =====
        
        self.templates["problem_solving_step_by_step"] = PromptTemplate(
            name="problem_solving_step_by_step",
            task_type=TaskType.PROBLEM_SOLVING,
            template="""Solve the following problem using structured reasoning:

**Problem:** {problem_statement}

**Context:** {context}

**Approach (think step by step):**

### Step 1: Understand the Problem
- What is being asked?
- What are the constraints?
- What is the expected output?

### Step 2: Break Down the Problem
- List key components
- Identify dependencies
- Define success criteria

### Step 3: Develop Solution
- Approach 1: {approach_1}
- Approach 2: {approach_2}
- Best approach: {best_approach} (because {reason})

### Step 4: Implement
```python
# Implementation
```

### Step 5: Verify
- Test cases covered: {test_cases}
- Edge cases handled: {edge_cases}
- Complexity: {complexity}

**Final Answer:** {final_answer}""",
            description="Structured problem-solving template with step-by-step reasoning",
            best_for=["math problems", "logic puzzles", "algorithm design"]
        )
        
        # ===== CODE REVIEW TEMPLATES =====
        
        self.templates["code_review_comprehensive"] = PromptTemplate(
            name="code_review_comprehensive",
            task_type=TaskType.CODE_REVIEW,
            template="""Perform a comprehensive code review of the following {language} code:

**Code:**
```{language}
{code}
```

**Review Criteria:**
1. **Correctness** - Does the code do what it's supposed to?
2. **Performance** - Are there obvious inefficiencies?
3. **Security** - Are there vulnerabilities?
4. **Readability** - Is the code easy to understand?
5. **Maintainability** - Is it well-structured?
6. **Best Practices** - Does it follow language conventions?

**Review Format:**

| Category | Rating | Issues | Suggestions |
|----------|--------|--------|-------------|
| Correctness | 1-5 | ... | ... |
| Performance | 1-5 | ... | ... |
| Security | 1-5 | ... | ... |
| Readability | 1-5 | ... | ... |
| Maintainability | 1-5 | ... | ... |

**Overall Score:** {overall_score}/100

**Critical Issues (must fix):**
1. ...

**Recommended Improvements:**
1. ...
2. ...

**Refactored Code:**
```python
# Improved version
```""",
            description="Thorough code review with scoring and recommendations",
            best_for=["code audits", "learning code review", "quality assurance"]
        )
        
        # ===== EXPLANATION TEMPLATES =====
        
        self.templates["explain_like_im_five"] = PromptTemplate(
            name="explain_like_im_five",
            task_type=TaskType.EXPLANATION,
            template="""Explain the following concept like I'm 5 years old:

**Concept:** {concept}

**Background I know:**
{background}

**Explanation Requirements:**
- Use simple words and analogies
- Avoid technical jargon (or explain it simply)
- Include a relatable example from everyday life
- Maximum 3 short paragraphs
- Make it fun and engaging!

**Example Explanation:**
"Think of {concept} like [relatable example]..."

**Your Turn:**""",
            description="ELI5 style explanations for complex topics",
            best_for=["learning new concepts", "teaching others", " clarification"]
        )
        
        self.templates["technical_explanation"] = PromptTemplate(
            name="technical_explanation",
            task_type=TaskType.EXPLANATION,
            template="""Provide a technical explanation of **{concept}**:

**Target Audience:** {audience} (assumed knowledge level)

**Depth Level:** {depth_level} (overview/intermediate/deep-dive)

**Structure:**
1. **Definition** - What is it?
2. **How It Works** - The mechanism/algorithm/process
3. **Why It Matters** - Importance and applications
4. **Key Components** - Main parts and their roles
5. **Real-World Example** - Practical use case
6. **Comparison** - How it differs from alternatives
7. **Further Reading** - Resources for deeper learning

**Technical Details to Include:**
{technical_details}

**Current State of the Field:**
{state_of_field}

**Explanation:**""",
            description="Comprehensive technical explanation for professionals",
            best_for=["technical documentation", "interview prep", "deep learning"]
        )
        
        # ===== DATA ANALYSIS TEMPLATES =====
        
        self.templates["data_analysis_report"] = PromptTemplate(
            name="data_analysis_report",
            task_type=TaskType.DATA_ANALYSIS,
            template="""Analyze the following dataset and provide insights:

**Dataset Overview:**
- Source: {data_source}
- Rows: {row_count}
- Columns: {columns}
- Data Types: {data_types}

**Analysis Request:**
{analysis_question}

**Required Analysis:**
1. **Descriptive Statistics** - Summary statistics for key variables
2. **Trends** - Identify patterns over time or categories
3. **Correlations** - Relationships between variables
4. **Anomalies** - Outliers or unusual patterns
5. **Recommendations** - Actionable insights

**Output Format:**
```markdown
# Data Analysis Report

## Executive Summary
[Brief overview of findings]

## Key Findings
1. ...
2. ...
3. ...

## Detailed Analysis
### [Section 1]
### [Section 2]

## Recommendations
1. ...
2. ...

## Visualizations
- [Chart 1 description]
- [Chart 2 description]
```

**Data Sample:**
```{language}
{data_sample}
```

**Analysis:**""",
            description="Structured data analysis with report generation",
            best_for=["business intelligence", "research analysis", "decision support"]
        )
        
        # ===== TEXT SUMMARIZATION TEMPLATES =====
        
        self.templates["text_summarization_abstractive"] = PromptTemplate(
            name="text_summarization_abstractive",
            task_type=TaskType.TEXT_SUMMARIZATION,
            template="""Summarize the following text using abstractive summarization:

**Original Text:**
{original_text}

**Summary Requirements:**
- Length: {summary_length} (words/sentences/paragraphs)
- Style: {style} (formal/casual/technical)
- Audience: {audience}
- Key Points to Preserve: {key_points}

**Summary Guidelines:**
1. Capture the main ideas, not just surface-level facts
2. Use your own words (paraphrase when possible)
3. Maintain the original meaning and tone
4. Include any critical numbers or statistics
5. Omit unnecessary details and examples

**Output:**
{summarized_text}""",
            description="Abstractive summarization preserving meaning",
            best_for=["article summarization", "meeting notes", "document review"]
        )
        
        # ===== CREATIVE WRITING TEMPLATES =====
        
        self.templates["creative_writing_story"] = PromptTemplate(
            name="creative_writing_story",
            task_type=TaskType.CREATIVE_WRITING,
            template="""Write a creative short story with the following parameters:

**Genre:** {genre}
**Theme:** {theme}
**Tone:** {tone} (e.g., humorous, suspenseful, heartfelt)
**Length:** {length} (short/medium/long)
** POV:** {pov} (first-person/third-person/omniscient)

**Character Profile:**
- Protagonist: {protagonist}
- Motivation: {motivation}
- Conflict: {conflict}

**Setting:**
- Time period: {time_period}
- Location: {location}
- Atmosphere: {atmosphere}

**Plot Structure:**
- Opening hook: {opening_hook}
- Rising action: {rising_action}
- Climax: {climax}
- Resolution: {resolution}

**Story Prompt:**
{story_prompt}

**Story:**
""",
            description="Guided creative writing with detailed parameters",
            best_for=["fiction writing", "content creation", "entertainment"]
        )
        
        # ===== INSTRUCTION FOLLOWING TEMPLATES =====
        
        self.templates["instruction_following_strict"] = PromptTemplate(
            name="instruction_following_strict",
            task_type=TaskType.INSTRUCTION_FOLLOWING,
            template="""Follow these instructions exactly:

**Task:** {task_description}

**Constraints (MUST FOLLOW):**
1. {constraint_1}
2. {constraint_2}
3. {constraint_3}
4. {constraint_4}
5. {constraint_5}

**Format Requirements:**
```
{output_format}
```

**Input Data:**
{input_data}

**Output (follow format exactly):**
""",
            description="Strict instruction following with format enforcement",
            best_for=["data transformation", "format conversion", "structured output"]
        )
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self, task_type: Optional[TaskType] = None) -> List[str]:
        """List available templates, optionally filtered by task type."""
        if task_type:
            return [name for t, template in self.templates.items() 
                    if template.task_type == task_type]
        return list(self.templates.keys())
    
    def search_templates(self, query: str) -> List[str]:
        """Search templates by description or name."""
        query = query.lower()
        return [name for name, template in self.templates.items()
                if query in template.name.lower() or 
                   query in template.description.lower()]
    
    def add_template(self, template: PromptTemplate):
        """Add a new template to the library."""
        self.templates[template.name] = template
    
    def export_library(self) -> Dict[str, Any]:
        """Export the entire library as a dictionary."""
        return {
            "version": self.VERSION,
            "total_templates": len(self.templates),
            "templates": {name: t.to_dict() for name, t in self.templates.items()}
        }
    
    def export_json(self, filename: str = "prompt_library.json"):
        """Export the library to a JSON file."""
        data = self.export_library()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Library exported to {filename}")
    
    def create_chain_prompt(self, 
                           template_names: List[str],
                           intermediate_outputs: Dict[str, str],
                           final_format: str) -> str:
        """
        Create a chained prompt from multiple templates.
        
        Example:
            templates = ["extract_info", "summarize", "translate"]
            outputs = {"extract_info": "...", "summarize": "..."}
            Returns a combined prompt
        """
        combined_context = []
        for name in template_names:
            if name in self.templates:
                template = self.templates[name]
                combined_context.append(
                    f"[{name}]: {template.description}\n"
                    f"Template: {template.template[:100]}..."
                )
        
        return f"""Based on the following chain of thought:

{chr(10).join(combined_context)}

Intermediate Results:
{json.dumps(intermediate_outputs, indent=2)}

{final_format}
"""


# ===== DEMONSTRATION =====
if __name__ == "__main__":
    library = PromptLibrary()
    
    print("=" * 60)
    print("AI Prompt Engineering Template Library v" + library.VERSION)
    print("=" * 60)
    print()
    
    # List all templates
    print("Available Templates:")
    print("-" * 40)
    for name in library.list_templates():
        template = library.get_template(name)
        print(f"• {name} [{template.task_type.value}]")
        print(f"  {template.description}")
    print()
    
    # Demonstrate usage
    print("Example Usage - Code Generation:")
    print("-" * 40)
    code_template = library.get_template("code_generation_basic")
    if code_template:
        example_prompt = code_template.format(
            description="calculates the Fibonacci sequence up to n",
            function_name="fibonacci",
            parameters="n: int",
            return_type="List[int]",
            constraints="- Use dynamic programming for efficiency"
        )
        print(example_prompt)
    print()
    
    # Export library
    print("Exporting library to JSON...")
    library.export_json()
    print("Done!")
