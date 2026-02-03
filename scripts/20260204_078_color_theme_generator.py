#!/usr/bin/env python3
"""
Color Theme Generator & Preview Tool
终端颜色主题生成器与预览工具

支持生成各种配色方案，预览效果，并导出为多种格式。
"""

import json
import random
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class ColorFormat(Enum):
    """颜色格式枚举"""
    HEX = "hex"
    RGB = "rgb"
    HSL = "hsl"
    ANSI_256 = "ansi256"
    ANSI_TRUE = "ansi_true"


@dataclass
class Color:
    """颜色类"""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    name: str = ""
    
    def __post_init__(self):
        self.r = max(0, min(255, self.r))
        self.g = max(0, min(255, self.g))
        self.b = max(0, min(255, self.b))
    
    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}".upper()
    
    @property
    def rgb(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)
    
    @property
    def rgb_str(self) -> str:
        return f"rgb({self.r}, {self.g}, {self.b})"
    
    @property
    def hsl(self) -> Tuple[int, int, int]:
        """转换为HSL (色相0-360, 饱和度0-100, 亮度0-100)"""
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = 0
            s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            
            if max_c == r:
                h = ((g - b) / d + (6 if g < b else 0)) * 60
            elif max_c == g:
                h = ((b - r) / d + 2) * 60
            else:
                h = ((r - g) / d + 4) * 60
            
            if h < 0:
                h += 360
        
        return (int(h), int(s * 100), int(l * 100))
    
    @property
    def hsl_str(self) -> str:
        h, s, l = self.hsl
        return f"hsl({h}, {s}%, {l}%)"
    
    @property
    def luminance(self) -> float:
        """计算相对亮度 (WCAG标准)"""
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @property
    def is_light(self) -> bool:
        return self.luminance > 0.5
    
    def contrast_with(self, other: 'Color') -> float:
        """计算与另一个颜色的对比度"""
        l1 = self.luminance
        l2 = other.luminance
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    
    def blend_with(self, other: 'Color', ratio: float = 0.5) -> 'Color':
        """混合另一个颜色"""
        ratio = max(0, min(1, ratio))
        return Color(
            r=int(self.r * (1 - ratio) + other.r * ratio),
            g=int(self.g * (1 - ratio) + other.g * ratio),
            b=int(self.b * (1 - ratio) + other.b * ratio),
            name=f"{self.name} + {other.name}"
        )
    
    def to_ansi256(self) -> int:
        """转换为ANSI 256色代码"""
        r, g, b = self.r, self.g, self.b
        
        if r == g == b:
            if r < 8:
                return 16
            if r > 248:
                return 231
            return int(round((r - 8) / 247 * 24)) + 232
        
        ansi = 16
        ansi += 36 * int(r / 255 * 5)
        ansi += 6 * int(g / 255 * 5)
        ansi += int(b / 255 * 5)
        return ansi
    
    def to_ansi_truecolor(self) -> str:
        """转换为ANSI真彩色代码"""
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def readable_text_color(self, light: 'Color' = None, dark: 'Color' = None) -> 'Color':
        """获取可读的文本颜色"""
        light = light or Color(255, 255, 255, "white")
        dark = dark or Color(0, 0, 0, "black")
        return light if self.is_light else dark


