#!/usr/bin/env python3
"""
🐍 Chinese Zodiac Year Calculator
Calculate zodiac sign and generate lucky messages for any year.
"""

ZODIAC_ANIMALS = [
    ("鼠", "Rat", "🐀"),
    ("牛", "Ox", "🐂"),
    ("虎", "Tiger", "🐅"),
    ("兔", "Rabbit", "🐇"),
    ("龙", "Dragon", "🐉"),
    ("蛇", "Snake", "🐍"),
    ("马", "Horse", "🐴"),
    ("羊", "Goat", "🐐"),
    ("猴", "Monkey", "🐒"),
    ("鸡", "Rooster", "🐓"),
    ("狗", "Dog", "🐕"),
    ("猪", "Pig", "🐖"),
]

ELEMENTS = ["金 (Metal)", "水 (Water)", "木 (Wood)", "火 (Fire)", "土 (Earth)"]

def get_zodiac(year: int) -> tuple:
    """Get zodiac animal for a given year."""
    index = (year - 4) % 12
    return ZODIAC_ANIMALS[index]

def get_element(year: int) -> str:
    """Get element for a given year (cycles every 2 years)."""
    index = ((year - 4) % 10) // 2
    return ELEMENTS[index]

def generate_blessing(zodiac: tuple, element: str) -> str:
    """Generate a New Year blessing."""
    cn, en, emoji = zodiac
    return f"""
{emoji} {cn}年大吉！Year of the {en}! {emoji}

🎊 Element: {element}
🧧 May this year bring you:
   • 福 (Fú) - Good Fortune
   • 禄 (Lù) - Prosperity  
   • 寿 (Shòu) - Longevity
   • 喜 (Xǐ) - Happiness

恭喜发财！🎆
"""

if __name__ == "__main__":
    year = 2026
    zodiac = get_zodiac(year)
    element = get_element(year)
    print(f"Year {year}:")
    print(generate_blessing(zodiac, element))
