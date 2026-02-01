#!/usr/bin/env python3
"""
Markov Chain Text Generator - 马尔可夫链文本生成器
基于N阶马尔可夫链的文本自动生成工具

特点：
- 支持1-3阶马尔可夫链
- 支持中文和英文文本
- 可调节生成文本长度
- 简单易用的API
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import hashlib


class MarkovChain:
    """N阶马尔可夫链文本生成器"""
    
    def __init__(self, order: int = 2):
        if order < 1 or order > 3:
            raise ValueError("Order must be between 1 and 3")
        self.order = order
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.starts: List[Tuple[str, ...]] = []
        self.tokens = set()
        
    def _tokenize(self, text: str) -> List[str]:
        if self._is_chinese(text):
            return list(text)
        else:
            tokens = re.findall(r"\w+|\s+|[^\w\s]", text, re.UNICODE)
            return [t for t in tokens if t.strip()]
    
    def _is_chinese(self, text: str) -> bool:
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return chinese_chars / len(text) > 0.3 if text else False
    
    def _detokenize(self, tokens: List[str]) -> str:
        if not tokens:
            return ""
        result = ""
        for i, token in enumerate(tokens):
            if token in "，。！？；：""''（）【】《》" or token in [".", ",", "!", "?", ";", ":", """, "'", "(", ")"]:
                result += token
            elif i > 0 and tokens[i-1] not in " \t\n" and tokens[i-1] not in "，。！？；：""''（）【】《》.":
                result += " " + token
            else:
                result += token
        return result
    
    def train(self, text: str, min_freq: int = 1) -> None:
        tokens = self._tokenize(text)
        if len(tokens) < self.order + 1:
            print(f"Warning: Text too short for order {self.order} Markov chain")
            return
        
        freq_counter = defaultdict(int)
        for i in range(len(tokens) - self.order):
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            freq_counter[(state, next_token)] += 1
        
        for (state, next_token), freq in freq_counter.items():
            if freq >= min_freq:
                self.chain[state].append(next_token)
        
        for i in range(len(tokens) - self.order):
            state = tuple(tokens[i:i + self.order])
            if i == 0 or tokens[i-1] in "。！？.!?\n":
                self.starts.append(state)
        
        self.tokens.update(tokens)
        if self.starts:
            print(f"Trained with {len(self.chain)} unique states, {len(self.starts)} starting points")
    
    def generate(self, max_length: int = 100, seed: Optional[str] = None) -> str:
        if not self.chain:
            raise ValueError("Chain is empty. Please train the model first.")
        
        if seed:
            seed_tokens = self._tokenize(seed)
            for i in range(len(seed_tokens) - self.order, -1, -1):
                state = tuple(seed_tokens[i:i + self.order])
                if state in self.chain:
                    current = state
                    break
            else:
                current = random.choice(self.starts)
        else:
            current = random.choice(self.starts)
        
        result = list(current)
        
        for _ in range(max_length - self.order):
            if current not in self.chain:
                break
            next_token = random.choice(self.chain[current])
            result.append(next_token)
            current = tuple(result[-self.order:])
            if next_token in "。！？.!?" and len(result) > 10 and random.random() < 0.3:
                break
        
        return self._detokenize(result)
    
    def save(self, filepath: str) -> None:
        data = {
            "order": self.order,
            "chain": {str(k): v for k, v in self.chain.items()},
            "starts": [str(s) for s in self.starts],
            "tokens": list(self.tokens)
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'MarkovChain':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        model = cls(order=data["order"])
        model.chain = {eval(k): v for k, v in data["chain"].items()}
        model.starts = [eval(s) for s in data["starts"]]
        model.tokens = set(data["tokens"])
        
        print(f"Model loaded from {filepath}")
        return model


def demo():
    training_text = """
    人工智能正在改变我们的世界。从自动驾驶汽车到智能助手，
    AI技术已经渗透到生活的方方面面。机器学习使计算机能够
    从数据中学习，而不需要明确的编程。自然语言处理让计算机
    能够理解和生成人类语言。计算机视觉使机器能够"看"和理解图像。
    
    深度学习是机器学习的一个分支，使用多层神经网络来处理数据。
    这些神经网络可以学习数据的复杂模式和特征。卷积神经网络
    特别擅长处理图像数据，而循环神经网络则适合处理序列数据。
    """
    
    print("=" * 60)
    print("Markov Chain Text Generator Demo")
    print("=" * 60)
    
    generator = MarkovChain(order=2)
    generator.train(training_text)
    
    print("\nGenerating text with different lengths:")
    print("-" * 40)
    
    for length in [30, 50, 80]:
        print(f"\nGenerated text ({length} tokens):")
        text = generator.generate(max_length=length)
        print(f"   {text}")
    
    print("\nModel Statistics:")
    print("-" * 40)
    print(f"   Order: {generator.order}")
    print(f"   Unique states: {len(generator.chain)}")
    print(f"   Starting points: {len(generator.starts)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("Interactive mode not implemented in this demo")
    else:
        demo()
