#!/usr/bin/env python3
"""
Huffman Compression Tool
Day 11: File compression/decompression using Huffman coding
"""

import heapq
import os
import json
from collections import defaultdict, Counter


class HuffmanCoding:
    """Huffman coding implementation for file compression"""
    
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
    
    def frequency_dict(self, text):
        """Build frequency dictionary"""
        return Counter(text)
    
    def build_heap(self, frequency_dict):
        """Build min heap from frequency dictionary"""
        for char, freq in frequency_dict.items():
            heapq.heappush(self.heap, (freq, char))
    
    def build_tree(self):
        """Build Huffman tree using heap"""
        while len(self.heap) > 1:
            freq1, char1 = heapq.heappop(self.heap)
            freq2, char2 = heapq.heappop(self.heap)
            merged_freq = freq1 + freq2
            heapq.heappush(self.heap, (merged_freq, (char1, char2)))
    
    def generate_codes_helper(self, node, current_code):
        """Recursively generate codes"""
        if isinstance(node, str):
            if current_code == "":
                current_code = "0"
            self.codes[node] = current_code
            self.reverse_mapping[current_code] = node
            return
        
        if node[0]:
            self.generate_codes_helper(node[0], current_code + "0")
        if node[1]:
            self.generate_codes_helper(node[1], current_code + "1")
    
    def build_codes(self):
        """Build codes from tree"""
        if self.heap:
            root = self.heap[0][1]
            self.generate_codes_helper(root, "")
    
    def compress(self, text):
        """Compress text using Huffman coding"""
        frequency = self.frequency_dict(text)
        self.build_heap(frequency)
        self.build_tree()
        self.build_codes()
        
        encoded_text = "".join(self.codes[char] for char in text)
        return encoded_text, self.codes
    
    def decompress(self, encoded_text, codes):
        """Decompress text using codes"""
        current_code = ""
        decoded_text = []
        
        for bit in encoded_text:
            current_code += bit
            if current_code in codes:
                decoded_text.append(codes[current_code])
                current_code = ""
        
        return "".join(decoded_text)


def compress_file(input_path, output_path=None):
    """Compress a text file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    huffman = HuffmanCoding()
    encoded_text, codes = huffman.compress(text)
    
    # Save compressed data and codes
    output_data = {
        'encoded': encoded_text,
        'codes': codes
    }
    
    if output_path is None:
        output_path = input_path + '.huff'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f)
    
    original_size = len(text.encode('utf-8'))
    compressed_size = len(json.dumps(output_data).encode('utf-8'))
    ratio = (1 - compressed_size / original_size) * 100
    
    print(f"✅ Compressed: {input_path}")
    print(f"   Original: {original_size} bytes")
    print(f"   Compressed: {compressed_size} bytes")
    print(f"   Ratio: {ratio:.2f}%")
    
    return output_path


def decompress_file(input_path, output_path=None):
    """Decompress a Huffman-encoded file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    huffman = HuffmanCoding()
    decoded_text = huffman.decompress(data['encoded'], data['codes'])
    
    if output_path is None:
        output_path = input_path.replace('.huff', '.decompressed')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
    
    print(f"✅ Decompressed: {input_path} -> {output_path}")
    return output_path


# Example usage and demonstration
if __name__ == "__main__":
    print("=" * 50)
    print("Huffman Coding Compression Tool")
    print("=" * 50)
    
    # Demo with sample text
    sample_text = """
    Artificial Intelligence is transforming our world.
    Machine learning enables computers to learn from data.
    Deep learning uses neural networks with many layers.
    Natural language processing understands human language.
    Computer vision sees and interprets visual information.
    """
    
    print("\n📝 Sample Text:")
    print(sample_text.strip())
    
    huffman = HuffmanCoding()
    encoded, codes = huffman.compress(sample_text)
    
    print(f"\n📊 Compression Results:")
    print(f"   Original length: {len(sample_text)} characters")
    print(f"   Encoded length: {len(encoded)} bits")
    print(f"   Unique characters: {len(codes)}")
    
    print(f"\n🔤 Character Frequencies:")
    for char, freq in sorted(Counter(sample_text).items(), key=lambda x: -x[1])[:5]:
        print(f"   '{char}': {freq}")
    
    # Verify decompression
    decoded = huffman.decompress(encoded, codes)
    print(f"\n✅ Decompression verified: {decoded == sample_text}")
    
    print("\n" + "=" * 50)
    print("Usage:")
    print("  python huffman_compression.py")
    print("  # To compress: compress_file('input.txt', 'output.huff')")
    print("  # To decompress: decompress_file('output.huff')")
    print("=" * 50)
