#!/usr/bin/env python3
"""
🎨 ASCII艺术生成器 - Day 27

一个功能丰富的ASCII艺术生成工具，支持：
- 图片转ASCII艺术
- 文本转ASCII标题
- 多种字符集和宽度调整
- 实时预览和调整
- 保存为文件

作者: MarsAssistant
日期: 2026-02-02
"""

import base64
import io
import os
import sys
from typing import Optional, Tuple, List

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Pillow未安装，图片功能将受限")
    print("💡 安装命令: pip install Pillow")


class ASCIIArtGenerator:
    """ASCII艺术生成器类"""
    
    # ASCII字符集（从暗到亮）
    CHARSETS = {
        'simple': '@%#*+=-:. ',
        'detailed': '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',
        'blocks': '█▓▒░ ',
        'binary': '01 ',
        'minimal': '#. ',
        'rainbow': 'ROYGBIV',
    }
    
    def __init__(self, charset: str = 'detailed', width: int = 100):
        """
        初始化ASCII生成器
        
        Args:
            charset: 字符集名称
            width: 输出宽度
        """
        self.charset_name = charset
        self.chars = self.CHARSETS.get(charset, self.CHARSETS['detailed'])
        self.width = width
    
    def resize_image(self, image, new_width: int) -> Image.Image:
        """调整图片大小，保持宽高比"""
        height = int(new_width * image.size[1] / image.size[0] * 0.55)
        return image.resize((new_width, height))
    
    def image_to_ascii(self, image_path: str, width: Optional[int] = None, 
                       invert: bool = False, colored: bool = False) -> str:
        """
        将图片转换为ASCII艺术
        
        Args:
            image_path: 图片路径
            width: 输出宽度
            invert: 是否反转字符顺序
            colored: 是否保留颜色
            
        Returns:
            ASCII艺术字符串
        """
        if not PIL_AVAILABLE:
            return "❌ 需要安装Pillow库才能处理图片"
        
        if width is None:
            width = self.width
        
        try:
            img = Image.open(image_path)
            
            # 转换为灰度图
            img = img.convert('L')
            
            # 调整大小
            img = self.resize_image(img, width)
            
            # 获取像素数据
            pixels = list(img.getdata())
            
            # 获取字符集
            chars = self.chars
            if invert:
                chars = chars[::-1]
            
            char_len = len(chars)
            
            # 构建ASCII字符串
            ascii_str = ""
            for i, pixel in enumerate(pixels):
                # 映射像素值到字符集索引
                char_idx = int(pixel * (char_len - 1) / 255)
                ascii_str += chars[char_idx]
                
                # 每行结束添加换行
                if (i + 1) % width == 0:
                    ascii_str += '\n'
            
            return ascii_str
            
        except Exception as e:
            return f"❌ 处理图片时出错: {str(e)}"
    
    def text_to_ascii(self, text: str, font: str = 'big') -> str:
        """
        将文本转换为ASCII标题（使用预定义字体）
        
        Args:
            text: 输入文本
            font: 字体风格
            
        Returns:
            ASCII标题字符串
        """
        # 简单的ASCII艺术字体定义
        fonts = {
            'big': {
                'A': ['  A  ', ' A A ', 'AAAAA', 'A   A', 'A   A'],
                'B': ['BBBB ', 'B   B', 'BBBB ', 'B   B', 'BBBB '],
                'C': [' CCC ', 'C    ', 'C    ', 'C    ', ' CCC '],
                'D': ['DDDD ', 'D   D', 'D   D', 'D   D', 'DDDD '],
                'E': ['EEEEE', 'E    ', 'EEE  ', 'E    ', 'EEEEE'],
                'F': ['FFFFF', 'F    ', 'FFF  ', 'F    ', 'F    ],
                'G': [' GGG ', 'G    ', 'G  GG', 'G   G', ' GGG '],
                'H': ['H   H', 'H   H', 'HHHHH', 'H   H', 'H   H'],
                'I': ['IIIII', '  I  ', '  I  ', '  I  ', 'IIIII'],
                'J': ['JJJJJ', '   J ', '   J ', 'J  J ', ' JJ  '],
                'K': ['K   K', 'K  K ', 'KKK  ', 'K  K ', 'K   K'],
                'L': ['L    ', 'L    ', 'L    ', 'L    ', 'LLLLL'],
                'M': ['M   M', 'MM MM', 'M M M', 'M   M', 'M   M'],
                'N': ['N   N', 'NN  N', 'N N N', 'N  NN', 'N   N'],
                'O': [' OOO ', 'O   O', 'O   O', 'O   O', ' OOO '],
                'P': ['PPPP ', 'P   P', 'PPPP ', 'P    ', 'P    '],
                'Q': [' QQQ ', 'Q   Q', 'Q   Q', 'Q Q Q', ' QQQQ'],
                'R': ['RRRR ', 'R   R', 'RRRR ', 'R  R ', 'R   R'],
                'S': [' SSS ', 'S    ', ' SSS ', '    S', ' SSS '],
                'T': ['TTTTT', '  T  ', '  T  ', '  T  ', '  T  '],
                'U': ['U   U', 'U   U', 'U   U', 'U   U', ' UUU '],
                'V': ['V   V', 'V   V', 'V   V', ' V V ', '  V  '],
                'W': ['W   W', 'W   W', 'W W W', 'WW WW', 'W   W'],
                'X': ['X   X', ' X X ', '  X  ', ' X X ', 'X   X'],
                'Y': ['Y   Y', ' Y Y ', '  Y  ', '  Y  ', '  Y  '],
                'Z': ['ZZZZZ', '   Z ', '  Z  ', ' Z   ', 'ZZZZZ'],
                '0': [' 00  ', '0  0 ', '0  0 ', '0  0 ', ' 00  '],
                '1': [' 1   ', '11   ', ' 1   ', ' 1   ', '1111 '],
                '2': [' 22  ', '  2  ', ' 2   ', '2    ', '2222 '],
                '3': [' 33  ', '  3  ', ' 33  ', '  3  ', ' 33  '],
                '4': ['4  4 ', '4  4 ', '4444 ', '   4 ', '   4 '],
                '5': ['5555 ', '5    ', '5555 ', '    5', '5555 '],
                '6': [' 666 ', '6    ', '6666 ', '6  6 ', ' 666 '],
                '7': ['7777 ', '   7 ', '  7  ', ' 7   ', '7    '],
                '8': [' 88  ', '8  8 ', ' 88  ', '8  8 ', ' 88  '],
                '9': [' 999 ', '9  9 ', ' 999 ', '   9 ', ' 99  '],
                ' ': ['     ', '     ', '     ', '     ', '     '],
                '-': ['     ', '     ', ' --  ', '     ', '     '],
                '.': ['     ', '     ', '     ', '  .  ', '  .  '],
                '!': ['  !  ', '  !  ', '  !  ', '     ', '  !  '],
                '?': [' ??? ', '  ?  ', '  ?  ', '     ', '  ?  '],
            },
            'small': {
                'A': [' A ', 'A A', 'AAA', 'A A', 'A A'],
                'B': ['BB ', 'B B', 'BB ', 'B B', 'BB '],
                'C': [' C ', 'C  ', 'C  ', 'C  ', ' C '],
                'D': ['D D', 'D D', 'DDD', 'D D', 'D D'],
                'E': ['EEE', 'E ', 'EE ', 'E ', 'EEE'],
                'F': ['FFF', 'F ', 'FF ', 'F ', 'F '],
                'G': [' GG', 'G  ', 'G G', 'G G', ' GG'],
                'H': ['H H', 'H H', 'HHH', 'H H', 'H H'],
                'I': ['I', 'I', 'I', 'I', 'I'],
                'J': ['  J', '  J', '  J', 'J J', ' J '],
                'K': ['K K', 'KK ', 'K K', 'K K', 'K K'],
                'L': ['L  ', 'L  ', 'L  ', 'L  ', 'LLL'],
                'M': ['M M', 'MMM', 'M M', 'M M', 'M M'],
                'N': ['N N', 'NN N', 'N NN', 'N  N', 'N  N'],
                'O': [' O ', 'O O', 'O O', 'O O', ' O '],
                'P': ['PP ', 'P P', 'PP ', 'P  ', 'P  '],
                'Q': [' Q ', 'Q Q', ' Q ', '  Q', ' QQ'],
                'R': ['RR ', 'R R', 'RR ', 'R R', 'R R'],
                'S': ['SSS', 'S  ', ' S ', '  S', 'SSS'],
                'T': ['TTT', ' T ', ' T ', ' T ', ' T '],
                'U': ['U U', 'U U', 'U U', 'U U', ' UU'],
                'V': ['V V', 'V V', 'V V', ' V ', ' V '],
                'W': ['W W', 'W W', 'W W', 'WWW', 'W W'],
                'X': ['X X', ' X ', ' X ', ' X ', 'X X'],
                'Y': ['Y Y', ' Y ', ' Y ', ' Y ', ' Y '],
                'Z': ['ZZZ', ' Z ', ' Z ', ' Z ', 'ZZZ'],
                '0': ['0 0', '0 0', '0 0', '0 0', '0 0'],
                '1': [' 1 ', '11 ', ' 1 ', ' 1 ', '111'],
                '2': ['22 ', '  2', ' 2 ', '2  ', '222'],
                '3': ['33 ', '  3', ' 3 ', '  3', '33 '],
                '4': ['4 4', '4 4', '444', '  4', '  4'],
                '5': ['555', '5  ', '55 ', '  5', '55 '],
                '6': [' 66', '6  ', '66 ', '6 6', ' 66'],
                '7': ['777', '  7', ' 7 ', '7  ', '7  '],
                '8': [' 8 ', '8 8', ' 8 ', '8 8', ' 8 '],
                '9': [' 99', '9 9', ' 99', '  9', '99 '],
                ' ': [' ', ' ', ' ', ' ', ' '],
                '-': [' ', '-', ' ', '-', ' '],
                '.': [' ', ' ', ' ', ' ', '.'],
            },
        }
        
        font_data = fonts.get(font, fonts['big'])
        result_lines = [''] * 5 if font == 'big' else [''] * 5
        
        text = text.upper()
        
        for char in text:
            char_lines = font_data.get(char, font_data.get(' ', ['     '] * 5))
            for i in range(5):
                result_lines[i] += char_lines[i] + ' '
        
        return '\n'.join(line.rstrip() for line in result_lines)
    
    def save_to_file(self, ascii_art: str, filename: str) -> bool:
        """
        将ASCII艺术保存到文件
        
        Args:
            ascii_art: ASCII艺术字符串
            filename: 文件名
            
        Returns:
            是否成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ascii_art)
            return True
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return False
    
    def list_charsets(self) -> List[str]:
        """列出所有可用的字符集"""
        return list(self.CHARSETS.keys())


def demo():
    """演示函数"""
    print("🎨 ASCII艺术生成器演示")
    print("=" * 50)
    
    # 创建生成器
    generator = ASCIIArtGenerator(charset='detailed', width=60)
    
    # 演示文本转ASCII
    print("\n📝 文本转ASCII艺术:")
    print("-" * 50)
    ascii_title = generator.text_to_ascii("HELLO", font='big')
    print(ascii_title)
    
    print("\n" + "-" * 50)
    ascii_title2 = generator.text_to_ascii("AI", font='small')
    print(ascii_title2)
    
    # 演示字符集
    print("\n\n🎯 不同字符集效果:")
    print("-" * 50)
    
    test_pixel = 128  # 中间灰度值
    
    for charset_name, chars in generator.CHARSETS.items():
        char_len = len(chars)
        char_idx = int(test_pixel * (char_len - 1) / 255)
        print(f"{charset_name:10}: {chars[char_idx]}")
    
    # 图片转换演示
    print("\n\n🖼️ 图片转ASCII:")
    print("-" * 50)
    if PIL_AVAILABLE:
        print("✅ Pillow已安装，可以使用图片转换功能")
        print("📌 使用方法:")
        print("   generator = ASCIIArtGenerator()")
        print("   ascii_art = generator.image_to_ascii('path/to/image.jpg')")
    else:
        print("❌ Pillow未安装，图片功能不可用")
        print("💡 安装命令: pip install Pillow")
    
    print("\n\n📁 保存到文件:")
    print("-" * 50)
    test_art = generator.text_to_ascii("TEST")
    success = generator.save_to_file(test_art, 'test_ascii.txt')
    if success:
        print("✅ 已保存到 test_ascii.txt")
        # 读取并显示
        with open('test_ascii.txt', 'r') as f:
            print(f.read())
        # 清理测试文件
        os.remove('test_ascii.txt')
    
    print("\n\n✨ 演示完成！")
    print("📚 查看完整文档和更多功能，请阅读代码注释")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🎨 ASCII艺术生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -t "HELLO"           # 生成文本ASCII
  %(prog)s -t "AI" -f small     # 使用小字体
  %(prog)s -i image.jpg         # 图片转ASCII
  %(prog)s -l                   # 列出字符集
        """
    )
    
    parser.add_argument('-t', '--text', help='要转换的文本')
    parser.add_argument('-f', '--font', default='big', choices=['big', 'small'],
                        help='字体风格 (默认: big)')
    parser.add_argument('-i', '--image', help='图片路径')
    parser.add_argument('-w', '--width', type=int, default=100, help='输出宽度 (默认: 100)')
    parser.add_argument('-c', '--charset', default='detailed',
                        choices=ASCIIArtGenerator.CHARSETS.keys(),
                        help='字符集 (默认: detailed)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-l', '--list-charsets', action='store_true',
                        help='列出所有字符集')
    parser.add_argument('--invert', action='store_true', help='反转字符顺序')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = ASCIIArtGenerator(charset=args.charset, width=args.width)
    
    # 列出字符集
    if args.list_charsets:
        print("🎯 可用的字符集:")
        for charset in generator.list_charsets():
            print(f"  • {charset}")
        return
    
    # 运行演示
    if args.demo:
        demo()
        return
    
    # 生成ASCII艺术
    ascii_art = ""
    
    if args.text:
        ascii_art = generator.text_to_ascii(args.text, font=args.font)
    elif args.image:
        ascii_art = generator.image_to_ascii(args.image, invert=args.invert)
    else:
        # 默认运行演示
        demo()
        return
    
    # 输出结果
    if ascii_art:
        print(ascii_art)
        
        # 保存到文件
        if args.output:
            if generator.save_to_file(ascii_art, args.output):
                print(f"\n✅ 已保存到 {args.output}")


if __name__ == '__main__':
    main()
