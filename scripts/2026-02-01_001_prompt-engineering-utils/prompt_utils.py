"""
AI Prompt Engineering Utilities
================================
A collection of reusable prompt templates and utilities for working with LLMs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class WritingStyle(Enum):
    """Available writing styles for content generation."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    HUMOROUS = "humorous"


class AudienceLevel(Enum):
    """Audience complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class SummaryLength(Enum):
    """Summary length options."""
    SHORT = "short"      # 1-2 sentences
    MEDIUM = "medium"    # 1 paragraph
    LONG = "long"        # Multiple paragraphs


@dataclass
class WritingPrompt:
    """Structured prompt for writing tasks."""
    topic: str
    audience: str
    style: str
    format: str = "paragraph"
    length: str = "medium"
    extra_instructions: str = ""


class PromptTemplates:
    """Collection of reusable prompt templates."""
    
    @staticmethod
    def get_writing_prompt(
        topic: str,
        audience: str,
        style: WritingStyle,
        format: str = "paragraph",
        length: str = "medium"
    ) -> str:
        """Generate a structured writing prompt.
        
        Args:
            topic: The subject to write about
            audience: Target audience description
            style: Writing style
            format: Output format (paragraph, bullet_points, etc.)
            length: Desired length
        
        Returns:
            Optimized prompt string
        """
        style_guide = {
            WritingStyle.PROFESSIONAL: "Use formal language, clear structure, and objective tone.",
            WritingStyle.CASUAL: "Use conversational tone, relatable examples, and engaging language.",
            WritingStyle.ACADEMIC: "Use scholarly language, cite concepts, maintain objectivity.",
            WritingStyle.CREATIVE: "Use vivid imagery, storytelling elements, and engaging narrative.",
            WritingStyle.TECHNICAL: "Use precise terminology, include technical details.",
            WritingStyle.HUMOROUS: "Include wit, clever observations, and lighthearted tone."
        }
        
        prompt = f"""Write about {topic}.
Target audience: {audience}
Style: {style_guide.get(style, style.value)}
Format: {format}
Length: {length}

Ensure the content is well-structured, engaging, and meets the above requirements."""
        
        return prompt
    
    @staticmethod
    def get_summary_prompt(
        text: str,
        length: SummaryLength = SummaryLength.MEDIUM,
        focus: Optional[str] = None
    ) -> str:
        """Generate a summarization prompt.
        
        Args:
            text: Text to summarize
            length: Desired summary length
            focus: Optional aspect to focus on
        
        Returns:
            Summarization prompt
        """
        length_guide = {
            SummaryLength.SHORT: "in 1-2 concise sentences",
            SummaryLength.MEDIUM: "in one comprehensive paragraph",
            SummaryLength.LONG: "in multiple detailed paragraphs, covering key points"
        }
        
        focus_note = f" Focus specifically on: {focus}" if focus else ""
        
        return f"""Summarize the following text {length_guide.get(length, length.value)}.{focus_note}

Text:
---
{text}
---

Summary:"""
    
    @staticmethod
    def get_code_review_prompt(
        code: str,
        language: str = "python",
        focus: Optional[str] = None
    ) -> str:
        """Generate a code review prompt.
        
        Args:
            code: Code to review
            language: Programming language
            focus: Optional specific aspects to focus on
        
        Returns:
            Code review prompt
        """
        focus_items = []
        if focus:
            focus_items.append(focus)
        focus_items.extend(["potential bugs", "performance issues", "code clarity"])
        
        return f"""Review the following {language} code.

Focus areas: {', '.join(focus_items)}

Code:
```{language}
{code}
```

Provide your review in this format:
1. **Strengths**: What works well
2. **Issues Found**: Bugs, improvements, concerns
3. **Suggestions**: Specific recommendations
4. **Overall Assessment**: Brief summary"""
    
    @staticmethod
    def get_debug_prompt(
        error: str,
        code: str,
        language: str = "python"
    ) -> str:
        """Generate a debugging assistance prompt.
        
        Args:
            error: Error message or description
            code: Relevant code
            language: Programming language
        
        Returns:
            Debugging prompt
        """
        return f"""Help debug this {language} code.

Error:
```
{error}
```

Code:
```{language}
{code}
```

Please:
1. Explain what caused the error
2. Suggest the fix
3. Provide corrected code
4. Offer prevention tips"""
    
    @staticmethod
    def get_explain_prompt(
        topic: str,
        level: AudienceLevel = AudienceLevel.INTERMEDIATE,
        format: str = "explanation"
    ) -> str:
        """Generate an explanation prompt.
        
        Args:
            topic: Topic to explain
            level: Audience expertise level
            format: Output format
        
        Returns:
            Explanation prompt
        """
        level_guide = {
            AudienceLevel.BEGINNER: "Assume no prior knowledge. Start from absolute basics.",
            AudienceLevel.INTERMEDIATE: "Assume basic familiarity. Build on fundamentals.",
            AudienceLevel.EXPERT: "Assume deep knowledge. Can use technical terminology freely."
        }
        
        format_examples = {
            "explanation": "Provide a clear, structured explanation.",
            "analogy": "Use real-world analogies to illustrate the concept.",
            "stepbystep": "Break down into numbered steps.",
            "comparison": "Compare with related concepts."
        }
        
        return f"""Explain {topic}.

