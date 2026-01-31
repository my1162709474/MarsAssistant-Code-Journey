#!/usr/bin/env python3
"""
AI Prompt Enhancer - 用AI优化提示词
Day 2: AI Prompt Enhancement Tool

功能：
- 分析现有提示词的结构和效果
- 生成改进后的提示词
- 提供优化建议

https://github.com/my1162709474/MarsAssistant-Code-Journey
"""

class PromptEnhancer:
    """提示词增强器"""
    
    def __init__(self):
        self.strengths = []
        self.weaknesses = []
    
    def analyze(self, prompt: str) -> dict:
        """分析提示词"""
        return {
            "original": prompt,
            "length": len(prompt),
            "structure": self._check_structure(prompt)
        }
    
    def enhance(self, prompt: str) -> str:
        """生成增强版提示词"""
        analysis = self.analyze(prompt)
        # 简单的增强逻辑
        if "请" not in prompt:
            prompt = "请" + prompt
        return f"{prompt}

请逐步思考并解释你的推理过程。"
    
    def _check_structure(self, prompt: str) -> str:
        """检查结构"""
        if len(prompt) > 50:
            return "detailed"
        return "simple"

def main():
    print("AI Prompt Enhancer v1.0")
    enhancer = PromptEnhancer()
    
    sample_prompt = "用Python写一个快速排序"
    enhanced = enhancer.enhance(sample_prompt)
    
    print(f"Original: {sample_prompt}")
    print(f"Enhanced: {enhanced}")

if __name__ == "__main__":
    main()
