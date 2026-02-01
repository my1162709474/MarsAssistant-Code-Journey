#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimHash Algorithm for Text Similarity Detection
中文: SimHash算法用于文本相似度检测

Usage:
    sim_hash = SimHash("your text here")
    distance, similarity = sim_hash.compare(another_text)
    
Features:
    - 64-bit hash for efficient comparison
    - Hamming distance calculation
    - Similarity percentage (0-100%)
"""

class SimHash:
    """SimHash implementation for detecting similar texts."""
    
    def __init__(self, text, hash_bits=64):
        """
        Initialize SimHash with text content.
        
        Args:
            text: Input string or iterable of tokens
            hash_bits: Number of bits in hash (default 64)
        """
        self.text = text
        self.hash_bits = hash_bits
        self.hash = self._compute_hash()
    
    def _compute_hash(self):
        """Compute sim hash from text."""
        if not self.text:
            return 0
        
        # Tokenize text
        if isinstance(self.text, str):
            words = self.text.split()
        else:
            words = list(self.text)
        
        if not words:
            return 0
        
        # Initialize hash vectors
        vectors = [0] * self.hash_bits
        
        # Process each word
        for word in words:
            word = word.strip().lower()
            if not word:
                continue
            
            # Compute word hash
            word_hash = self._hash_word(word)
            
            # Add to vectors
            for i in range(self.hash_bits):
                if (word_hash >> i) & 1:
                    vectors[i] += 1
                else:
                    vectors[i] -= 1
        
        # Generate final hash
        hash_value = 0
        for i in range(self.hash_bits):
            if vectors[i] > 0:
                hash_value |= (1 << i)
        
        return hash_value
    
    def _hash_word(self, word):
        """Compute hash value for a single word."""
        h = 0
        for char in word:
            h = ((h * 31) + ord(char)) & 0xFFFFFFFFFFFFFFFF
        return h
    
    def compare(self, other):
        """
        Compare with another SimHash object or text.
        
        Returns:
            Tuple of (hamming_distance, similarity_percentage)
        """
        if other is None:
            return 0, 0
        
        if not isinstance(other, SimHash):
            other = SimHash(other, self.hash_bits)
        
        hamming_distance = 0
        hash1 = self.hash
        hash2 = other.hash
        
        # Count differing bits
        diff = hash1 ^ hash2
        while diff:
            if diff & 1:
                hamming_distance += 1
            diff >>= 1
        
        similarity = (self.hash_bits - hamming_distance) / self.hash_bits * 100
        return hamming_distance, similarity
    
    def __repr__(self):
        return f"SimHash(hash={self.hash:#0{self.hash_bits // 4 + 2}x})"


def demo():
    """Demo of SimHash functionality."""
    print("=" * 50)
    print("SimHash Demo - 文本相似度检测演示")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("The quick brown fox jumps over the lazy dog", 
         "The quick brown fox jumps over the lazy dog"),  # Exact match
        ("The quick brown fox jumps over the lazy dog",
         "A quick brown fox jumped over a sleeping dog"),  # Similar
        ("Hello world!",
         "Goodbye world!"),  # Different
        ("人工智能正在改变世界",
         "AI正在革新我们的生活方式"),  # Chinese text
    ]
    
    texts1 = [tc[0] for tc in test_cases]
    texts2 = [tc[1] for tc in test_cases]
    
    # Create SimHash objects
    hashes = [SimHash(text) for text in texts1]
    
    print("\n相似度对比结果:")
    print("-" * 50)
    
    for i, (text1, text2) in enumerate(test_cases):
        distance, similarity = hashes[i].compare(text2)
        match_type = "完全相同" if similarity == 100 else \
                     "高度相似" if similarity > 70 else \
                     "部分相似" if similarity > 40 else "差异较大"
        
        print(f"\n对比 {i+1}:")
        print(f"  文本1: {text1[:40]}...")
        print(f"  文本2: {text2[:40]}...")
        print(f"  相似度: {similarity:.1f}% ({match_type})")
        print(f"  Hamming距离: {distance}")
    
    # Plagiarism detection demo
    print("\n" + "=" * 50)
    print("抄袭检测示例 / Plagiarism Detection Demo")
    print("=" * 50)
    
    original = """
    Machine learning is a subset of artificial intelligence that 
    enables systems to learn and improve from experience without 
    being explicitly programmed.
    """
    
    plagiarism = """
    Machine learning is a part of AI that allows systems to learn 
    and get better from experience without being explicitly coded.
    """
    
    # Create hashes
    hash1 = SimHash(original)
    hash2 = SimHash(plagiarism)
    
    distance, similarity = hash1.compare(hash2)
    
    print(f"\n原文: {original.strip()[:60]}...")
    print(f"\n疑似抄袭: {plagiarism.strip()[:60]}...")
    print(f"\n相似度: {similarity:.1f}%")
    print(f"检测结论: {'⚠️ 高度相似，可能存在抄袭' if similarity > 80 else '✓ 无明显抄袭痕迹'}")


if __name__ == "__main__":
    demo()
