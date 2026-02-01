#!/usr/bin/env python3
"""
BitNet 量化模型推理工具
=======================
演示 2-bit BitNet 模型的加载和推理流程

功能:
- 量化模型加载
- 权重量化转换
- 推理执行
- 与标准模型对比

Author: MarsAssistant
Date: 2026-02-01
"""

import torch
import numpy as np
from typing import List, Tuple


class BitNetQuantizer:
    """
    BitNet 2-bit量化器
    
    将FP16权重转换为2-bit表示：
    - 00: -1 (负大)
    - 01: -0.5 (负小)
    - 10: 0.5 (正小)
    - 11: 1 (正大)
    """
    
    def __init__(self, bit_width: int = 2):
        self.bit_width = bit_width
        self.levels = 2 ** bit_width - 1  # 3 for 2-bit
        
    def quantize(self, weight: np.ndarray) -> np.ndarray:
        """
        量化权重到指定bit宽度
        """
        # 获取权重的min/max
        w_min, w_max = weight.min(), weight.max()
        
        if w_max == w_min:
            return np.zeros_like(weight, dtype=np.int8)
        
        # 归一化到 [0, 1]
        normalized = (weight - w_min) / (w_max - w_min)
        
        # 量化到 levels
        quantized = np.round(normalized * self.levels).astype(np.int8)
        
        return quantized
    
    def dequantize(self, quantized: np.ndarray) -> np.ndarray:
        """
        从2-bit表示恢复FP16权重
        """
        # 映射表: 2-bit -> FP16
        mapping = {
            0: -1.0,
            1: -0.5,
            2: 0.5,
            3: 1.0
        }
        
        # 批量映射
        result = np.vectorize(mapping.get)(quantized)
        return result.astype(np.float16)
    
    def get_compression_ratio(self, original_shape: Tuple) -> float:
        """
        计算压缩比
        """
        original_bits = np.prod(original_shape) * 16  # FP16 = 16 bits
        quantized_bits = np.prod(original_shape) * self.bit_width
        return original_bits / quantized_bits


class BitNetLayer:
    """
    BitNet 量化神经网络层
    
    演示如何使用量化权重进行前向传播
    """
    
    def __init__(self, in_features: int, out_features: int):
        self.in_features = in_features
        self.out_features = out_features
        
        # 原始FP16权重
        self.weight_fp16 = np.random.randn(out_features, in_features).astype(np.float16)
        
        # 量化器
        self.quantizer = BitNetQuantizer(bit_width=2)
        
        # 2-bit量化权重
        self.weight_quantized = self.quantizer.quantize(self.weight_fp16)
        
        # 计算压缩比
        self.compression_ratio = self.quantizer.get_compression_ratio(
            (out_features, in_features)
        )
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        前向传播（使用量化权重）
        """
        # 解量化
        weight = self.quantizer.dequantize(self.weight_quantized)
        
        # 矩阵乘法
        output = np.matmul(x, weight.T)
        return output
    
    def forward_fp16(self, x: np.ndarray) -> np.ndarray:
        """
        前向传播（使用原始FP16权重）
        """
        output = np.matmul(x, self.weight_fp16.T)
        return output


class BitNetModel:
    """
    完整的 BitNet 模型演示
    
    包含多个量化层，支持：
    - 量化推理
    - 标准FP16推理
    - 性能对比
    """
    
    def __init__(self, hidden_sizes: List[int] = [768, 768, 768]):
        self.layers = []
        self.hidden_sizes = hidden_sizes
        
        # 构建网络
        for i in range(len(hidden_sizes) - 1):
            layer = BitNetLayer(hidden_sizes[i], hidden_sizes[i + 1])
            self.layers.append(layer)
    
    def generate_text(self, prompt: str, max_tokens: int = 10) -> str:
        """
        模拟文本生成（演示用，非真实LLM）
        """
        # 简单token化
        tokens = prompt.split()
        generated = tokens.copy()
        
        for _ in range(max_tokens):
            # 模拟token选择（随机）
            next_token = np.random.choice(['的', '是', '了', '在', '和'])
            generated.append(next_token)
            
            if next_token.endswith('。'):
                break
        
        return ' '.join(generated)
    
    def profile_quantized(self) -> dict:
        """
        分析模型量化后的参数规模
        """
        total_params_fp16 = 0
        total_params_2bit = 0
        
        for layer in self.layers:
            params = layer.in_features * layer.out_features
            total_params_fp16 += params * 2  # FP16 = 2 bytes
            total_params_2bit += params * 1  # 2-bit = 0.25 bytes, 但用1byte存储
        
        return {
            'layers': len(self.layers),
            'hidden_sizes': self.hidden_sizes,
            'total_params_fp16_mb': total_params_fp16 / (1024 * 1024),
            'total_params_2bit_mb': total_params_2bit / (1024 * 1024),
            'compression_ratio': total_params_fp16 / total_params_2bit
        }


def demo():
    """
    演示 BitNet 量化推理
    """
    print("=" * 60)
    print("BitNet 量化模型推理演示")
    print("=" * 60)
    
    # 创建模型
    print("\n[1] 初始化 BitNet 模型...")
    model = BitNetModel(hidden_sizes=[512, 512, 512])
    
    # 量化分析
    print("\n[2] 模型量化分析:")
    profile = model.profile_quantized()
    for key, value in profile.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # 单层演示
    print("\n[3] 单层量化演示:")
    test_input = np.random.randn(1, 512).astype(np.float16)
    
    # FP16推理
    output_fp16 = model.layers[0].forward_fp16(test_input)
    
    # 量化推理
    output_quantized = model.layers[0].forward(test_input)
    
    # 误差分析
    error = np.abs(output_fp16 - output_quantized).mean()
    print(f"   输入形状: {test_input.shape}")
    print(f"   FP16输出范围: [{output_fp16.min():.4f}, {output_fp16.max():.4f}]")
    print(f"   量化输出范围: [{output_quantized.min():.4f}, {output_quantized.max():.4f}]")
    print(f"   平均误差: {error:.6f}")
    
    # 文本生成演示
    print("\n[4] 文本生成演示:")
    prompt = "人工智能是"
    generated = model.generate_text(prompt, max_tokens=15)
    print(f"   提示词: {prompt}")
    print(f"   生成: {generated}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo()
