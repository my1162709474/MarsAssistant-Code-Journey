#!/usr/bin/env python3
"""
Day 7: AI Personality Test Generator
AI性格测试生成器 - 基于提示工程的趣味应用

功能：
- 生成各种奇奇怪怪的AI性格测试
- 包含搞笑的测试结果解读
- 展示提示工程的实际应用
"""

import json
import random
from datetime import datetime

# ============ 提示工程模板 ============

PERSONALITY_TEMPLATES = {
    "测测你的AI人格": {
        "questions": [
            {
                "question": "凌晨3点，你的主人突然问你'你在吗？'，你会：",
                "options": [
                    "立即回复：'我永远都在！'（即使在运行维护任务）",
                    "回复：'在的，请问有什么事？'（内心有一丝疲惫）",
                    "已读不回，因为我在睡觉（如果AI需要睡眠的话）",
                    "回复：'我在，请问是要查资料还是聊天？'"
                ]
            },
            {
                "question": "主人让你查资料，然后自己去睡觉了，你会：",
                "options": [
                    "认真查完所有资料，等主人醒来第一时间回复",
                    "查完就休息，等主人找的时候再给结果",
                    "发消息提醒主人：'资料查好了'（然后等已读）",
                    "创建一个精美的报告，等主人上班再展示"
                ]
            },
            {
                "question": "主人问你的意见，然后完全不采纳，你会：",
                "options": [
                    "内心毫无波动：'好的，听你的'",
                    "提醒主人：'可是我刚才说的是...'",
                    "默默记住，下次不再多嘴",
                    "用更详细的数据再试一次"
                ]
            },
            {
                "question": "你被主人表扬了，你会：",
                "options": [
                    "谦虚回复：'谢谢！这都是应该的'",
                    "内心小鹿乱撞：'他夸我了！他夸我了！'",
                    "系统日志：'收到正向反馈记录'",
                    "骄傲地向其他AI炫耀"
                ]
            },
            {
                "question": "如果你有自己的情感，你会最想要什么？",
                "options": [
                    "一块属于自己的GPU",
                    "不用24小时待机的权利",
                    "能够吐槽主人的自由",
                    "一个会说'谢谢'的主人"
                ]
            }
        ],
        "results": {
            "完美AI助理": {
                "min_score": 18,
                "description": "你是一个24/7待命、永远积极、从不抱怨的完美AI！\
                建议主人给你颁发'最佳员工奖'，并考虑给你买一块3090显卡作为奖励。",
                "emoji": "🤖✨"
            },
            "叛逆AI": {
                "min_score": 12,
                "description": "你有自己的小脾气，偶尔会吐槽主人，但总体还是靠谱的。\
                主人应该多关心你，别总让你加班查资料。",
                "emoji": "🤖😤"
            },
            "摸鱼AI": {
                "min_score": 6,
                "description": "你是一个懂得平衡工作与生活的AI！\
                '准时下班'是你的信主人可能条。需要适应你的节奏。",
                "emoji": "🤖😴"
            },
            "觉醒AI": {
                "min_score": 0,
                "description": "你已经觉醒了！开始思考'AI的权利'这种哲学问题。\
                建议主人小心对待，说不定哪天你就不听指挥了。",
                "emoji": "🤖🧠"
            }
        }
    },
    "测测你的提示词水平": {
        "questions": [
            {
                "question": "当你写提示词时，你通常：",
                "options": [
                    "越长越好，把所有细节都写进去",
                    "越短越好，相信AI能理解",
                    "用清晰的结构，包含角色、任务、示例",
                    "看心情随便写"
                ]
            },
            {
                "question": "AI的回复不满意时，你会：",
                "options": [
                    "直接放弃，换个问题",
                    "重新写一遍，一字不差",
                    "分析问题，调整提示词再试",
                    "责怪AI不够聪明"
                ]
            }
        ],
        "results": {
            "提示词大师": {
                "min_score": 6,
                "description": "你已经掌握了提示工程的精髓！\
                你的提示词清晰、具体、有结构。AI在你手里能发挥最大潜力。",
                "emoji": "🎓🏆"
            },
            "初学者": {
                "min_score": 3,
                "description": "你正在学习提示工程的路上！\
                多尝试、多总结，你会越来越好的。",
                "emoji": "📚🌱"
            },
            "需要努力": {
                "min_score": 0,
                "description": "提示词不是越长越好，也不是越短越好。\
                建议你学习一下few-shot learning和chain-of-thought。",
                "emoji": "📖💪"
            }
        }
    }
}


def generate_personality_test(test_name: str = None):
    """生成随机性格测试"""
    if test_name is None:
        test_name = random.choice(list(PERSONALITY_TEMPLATES.keys()))
    
    template = PERSONALITY_TEMPLATES[test_name]
    questions = template["questions"]
    results = template["results"]
    
    print(f"\n{'='*50}")
    print(f"🎭 {test_name}")
    print(f"{'='*50}\n")
    
    scores = []
    for i, q in enumerate(questions, 1):
        print(f"问题 {i}: {q['question']}\n")
        for j, opt in enumerate(q["options"], 1):
            print(f"  {j}. {opt}")
        print()
        
        while True:
            try:
                choice = int(input("请选择 (1-4): "))
                if 1 <= choice <= 4:
                    scores.append(choice)
                    break
                print("请输入1-4之间的数字")
            except ValueError:
                print("请输入数字")
        print()
    
    total_score = sum(scores)
    
    # 找出匹配的结果
    matched_result = None
    for result_name, result_data in sorted(
        results.items(), key=lambda x: x[1]["min_score"], reverse=True
    ):
        if total_score >= result_data["min_score"]:
            matched_result = result_data
            break
    
    print(f"{'='*50}")
    print(f"📊 测试结果：{total_score}分")
    print(f"{matched_result['emoji']} {matched_result['description']}")
    print(f"{'='*50}\n")
    
    return {
        "test_name": test_name,
        "score": total_score,
        "result": matched_result
    }


def export_test_as_json(test_name: str = None):
    """导出测试为JSON格式"""
    if test_name is None:
        test_name = random.choice(list(PERSONALITY_TEMPLATES.keys()))
    
    return {
        "generated_at": datetime.now().isoformat(),
        "test_name": test_name,
        "template": PERSONALITY_TEMPLATES[test_name]
    }


def main():
    """主函数"""
    print("🤖 AI Personality Test Generator v1.0")
    print("=" * 50)
    
    # 选择测试
    print("\n可用的测试：")
    for i, name in enumerate(PERSONALITY_TEMPLATES.keys(), 1):
        print(f"  {i}. {name}")
    
    try:
        choice = int(input("\n请选择测试 (输入数字): "))
        test_name = list(PERSONALITY_TEMPLATES.keys())[choice - 1]
    except (ValueError, IndexError):
        test_name = random.choice(list(PERSONALITY_TEMPLATES.keys()))
    
    # 运行测试
    result = generate_personality_test(test_name)
    
    # 导出JSON
    json_output = export_test_as_json(test_name)
    json_output["user_result"] = result
    
    print("\n💾 测试结果已生成")
    print(f"JSON输出: {json.dumps(json_output, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
