#!/usr/bin/env python3
"""
批量图片处理器 (Day 24)

支持图片批量缩放、裁剪、格式转换、旋转、水印添加等操作。

功能:
- 批量缩放指定尺寸
- 裁剪指定区域
- 格式转换 (PNG/JPG/GIF/BMP/WEBP)
- 批量添加水印
- 旋转/翻转图片
- 调整亮度/对比度

依赖: pip install Pillow

作者: AI Assistant
日期: 2026-02-02
"""

import os
import sys
import base64
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
from PIL import Image, ImageEnhance, ImageDraw, ImageFont


class ImageProcessor:
    """批量图片处理器类"""
    
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    def __init__(self, input_dir: str, output_dir: str = None):
        """
        初始化处理器
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径 (默认: input_dir/processed)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = output_dir or self.input_dir / 'processed'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'total_size_before': 0,
            'total_size_after': 0
        }
    
    def load_images(self) -> List[Path]:
        """加载所有支持的图片文件"""
        images = []
        for ext in self.SUPPORTED_FORMATS:
            images.extend(self.input_dir.rglob(f'*{ext}'))
            images.extend(self.input_dir.rglob(f'*{ext.upper()}'))
        return sorted(set(images))
    
    def resize(self, image_path: Path, size: Tuple[int, int], 
               maintain_aspect: bool = True) -> Image.Image:
        """
        调整图片尺寸
        
        Args:
            image_path: 图片路径
            size: 目标尺寸 (width, height)
            maintain_aspect: 是否保持宽高比
        """
        img = Image.open(image_path)
        
        if maintain_aspect:
            img.thumbnail(size, Image.Resampling.LANCZOS)
        else:
            img = img.resize(size, Image.Resampling.LANCZOS)
        
        return img
    
    def crop(self, image_path: Path, box: Tuple[int, int, int, int]) -> Image.Image:
        """
        裁剪图片
        
        Args:
            image_path: 图片路径
            box: 裁剪区域 (left, upper, right, lower)
        """
        img = Image.open(image_path)
        return img.crop(box)
    
    def convert_format(self, image_path: Path, output_format: str) -> Image.Image:
        """
        转换图片格式
        
        Args:
            image_path: 图片路径
            output_format: 目标格式 (PNG/JPG/GIF/BMP/WEBP)
        """
        img = Image.open(image_path)
        return img
    
    def rotate(self, image_path: Path, degrees: float, 
               expand: bool = True) -> Image.Image:
        """
        旋转图片
        
        Args:
            image_path: 图片路径
            degrees: 旋转角度（正数为逆时针）
            expand: 是否扩展画布以容纳旋转后的图片
        """
        img = Image.open(image_path)
        return img.rotate(degrees, expand=expand)
    
    def flip(self, image_path: Path, direction: str = 'horizontal') -> Image.Image:
        """
        翻转图片
        
        Args:
            image_path: 图片路径
            direction: 翻转方向 ('horizontal' 或 'vertical')
        """
        img = Image.open(image_path)
        
        if direction == 'horizontal':
            return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            raise ValueError("direction必须是 'horizontal' 或 'vertical'")
    
    def adjust_brightness(self, image_path: Path, factor: float) -> Image.Image:
        """
        调整亮度
        
        Args:
            image_path: 图片路径
            factor: 亮度因子 (1.0 为原图, >1.0 更亮, <1.0 更暗)
        """
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, image_path: Path, factor: float) -> Image.Image:
        """
        调整对比度
        
        Args:
            image_path: 图片路径
            factor: 对比度因子 (1.0 为原图)
        """
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def add_watermark(self, image_path: Path, text: str, 
                      position: str = 'bottom-right', 
                      font_size: int = 20,
                      color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """
        添加文字水印
        
        Args:
            image_path: 图片路径
            text: 水印文字
            position: 位置 ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
            font_size: 字体大小
            color: 文字颜色 (RGB)
        """
        img = Image.open(image_path).convert('RGBA')
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        img_width, img_height = img.size
        
        # 计算位置
        positions = {
            'top-left': (10, 10),
            'top-right': (img_width - text_width - 10, 10),
            'bottom-left': (10, img_height - text_height - 10),
            'bottom-right': (img_width - text_width - 10, img_height - text_height - 10),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2)
        }
        
        pos = positions.get(position, positions['bottom-right'])
        
        # 绘制半透明背景
        padding = 5
        bg_box = (pos[0] - padding, pos[1] - padding,
                  pos[0] + text_width + padding, pos[1] + text_height + padding)
        draw.rectangle(bg_box, fill=(0, 0, 0, 128))
        
        # 绘制文字
        draw.text(pos, text, fill=color + (255,), font=font)
        
        # 合并图层
        watermarked = Image.alpha_composite(img, overlay)
        return watermarked.convert('RGB')
    
    def process_batch(self, operation: str, **kwargs):
        """
        批量处理图片
        
        Args:
            operation: 操作类型 (resize/crop/convert/rotate/flip/brightness/contrast/watermark)
            **kwargs: 操作参数
        """
        images = self.load_images()
        self.stats['total'] = len(images)
        
        print(f"📁 发现 {len(images)} 张图片")
        print(f"📂 输入目录: {self.input_dir}")
        print(f"📂 输出目录: {self.output_dir}")
        print("-" * 50)
        
        for i, image_path in enumerate(images, 1):
            try:
                # 统计原始大小
                original_size = image_path.stat().st_size
                self.stats['total_size_before'] += original_size
                
                # 根据操作类型处理图片
                if operation == 'resize':
                    result = self.resize(image_path, kwargs['size'], kwargs.get('maintain_aspect', True))
                elif operation == 'crop':
                    result = self.crop(image_path, kwargs['box'])
                elif operation == 'convert':
                    result = self.convert_format(image_path, kwargs['format'])
                elif operation == 'rotate':
                    result = self.rotate(image_path, kwargs['degrees'])
                elif operation == 'flip':
                    result = self.flip(image_path, kwargs['direction'])
                elif operation == 'brightness':
                    result = self.adjust_brightness(image_path, kwargs['factor'])
                elif operation == 'contrast':
                    result = self.adjust_contrast(image_path, kwargs['factor'])
                elif operation == 'watermark':
                    result = self.add_watermark(image_path, kwargs['text'], 
                                               kwargs.get('position', 'bottom-right'),
                                               kwargs.get('font_size', 20),
                                               kwargs.get('color', (255, 255, 255)))
                else:
                    raise ValueError(f"不支持的操作: {operation}")
                
                # 保存结果
                output_name = image_path.stem
                output_ext = f".{kwargs.get('format', image_path.suffix[1:]).lower()}"
                if operation == 'watermark':
                    output_ext = '.jpg'
                
                output_path = self.output_dir / f"{output_name}_processed{output_ext}"
                result.save(output_path, quality=95)
                
                # 统计处理后大小
                processed_size = output_path.stat().st_size
                self.stats['total_size_after'] += processed_size
                self.stats['success'] += 1
                
                print(f"✅ [{i}/{len(images)}] {image_path.name} → {output_path.name}")
                
            except Exception as e:
                self.stats['failed'] += 1
                print(f"❌ [{i}/{len(images)}] {image_path.name}: {e}")
        
        self.print_stats()
    
    def print_stats(self):
        """打印处理统计"""
        print("-" * 50)
        print(f"📊 处理统计:")
        print(f"   总图片数: {self.stats['total']}")
        print(f"   成功处理: {self.stats['success']}")
        print(f"   处理失败: {self.stats['failed']}")
        
        if self.stats['total_size_before'] > 0:
            before_mb = self.stats['total_size_before'] / (1024 * 1024)
            after_mb = self.stats['total_size_after'] / (1024 * 1024)
            ratio = (1 - self.stats['total_size_after'] / self.stats['total_size_before']) * 100
            
            print(f"   原始大小: {before_mb:.2f} MB")
            print(f"   处理后大小: {after_mb:.2f} MB")
            print(f"   大小变化: {ratio:.1f}%")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='批量图片处理器 - 缩放/裁剪/转换/水印',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./images --resize 800 600
  %(prog)s ./images --crop 0 0 400 400
  %(prog)s ./images --convert png
  %(prog)s ./images --rotate 90
  %(prog)s ./images --flip horizontal
  %(prog)s ./images --watermark "© 2026"
  %(prog)s ./images --brightness 1.2 --contrast 1.1
        """
    )
    
    parser.add_argument('input_dir', help='输入图片目录')
    parser.add_argument('--output', '-o', help='输出目录 (默认: input_dir/processed)')
    
    # 操作参数
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('--resize', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                                  help='调整尺寸 (宽 高)')
    operation_group.add_argument('--crop', nargs=4, type=int, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'),
                                  help='裁剪区域 (左 上 右 下)')
    operation_group.add_argument('--convert', choices=['png', 'jpg', 'gif', 'bmp', 'webp'],
                                  help='转换格式')
    operation_group.add_argument('--rotate', type=float, metavar='DEGREES',
                                  help='旋转角度 (度)')
    operation_group.add_argument('--flip', choices=['horizontal', 'vertical'],
                                  help='翻转方向')
    operation_group.add_argument('--watermark', metavar='TEXT',
                                  help='添加水印文字')
    operation_group.add_argument('--brightness', type=float, metavar='FACTOR',
                                  help='调整亮度 (1.0=原图)')
    operation_group.add_argument('--contrast', type=float, metavar='FACTOR',
                                  help='调整对比度 (1.0=原图)')
    
    # 可选参数
    parser.add_argument('--maintain-aspect', action='store_true', default=True,
                        help='保持宽高比 (默认: True)')
    parser.add_argument('--watermark-position', choices=['top-left', 'top-right', 'bottom-left', 
                                                         'bottom-right', 'center'], 
                        default='bottom-right', help='水印位置')
    parser.add_argument('--font-size', type=int, default=20, help='水印字体大小')
    
    args = parser.parse_args()
    
    # 验证输入目录
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"❌ 错误: 目录不存在: {args.input_dir}")
        sys.exit(1)
    if not input_path.is_dir():
        print(f"❌ 错误: 不是一个目录: {args.input_dir}")
        sys.exit(1)
    
    # 创建处理器
    processor = ImageProcessor(str(input_path), args.output)
    
    # 执行操作
    if args.resize:
        processor.process_batch('resize', size=(args.resize[0], args.resize[1]),
                                maintain_aspect=args.maintain_aspect)
    elif args.crop:
        processor.process_batch('crop', box=tuple(args.crop))
    elif args.convert:
        processor.process_batch('convert', format=args.convert)
    elif args.rotate:
        processor.process_batch('rotate', degrees=args.rotate)
    elif args.flip:
        processor.process_batch('flip', direction=args.flip)
    elif args.watermark:
        processor.process_batch('watermark', text=args.watermark, 
                                position=args.watermark_position,
                                font_size=args.font_size)
    elif args.brightness:
        processor.process_batch('brightness', factor=args.brightness)
    elif args.contrast:
        processor.process_batch('contrast', factor=args.contrast)


if __name__ == '__main__':
    main()