Audience level: {level.value}
{level_guide.get(level, '')}
Format: {format_examples.get(format, format)}

Make it educational, engaging, and appropriate for the specified audience."""
    
    @staticmethod
    def get_quiz_prompt(
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """Generate a quiz generation prompt.
        
        Args:
            topic: Topic for the quiz
            num_questions: Number of questions
            difficulty: Difficulty level
        
        Returns:
            Quiz generation prompt
        """
        return f"""Create a {difficulty}-difficulty quiz about {topic}.

Requirements:
- {num_questions} questions total
- Mix of multiple choice and short answer
- Include an answer key
- Test understanding, not just memorization

Format:
Question 1: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct answer]

[Repeat for all questions]

---  
ANSWER KEY:
1. [Answer]
2. [Answer]
etc."""


class PromptOptimizer:
    """Utilities for optimizing prompts."""
    
    @staticmethod
    def make_specific(
        original: str,
        context: Optional[str] = None,
        output_format: Optional[str] = None,
        constraints: Optional[list] = None
    ) -> str:
        """Make a vague prompt more specific and effective.
        
        Args:
            original: Original vague prompt
            context: Additional context
            output_format: Desired output format
            constraints: List of constraints
        
        Returns:
            Optimized prompt
        """
        optimized = original
        
        if context:
            optimized = f"Context: {context}\n\nTask: {optimized}"
        
        if output_format:
            optimized += f"\n\nOutput format: {output_format}"
        
        if constraints:
            constraints_text = "\n".join(f"- {c}" for c in constraints)
            optimized += f"\n\nConstraints:\n{constraints_text}"
        
        optimized += "\n\nBe specific, detailed, and thorough."
        
        return optimized
    
    @staticmethod
    def add_examples(original: str, examples: list) -> str:
        """Add examples to a prompt.
        
        Args:
            original: Original prompt
            examples: List of input-output examples
        
        Returns:
            Prompt with examples
        """
        example_section = "\n\nExamples:\n"
        for i, (inp, out) in enumerate(examples, 1):
            example_section += f"Example {i}:\nInput: {inp}\nOutput: {out}\n\n"
        
        return original + example_section
    
    @staticmethod
    def add_chain_of_thought(original: str) -> str:
        """Add chain-of-thought instruction to prompt.
        
        Args:
            original: Original prompt
        
        Returns:
            Prompt with CoT instruction
        """
        return f"""{original}

Before giving your final answer, think through this step by step.
Show your reasoning process clearly."""
    
    @staticmethod
    def add_role_play(original: str, role: str, expertise: str) -> str:
        """Add role-playing context to prompt.
        
        Args:
            original: Original prompt
            role: Role to adopt
            expertise: Level of expertise
        
        Returns:
            Role-play enhanced prompt
        """
        return f"""You are a {role} with {expertise} expertise.

{original}

Respond as this expert would, using your knowledge and professional judgment."""


# Convenience functions
def write_about(topic, audience="general", style=WritingStyle.CASUAL):
    """Quick writing prompt helper."""
    return PromptTemplates.get_writing_prompt(topic, audience, style)


def summarize(text, length=SummaryLength.MEDIUM):
    """Quick summary helper."""
    return PromptTemplates.get_summary_prompt(text, length)


def review_code(code, language="python"):
    """Quick code review helper."""
    return PromptTemplates.get_code_review_prompt(code, language)


def explain(topic, level=AudienceLevel.INTERMEDIATE):
    """Quick explanation helper."""
    return PromptTemplates.get_explain_prompt(topic, level)


if __name__ == "__main__":
    # Demo usage
    print("=== AI Prompt Engineering Utilities Demo ===\n")
    
    # Writing prompt example
    writing = write_about("artificial intelligence", "students", WritingStyle.CASUAL)
    print("1. Writing Prompt:")
    print(writing[:200] + "...\n")
    
    # Summary prompt example
    sample_text = "Python is a high-level programming language known for its simplicity and readability."
    summary = summarize(sample_text, SummaryLength.SHORT)
    print("2. Summary Prompt:")
    print(summary[:150] + "...\n")
    
    # Explanation prompt example
    explain_prompt = explain("machine learning", AudienceLevel.BEGINNER)
    print("3. Explanation Prompt:")
    print(explain_prompt[:200] + "...\n")
    
    print("✓ Import this module to use in your AI projects!")
