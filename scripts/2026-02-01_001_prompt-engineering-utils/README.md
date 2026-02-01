# AI Prompt Engineering Utilities

A collection of reusable prompt templates and utilities for working with LLMs.

## Features

- Structured prompt templates
- Prompt optimization helpers
- Common use-case prompts

## Usage

```python
from prompt_utils import PromptTemplates, PromptOptimizer

# Use built-in templates
template = PromptTemplates.get_writing_prompt(
    topic="Explain quantum computing",
    audience="beginners",
    style="engaging"
)

# Optimize your own prompts
optimized = PromptOptimizer.make_specific(
    original="Write about AI"
)
```

## Prompt Templates

### Writing Prompts
- `get_writing_prompt(topic, audience, style)` - Generate writing prompts
- `get_summar_prompt(text, length)` - Summarize text

### Code Prompts  
- `get_code_review_prompt(code, language)` - Code review prompts
- `get_debug_prompt(error, code)` - Debugging assistance

### Learning Prompts
- `get_explain_prompt(topic, level)` - Explain concepts at various levels
- `get_quiz_prompt(topic, num_questions)` - Generate quizzes

## Prompt Engineering Tips

1. **Be Specific**: Clear, detailed instructions yield better results
2. **Set Context**: Provide background information
3. **Define Format**: Specify desired output structure
4. **Use Examples**: Show what you want with examples
5. **Iterate**: Refine prompts based on outputs

## License

MIT
