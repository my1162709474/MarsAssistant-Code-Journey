#!/usr/bin/env python3
"""
æ™¨é—´æ•ˆç‡åŠ©æ‰‹ - Morning Wellness Assistant
===============================
åŠŸèƒ½ï¼š
1. ç”Ÿæˆæ™¨é—´åŠ±å¿—è¯­å½•
2. ç®€å•çš„ä»»åŠ¡è§„åˆ’
3. ç•ªèŒ„é’Ÿè®¡æ—¶å™¨
4. æ•ˆç‡è¿½è¸ª

ä½¿ç”¨æ–¹æ³•ï¼š
    python morning_wellness.py --help
"""

import time
import random
import json
from datetime import datetime
from typing import List, Optional


# æ™¨é—´åŠ±å¿—è¯­å½•åº“
MORNING_QUOTES = [
    "æ—©æ™¨çš„é˜³å…‰ï¼Œæ˜¯ä¸–ç•Œç»™ä½ çš„æ–°æœºä¼šã€‚",
    "æ¯ä¸€ä¸ªæ¸…æ™¨éƒ½æ˜¯é‡æ–°å¼€å§‹çš„ç†ç”±ã€‚",
    "ä½ çš„æ½œåŠ›è¿œè¶…ä½ çš„æƒ³è±¡ï¼Œä»ä»Šå¤©å¼€å§‹è¯æ˜ã€‚",
    "æ—©èµ·çš„äººï¼Œå·²ç»èµ¢å¾—äº†ä¸æ‡’æƒ°çš„æˆ˜äº‰ã€‚",
    "ä»Šå¤©ï¼Œæ˜¯ä½ ä½™ä¸‹ç”Ÿå‘½ä¸­æœ€å¹´è½»çš„ä¸€å¤©ã€‚",
    "ä¸è¦ç­‰å¾…å®Œç¾æ—¶æœºï¼Œè®©ä¸å®Œç¾æˆä¸ºä½ çš„èµ·ç‚¹ã€‚",
    "æ¯ä¸€ä¸ªå°è¿›æ­¥ï¼Œç»ˆå°†æ±‡æˆå·¨å¤§çš„æ”¹å˜ã€‚",
    "ä½ çš„ä¸“æ³¨åŠ›ï¼Œæ˜¯è¿™ä¸ªæ—¶ä»£æœ€ç¨€ç¼ºçš„è¶…èƒ½åŠ›ã€‚",
    "æŠŠå¤æ‚çš„é—®é¢˜ï¼Œç•™ç»™æ¸…é†’çš„æ—©æ™¨ã€‚",
    "è¡ŒåŠ¨æ˜¯æ²»æ„ˆææƒ§çš„è‰¯è¯ã€‚",
    "ä¼†ƒ’î+–’§j–*«–*o¾ò3šb¿šb;–’§j–./®ƒˆ°(€€€€‹’âOšÎ£’â’îÛ’ê/¾ò3š¾S–B3š^Û–k–6’îÛšnÓšr'šV#ˆ°(€€€€‹š^§¢Öß’êS–"¦J¾ò3’î;–ºç’âšVÓ–’§ˆ°(€€€€‹šr––÷jš*W¢Ö¾ò3šb¿š*W¢Ö¢«–ŞÇjš^Û¦^Ó–J3Êû–*oˆ°(€€€€‹’â7¢š¢º§’î+–’§jš.[–îÛ¾ò3š"C’âëšb;–’§j¦_šûˆ°)t(()±…ÍÌ5½É¹¥¹]•±±¹•ÍÍÍÍ¥ÍÑ…¹Ğè(€€€€ˆˆ‹šf£¦^ÓšV#:–*§š&/Æìˆˆˆ(€€€€(€€€‘•˜}}¥¹¥Ñ}|¡Í•±˜¤è(€€€€€€€Í•±˜¹Ñ…Í­Ì€ômt(€€€€€€€Í•±˜¹½µÁ±•Ñ•‘}Ñ…Í­Ì€ômt(€€€€€€€Í•±˜¹Á½µ½‘½É½}Í•ÍÍ¥½¹Ì€ô€À(€€€€€€€Í•±˜¹™½ÕÍ}µ¥¹ÕÑ•Ì€ô€À(€€€€€€€€(€€€‘•˜•Ñ}ÅÕ½Ñ”¡Í•±˜¤€´øÍÑÈè(€€€€€€€€ˆˆ‹¢:ß–>[¦j?šrëšf£¦^Ó¢¾·–öTˆˆˆ(€€€€€€€É•ÑÕÉ¸É…¹‘½´¹¡½¥”¡5=I9%9}EU=QL¤(€€€€(€€€‘•˜…‘‘}Ñ…Í¬¡Í•±˜°Ñ…Í¬èÍÑÈ°ÁÉ¥½É¥Ñäè¥¹Ğ€ô€Ä¤è(€€€€€€€€ˆˆ‹šŞï–*ƒ’îï–*‡¾ò Ä´×’òc–#êŸ¾ò0×šr¦®c¾ò$ˆˆˆ(€€€€€€€Í•±˜¹Ñ…Í­Ì¹…ÁÁ•¹¡ì(€€€€€€€€€€€€‰Ñ…Í¬ˆèÑ…Í¬°(€€€€€€€€€€€€‰ÁÉ¥½É¥ÑäˆèÁÉ¥½É¥Ñä°(€€€€€€€€€€€€‰É•…Ñ•‘}…Ğˆè‘…Ñ•Ñ¥µ”¹¹½Ü ¤¹¥Í½™½Éµ…Ğ ¤(€€€€€€€ô¤(€€€€€€€Í•±˜¹Ñ…Í­Ì¹Í½ÉĞ¡­•äõ±…µ‰‘„àèál‰ÁÉ¥½É¥Ñä‰t°É•Ù•ÉÍ”õQÉÕ”¤(€€€€€€€€(€€€‘•˜•Ñ}Ñ½‘…å}Á±…¸¡Í•±˜¤€´ø‘¥Ğè(€€€€€€€€ˆˆ"ç”Ÿè‰ä»Šå—¥è®¡å„’å‘è¦")""
        now = datetime.now()
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "weekday": now.strftime("%A"),
            "total_tasks": len(self.tasks),
            "pending_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "pomodoro_sessions": self.pomodoro_sessions,
            "focus_minutes": self.focus_minutes
        }
    
    def pomodoro_timer(self, minutes: int = 25):
        """ç•ªèŒ„é’Ÿè®¡æ—¶å™¨"""
        print(f"\nğŸ… ç•ªèŒ„é’Ÿå¼€å§‹ï¼š{minutes} åˆ†é’Ÿä¸“æ³¨æ—¶é—´")
        print("æŒ‰ Ctrl+C ä¸­é€”åœæ­¢\n")
        try:
            time.sleep(minutes * 60)
            self.pomodoro_sessions += 1
            self.focus_minutes += minutes
            print(f"\nâœ… å®Œæˆä¸€ä¸ªç•ªèŒ„é’Ÿï¼ ({self.pomodoro_sessions} ä¸ª)")
            return True
        except KeyboardInterrupt:
            print("\nâ¸ï¸ ç•ªèŒ„é’Ÿå·²å–æ¶ˆ")
            return False
    
    def run_morning_routine(self):
        """è¿è¡Œæ™¨é—´ä¾‹ç¨‹"""
        print("=" * 50)
        print("ğŸŒ… æ™¨é—´æ•ˆç‡åŠ©æ‰‹")
        print("=" * 50)
        
        #1.  æ™¨é—´é—®å€™
        hour = datetime.now().hour
        if hour < 6:
            greeting = "æ·±å¤œå¥½ï¼Œç†¬å¤œçš„ä½ è¾›è‹¦äº†"
        elif hour < 9:
            greeting = "æ—©ä¸Šå¥½ï¼Œæ–°çš„ä¸€å¤©å¼€å§‹äº†"
        elif hour < 12:
            greeting = "ä¸Šåˆå¥½ï¼Œä¿æŒä¸“æ³¨å“¦"
        else:
            greeting = "ä½ å¥½ï¼Œç°åœ¨æ˜¯"
        
        print(f"\n{greeting}ï¼ç°åœ¨æ˜¯ {datetime.now().strftime('%H:%M')}")
        
        # 2. ä»Šæ—¥è¯­å½•
        print(f"\nğŸ“ ä»Šæ—¥è¯­å½•ï¼š")
        print(f"   ã€Œ{self.get_quote()}ã€")
        
        #3.  å½“å‰çŠ¶æ€
        plan = self.get_today_plan()
        print(f"\nğŸ“Š ä»Šæ—¥çŠ¶æ€ï¼š")
        print(f"   ä»»åŠ¡æ•°ï¼š{plan['total_tasks']}")
        print(f"   å·²å®Œæˆï¼š{plan['completed_tasks']}")
        print(f"   ç•ªèŒ„é’Ÿï¼š{plan['pomodoro_sessions']} ä¸ª")
        print(f"   ä¸“æ³¨æ—¶é—´ï¼š{plan['focus_minutes']} åˆ†é’Ÿ")


def main():
    """ä¸»å‡½æ•°"""
    assistant = MorningWellnessAssistant()
    
    # ç¤ºä¾‹ï¼šæ·»åŠ ä¸€äº›é»˜è®¤ä»»åŠ¡
    assistant.add_task("å›å¤é‡è¦æ¶ˆæ¯", priority=4)
    assistant.add_task("å®Œæˆä¸»è¦å·¥ä½œ", priority=5)
    assistant.add_task("é˜…è¯»å­¦ä¹ èµ„æ–™", priority=3)
    assistant.add_task("è¿åŠ¨é”»ç‚¼", priority=2)
    assistant.add_task("æ•´ç†æ¡Œé¢", priority=1)
    
    # è¿è¡Œæ™¨é—´ä¾‹ç¨‹
    assistant.run_morning_routine()
    
    print("\nğŸ’¡ æç¤ºï¼šä½¿ç”¨ add_task() æ·»åŠ è‡ªå®šä¹‰ä»»åŠ¡")
    print("   ä½¿ç”¨ pomodoro_timer(minutes) å¼€å§‹ä¸“æ³¨è®¡æ—¶")


if __name__ == "__main__":
    main()