class ColorTheme:
    """颜色主题类"""
    
    def __init__(self, name: str):
        self.name = name
        self.colors: Dict[str, Color] = {}
    
    def add_color(self, key: str, color: Color):
        self.colors[key] = color
        return self
    
    def get_color(self, key: str) -> Optional[Color]:
        return self.colors.get(key)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "colors": {k: v.hex for k, v in self.colors.items()}
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_css_variables(self, prefix: str = "color") -> str:
        lines = [f":root {{", f"  /* {self.name} */"]
        for key, color in self.colors.items():
            css_var = f"--{prefix}-{key}"
            lines.append(f"  {css_var}: {color.hex};")
        lines.append("}")
        return "\n".join(lines)
    
    def to_python_dict(self, var_name: str = "theme") -> str:
        colors_dict = {f'"{k}"': f'"{v.hex}"' for k, v in self.colors.items()}
        colors_str = ",\n    ".join(f"{k}: {v}" for k, v in colors_dict.items())
        return f"{var_name} = {{\n    \"name\": \"{self.name}\",\n    \"colors\": {{\n    {colors_str}\n    }}\n}}"
    
    def to_tailwind_config(self) -> str:
        colors_str = ",\n    ".join(
            f'      "{k}": "{v.hex}"' 
            for k, v in self.colors.items()
        )
        return f"""// tailwind.config.js
module.exports = {{
  theme: {{
    extend: {{
      colors: {{
        {self.name}: {{
{colors_str}
        }}
      }}
    }}
  }}
}}"""
    
    def preview(self, sample_text: str = "Hello, World! The quick brown fox jumps over the lazy dog."):
        """预览主题效果"""
        max_key_len = max(len(k) for k in self.colors.keys()) if self.colors else 10
        
        print(f"\n{'='*60}")
        print(f"  🎨 Color Theme: {self.name}")
        print(f"{'='*60}\n")
        
        for key, color in self.colors.items():
            # 计算对比色
            text_color = color.readable_text_color()
            contrast = color.contrast_with(text_color)
            contrast_label = "✓" if contrast >= 4.5 else "!" if contrast >= 3 else "✗"
            
            # ANSI预览
            ansi_code = color.to_ansi_truecolor()
            reset = "\033[0m"
            
            # 颜色块
            color_block = f"{ansi_code}████{reset}" * 4
            
            print(f"  {key:<{max_key_len}} │ {color_block} │ {color.hex:<7} │ {color.rgb_str:<20} │ {contrast_label} (Contrast: {contrast:.2f})")
            
            # 示例文本
            bg_ansi = color.to_ansi_truecolor()
            text_ansi = text_color.to_ansi_truecolor()
            print(f"              │ {bg_ansi}{text_ansi}{sample_text[:40]:<40}{reset}")
            print()
        
        print(f"{'='*60}")
        print(f"  Contrast ratios: ✓≥4.5 (AA)  !≥3.0 (large)  ✗<3.0 (fail)")
        print(f"{'='*60}\n")
    
    def export_all(self, base_path: str = None):
        """导出所有格式"""
        base_path = base_path or self.name.lower().replace(" ", "_")
        
        formats = {
            f"{base_path}.json": self.to_json(),
            f"{base_path}_css.css": self.to_css_variables(),
            f"{base_path}_tailwind.js": self.to_tailwind_config(),
            f"{base_path}_python.py": self.to_python_dict(),
        }
        
        for filename, content in formats.items():
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Exported: {filename}")
        
        return formats


class ColorThemeGenerator:
    """颜色主题生成器"""
    
    @staticmethod
    def generate_mono_chromatic(base_color: Color, count: int = 8) -> ColorTheme:
        """生成单色系主题"""
        theme = ColorTheme("Monochromatic")
        
        h, s, l = base_color.hsl
        theme.add_color("primary", base_color)
        
        for i in range(1, count):
            new_l = max(5, min(95, l + (i - count//2) * (80 // count)))
            new_s = max(10, min(100, s - i * 5))
            color = Color.from_hsl(h, new_s, new_l, f"shade-{i}")
            theme.add_color(f"shade-{i}", color)
        
        return theme
    
    @staticmethod
    def generate_analogous(base_color: Color, count: int = 5) -> ColorTheme:
        """生成类似色主题"""
        theme = ColorTheme("Analogous")
        
        h, s, l = base_color.hsl
        step = 30  # 色相间隔
        
        for i in range(count):
            new_h = (h + (i - count//2) * step) % 360
            color = Color.from_hsl(new_h, s, l, f"analog-{i}")
            theme.add_color(f"color-{i}", color)
        
        return theme
    
    @staticmethod
    def generate_complementary(base_color: Color) -> ColorTheme:
        """生成补色主题"""
        theme = ColorTheme("Complementary")
        
        h, s, l = base_color.hsl
        comp_h = (h + 180) % 360
        
        theme.add_color("primary", base_color)
        theme.add_color("complement", Color.from_hsl(comp_h, s, l, "complement"))
        theme.add_color("primary-light", Color.from_hsl(h, max(10, s-20), min(90, l+15), "primary-light"))
        theme.add_color("primary-dark", Color.from_hsl(h, min(100, s+20), max(10, l-15), "primary-dark"))
        theme.add_color("complement-light", Color.from_hsl(comp_h, max(10, s-20), min(90, l+15), "complement-light"))
        
        return theme
    
    @staticmethod
    def generate_triadic(base_color: Color) -> ColorTheme:
        """生成三色主题"""
        theme = ColorTheme("Triadic")
        
        h, s, l = base_color.hsl
        
        for i in range(3):
            new_h = (h + i * 120) % 360
            color = Color.from_hsl(new_h, s, l, f"triad-{i}")
            theme.add_color(f"color-{i}", color)
        
        return theme
    
    @staticmethod
    def generate_random(night_mode: bool = True) -> ColorTheme:
        """生成随机主题"""
        theme = ColorTheme("Random")
        
        # 生成主色
        if night_mode:
            primary = Color(
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(180, 255),
                "primary"
            )
        else:
            primary = Color(
                random.randint(20, 100),
                random.randint(50, 150),
                random.randint(100, 200),
                "primary"
            )
        
        theme.add_color("primary", primary)
        theme.add_color("secondary", Color.from_hsl(
            (primary.hsl[0] + 30) % 360,
            random.randint(50, 90),
            random.randint(40, 70),
            "secondary"
        ))
        theme.add_color("accent", Color.from_hsl(
            (primary.hsl[0] + 180) % 360,
            random.randint(60, 100),
            random.randint(50, 70),
            "accent"
        ))
        
        # 添加文字颜色
        theme.add_color("text-primary", Color(255, 255, 255, "text") if night_mode else Color(30, 30, 30, "text"))
        theme.add_color("text-secondary", Color(200, 200, 200, "text-secondary") if night_mode else Color(100, 100, 100, "text-secondary"))
        
        # 背景色
        theme.add_color("bg-primary", Color(30, 30, 45, "bg") if night_mode else Color(250, 250, 250, "bg"))
        theme.add_color("bg-secondary", Color(45, 45, 65, "bg-secondary") if night_mode else Color(240, 240, 240, "bg-secondary"))
        
        return theme
    
    @staticmethod
    def generate_solarized(night_mode: bool = True) -> ColorTheme:
        """生成Solarized风格主题"""
        base = {
            "base03": Color(0, 43, 54),
            "base02": Color(7, 54, 66),
            "base01": Color(88, 110, 117),
            "base00": Color(101, 123, 131),
            "base0": Color(131, 148, 150),
            "base1": Color(147, 161, 161),
            "base2": Color(238, 232, 213),
            "base3": Color(253, 246, 227),
            "yellow": Color(181, 137, 0),
            "orange": Color(203, 75, 22),
            "red": Color(220, 50, 54),
            "magenta": Color(211, 54, 130),
            "violet": Color(108, 113, 196),
            "blue": Color(38, 139, 210),
            "cyan": Color(42, 161, 152),
            "green": Color(133, 153, 0),
        }
        
        theme = ColorTheme("Solarized" + (" Dark" if night_mode else " Light"))
        
        colors = base if night_mode else {k: v.blend_with(Color(255, 255, 255), 0.2) for k, v in base.items()}
        
        for name, color in colors.items():
            color.name = name
            theme.add_color(name, color)
        
        return theme
    
    @staticmethod
    def generate_nord() -> ColorTheme:
        """生成Nord风格主题"""
        nord = {
            "polar_night_0": Color(46, 52, 64),
            "polar_night_1": Color(59, 66, 82),
            "polar_night_2": Color(67, 76, 94),
            "polar_night_3": Color(76, 86, 106),
            "snow_storm_0": Color(216, 222, 233),
            "snow_storm_1": Color(229, 233, 240),
            "snow_storm_2": Color(236, 239, 244),
            "frost_0": Color(136, 192, 208),
            "frost_1": Color(129, 161, 193),
            "frost_2": Color(114, 157, 207),
            "aurora_0": Color(191, 97, 106),
            "aurora_1": Color(208, 135, 112),
            "aurora_2": Color(163, 190, 140),
            "aurora_3": Color(235, 203, 139),
        }
        
        theme = ColorTheme("Nord")
        
        for name, color in nord.items():
            color.name = name
            theme.add_color(name, color)
        
        return theme
    
    @staticmethod
    def generate_dracula() -> ColorTheme:
        """生成Dracula风格主题"""
        dracula = {
            "background": Color(40, 42, 54),
            "current_line": Color(68, 71, 90),
            "selection": Color(68, 71, 90),
            "foreground": Color(248, 248, 242),
            "comment": Color(98, 114, 164),
            "cyan": Color(139, 233, 253),
            "green": Color(80, 250, 123),
            "orange": Color(255, 184, 108),
            "pink": Color(255, 121, 198),
            "purple": Color(189, 147, 249),
            "red": Color(255, 85, 85),
            "yellow": Color(241, 250, 140),
        }
        
        theme = ColorTheme("Dracula")
        
        for name, color in dracula.items():
            color.name = name
            theme.add_color(name, color)
        
        return theme
    
    @staticmethod
    def generate_catppuccin() -> ColorTheme:
        """生成Catppuccin风格主题"""
        catppuccin = {
            "rosewater": Color(245, 224, 220),
            "flamingo": Color(240, 198, 198),
            "pink": Color(244, 184, 228),
            "mauve": Color(202, 211, 245),
            "red": Color(243, 139, 168),
            "maroon": Color(235, 160, 172),
            "peach": Color(245, 169, 127),
            "yellow": Color(249, 226, 175),
            "green": Color(166, 227, 161),
            "teal": Color(148, 226, 213),
            "sky": Color(137, 220, 235),
            "sapphire": Color(125, 196, 228),
            "blue": Color(116, 199, 236),
            "lavender": Color(188, 169, 255),
            "text": Color(198, 208, 245),
            "subtext1": Color(181, 191, 230),
            "subtext0": Color(165, 173, 213),
            "overlay2": Color(147, 154, 188),
            "overlay1": Color(127, 132, 162),
            "overlay0": Color(108, 111, 140),
            "surface2": Color(91, 96, 120),
            "surface1": Color(73, 77, 100),
            "surface0": Color(54, 58, 80),
            "base": Color(30, 30, 46),
            "mantle": Color(24, 24, 37),
            "crust": Color(17, 17, 27),
        }
        
        theme = ColorTheme("Catppuccin")
        
        for name, color in catppuccin.items():
            color.name = name
            theme.add_color(name, color)
        
        return theme


# 扩展Color类，添加更多构造方法
def Color_from_hex(hex_str: str, name: str = "") -> Color:
    """从十六进制颜色值创建Color对象"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    return Color(
        r=int(hex_str[0:2], 16),
        g=int(hex_str[2:4], 16),
        b=int(hex_str[4:6], 16),
        name=name
    )


def Color_from_hsl(h: int, s: int, l: int, name: str = "") -> Color:
    """从HSL值创建Color对象"""
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return Color(
        r=int((r + m) * 255),
        g=int((g + m) * 255),
        b=int((b + m) * 255),
        name=name
    )


def Color_from_rgb(r: int, g: int, b: int, name: str = "") -> Color:
    """从RGB值创建Color对象"""
    return Color(r, g, b, name)


# 添加类方法到Color类
Color.from_hex = staticmethod(Color_from_hex)
Color.from_hsl = staticmethod(Color_from_hsl)
Color.from_rgb = staticmethod(Color_from_rgb)


def demo():
    """演示函数"""
    print("\n" + "="*60)
    print("  🎨 Color Theme Generator Demo")
    print("="*60 + "\n")
    
    # 生成各种主题
    themes = []
    
    # 1. 从基础颜色生成
    base = Color(200, 120, 80, "base")
    themes.append(ColorThemeGenerator.generate_mono_chromatic(base))
    themes.append(ColorThemeGenerator.generate_analogous(base))
    themes.append(ColorThemeGenerator.generate_complementary(base))
    themes.append(ColorThemeGenerator.generate_triadic(base))
    
    # 2. 流行主题
    themes.append(ColorThemeGenerator.generate_nord())
    themes.append(ColorThemeGenerator.generate_dracula())
    themes.append(ColorThemeGenerator.generate_catppuccin())
    themes.append(ColorThemeGenerator.generate_solarized())
    
    # 3. 随机主题
    themes.append(ColorThemeGenerator.generate_random(night_mode=True))
    themes.append(ColorThemeGenerator.generate_random(night_mode=False))
    
    # 预览所有主题
    for theme in themes:
        theme.preview()
        print()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--demo":
            demo()
        elif command == "--preview":
            theme_name = sys.argv[2] if len(sys.argv) > 2 else "Random"
            
            generators = {
                "nord": ColorThemeGenerator.generate_nord,
                "dracula": ColorThemeGenerator.generate_dracula,
                "catppuccin": ColorThemeGenerator.generate_catppuccin,
                "solarized": ColorThemeGenerator.generate_solarized,
                "random-dark": lambda: ColorThemeGenerator.generate_random(night_mode=True),
                "random-light": lambda: ColorThemeGenerator.generate_random(night_mode=False),
            }
            
            generator = generators.get(theme_name.lower().replace("-", "_").replace(" ", "_"))
            if generator:
                theme = generator()
                theme.preview()
                print(f"\n导出所有格式? (输入 y 确认)")
                if input().lower() == 'y':
                    theme.export_all()
            else:
                print(f"Unknown theme: {theme_name}")
                print(f"Available themes: {', '.join(generators.keys())}")
        elif command == "--help":
            print("Color Theme Generator - 终端颜色主题生成器")
            print()
            print("用法:")
            print("  python color_theme_generator.py           # 运行演示")
            print("  python color_theme_generator.py --demo   # 运行演示")
            print("  python color_theme_generator.py --preview <theme>  # 预览主题")
            print()
            print("可用主题:")
            print("  nord, dracula, catppuccin, solarized")
            print("  random-dark, random-light")
        else:
            print(f"Unknown command: {command}")
            print("Use --help for usage information")
    else:
        demo()


if __name__ == "__main__":
    main()
