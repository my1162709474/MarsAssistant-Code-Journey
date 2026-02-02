#!/usr/bin/env python3
"""
Interactive CLI Learning Quiz
交互式命令行测验学习工具

功能:
- 支持多种题型（单选、多选、判断、填空、编程）
- 随机抽题、错题复习、进度追踪
- 支持JSON/YAML格式的题库
- 命令行交互界面

使用方式:
    python interactive_quiz.py                    # 交互模式
    python interactive_quiz.py --quiz math        # 指定题库
    python interactive_quiz.py --review           # 错题复习模式
    python interactive_quiz.py --add quiz.json    # 添加新题库
"""

import json
import yaml
import random
import os
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class QuestionType(Enum):
    SINGLE_CHOICE = "single"      # 单选题
    MULTIPLE_CHOICE = "multiple"  # 多选题
    TRUE_FALSE = "true_false"     # 判断题
    FILL_BLANK = "fill_blank"     # 填空题
    PROGRAMMING = "programming"   # 编程题


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class Option:
    """选择题选项"""
    label: str          # 选项标签 (A, B, C, D)
    text: str           # 选项内容
    is_correct: bool    # 是否正确


@dataclass
class Question:
    """题目"""
    qid: str                    # 题目ID
    question_type: QuestionType  # 题目类型
    question: str               # 题干
    options: List[Option] = field(default_factory=list)  # 选项（选择/判断题）
    answer: str = ""            # 答案（填空/编程题）
    explanation: str = ""       # 解析
    difficulty: Difficulty = Difficulty.EASY  # 难度
    tags: List[str] = field(default_factory=list)  # 标签
    hint: str = ""              # 提示
    code_template: str = ""     # 编程题代码模板


@dataclass
class QuizResult:
    """测验结果"""
    total_questions: int
    correct_answers: int
    wrong_questions: List[Question]
    time_spent: float          # 用时（秒）
    score: float               # 得分
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class QuizStats:
    """学习统计"""
    total_quizzes: int = 0
    total_questions: int = 0
    correct_answers: int = 0
    wrong_question_ids: List[str] = field(default_factory=list)
    topic_stats: Dict[str, Dict] = field(default_factory=dict)
    streak_days: int = 0
    last_quiz_date: Optional[datetime] = None
    
    @property
    def accuracy(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return self.correct_answers / self.total_questions * 100


class QuestionBank:
    """题库管理"""
    
    def __init__(self, bank_dir: str = "question_banks"):
        self.bank_dir = Path(bank_dir)
        self.bank_dir.mkdir(exist_ok=True)
        self.banks: Dict[str, List[Question]] = {}
        self.load_all_banks()
    
    def load_all_banks(self):
        """加载所有题库"""
        for file_path in self.bank_dir.glob("*.json"):
            self.load_bank(file_path.stem)
        for file_path in self.bank_dir.glob("*.yaml"):
            self.load_bank(file_path.stem)
    
    def load_bank(self, bank_name: str) -> List[Question]:
        """加载指定题库"""
        questions = []
        
        # 尝试JSON格式
        json_path = self.bank_dir / f"{bank_name}.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions = self._parse_questions(data)
        
        # 尝试YAML格式
        yaml_path = self.bank_dir / f"{bank_name}.yaml"
        if yaml_path.exists() and not questions:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                questions = self._parse_questions(data)
        
        self.banks[bank_name] = questions
        return questions
    
    def _parse_questions(self, data: Any) -> List[Question]:
        """解析题目数据"""
        questions = []
        
        if isinstance(data, dict) and 'questions' in data:
            data = data['questions']
        
        for item in data:
            qtype = QuestionType(item.get('type', 'single'))
            
            options = []
            if 'options' in item:
                for opt in item['options']:
                    options.append(Option(
                        label=opt.get('label', 'A'),
                        text=opt.get('text', ''),
                        is_correct=opt.get('is_correct', False)
                    ))
            
            difficulty = Difficulty.EASY
            diff_map = {'easy': 1, 'medium': 2, 'hard': 3}
            if isinstance(item.get('difficulty'), str):
                difficulty = Difficulty(diff_map.get(item['difficulty'].lower(), 1))
            elif isinstance(item.get('difficulty'), int):
                difficulty = Difficulty(item['difficulty'])
            
            questions.append(Question(
                qid=item.get('id', f"q_{len(questions)+1}"),
                question_type=qtype,
                question=item.get('question', ''),
                options=options,
                answer=item.get('answer', ''),
                explanation=item.get('explanation', ''),
                difficulty=difficulty,
                tags=item.get('tags', []),
                hint=item.get('hint', ''),
                code_template=item.get('code_template', '')
            ))
        
        return questions
    
    def get_questions(self, bank_name: str, count: int = 10, 
                      difficulty: Optional[Difficulty] = None,
                      tags: Optional[List[str]] = None) -> List[Question]:
        """获取题目"""
        questions = self.banks.get(bank_name, [])
        
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        
        if tags:
            questions = [q for q in questions if any(tag in q.tags for tag in tags)]
        
        if count > 0:
            questions = random.sample(questions, min(count, len(questions)))
        
        return questions
    
    def create_sample_bank(self):
        """创建示例题库"""
        sample_data = {
            "name": "Python基础测试",
            "description": "Python编程基础知识和语法测试",
            "questions": [
                {
                    "id": "py_001",
                    "type": "single",
                    "question": "Python中用于输出内容的函数是？",
                    "options": [
                        {"label": "A", "text": "echo()", "is_correct": False},
                        {"label": "B", "text": "print()", "is_correct": True},
                        {"label": "C", "text": "output()", "is_correct": False},
                        {"label": "D", "text": "write()", "is_correct": False}
                    ],
                    "explanation": "print()是Python内置的输出函数，用于将内容打印到标准输出。",
                    "difficulty": "easy",
                    "tags": ["python", "基础", "函数"]
                },
                {
                    "id": "py_002",
                    "type": "single",
                    "question": "以下哪个是Python的不可变数据类型？",
                    "options": [
                        {"label": "A", "text": "list（列表）", "is_correct": False},
                        {"label": "B", "text": "dict（字典）", "is_correct": False},
                        {"label": "C", "text": "tuple（元组）", "is_correct": True},
                        {"label": "D", "text": "set（集合）", "is_correct": False}
                    ],
                    "explanation": "tuple（元组）是Python中的不可变序列，创建后不能修改。",
                    "difficulty": "easy",
                    "tags": ["python", "数据类型"]
                },
                {
                    "id": "py_003",
                    "type": "multiple",
                    "question": "Python中哪些是合法的变量名？（多选）",
                    "options": [
                        {"label": "A", "text": "variable", "is_correct": True},
                        {"label": "B", "text": "_private", "is_correct": True},
                        {"label": "C", "text": "2nd_value", "is_correct": False},
                        {"label": "D", "text": "class", "is_correct": False},
                        {"label": "E", "text": "myVar123", "is_correct": True}
                    ],
                    "explanation": "变量名必须以字母或下划线开头，不能使用Python关键字。",
                    "difficulty": "easy",
                    "tags": ["python", "变量"]
                },
                {
                    "id": "py_004",
                    "type": "true_false",
                    "question": "Python中的range()函数返回一个列表。",
                    "options": [
                        {"label": "A", "text": "正确", "is_correct": False},
                        {"label": "B", "text": "错误", "is_correct": True}
                    ],
                    "explanation": "range()返回一个range对象（可迭代对象），不是列表。使用list()可以将其转换为列表。",
                    "difficulty": "easy",
                    "tags": ["python", "函数"]
                },
                {
                    "id": "py_005",
                    "type": "fill_blank",
                    "question": "Python中使用_____关键字来定义函数。",
                    "answer": "def",
                    "explanation": "def是Python中用于定义函数的关键字。",
                    "difficulty": "easy",
                    "tags": ["python", "函数"]
                },
                {
                    "id": "py_006",
                    "type": "single",
                    "question": "列表推导式 [x*2 for x in range(5)] 的结果是？",
                    "options": [
                        {"label": "A", "text": "[0, 2, 4, 6, 8]", "is_correct": True},
                        {"label": "B", "text": "[0, 1, 2, 3, 4]", "is_correct": False},
                        {"label": "C", "text": "[2, 4, 6, 8, 10]", "is_correct": False},
                        {"label": "D", "text": "[1, 2, 3, 4, 5]", "is_correct": False}
                    ],
                    "explanation": "range(5)生成[0,1,2,3,4]，每个元素乘以2后得到[0,2,4,6,8]。",
                    "difficulty": "medium",
                    "tags": ["python", "列表推导式"]
                },
                {
                    "id": "py_007",
                    "type": "single",
                    "question": "以下哪个不是Python的异常处理关键字？",
                    "options": [
                        {"label": "A", "text": "try", "is_correct": False},
                        {"label": "B", "text": "except", "is_correct": False},
                        {"label": "C", "text": "catch", "is_correct": True},
                        {"label": "D", "text": "finally", "is_correct": False}
                    ],
                    "explanation": "Python使用try/except/finally进行异常处理，没有catch关键字（C++/Java使用catch）。",
                    "difficulty": "easy",
                    "tags": ["python", "异常处理"]
                },
                {
                    "id": "py_008",
                    "type": "multiple",
                    "question": "关于Python装饰器，以下说法正确的是？（多选）",
                    "options": [
                        {"label": "A", "text": "装饰器本质上是一个函数", "is_correct": True},
                        {"label": "B", "text": "使用@符号应用装饰器", "is_correct": True},
                        {"label": "C", "text": "装饰器会替换原函数", "is_correct": False},
                        {"label": "D", "text": "一个函数可以应用多个装饰器", "is_correct": True}
                    ],
                    "explanation": "装饰器接收一个函数并返回一个新函数，不会替换原函数（只是在外部包装）。",
                    "difficulty": "hard",
                    "tags": ["python", "装饰器", "进阶"]
                },
                {
                    "id": "py_009",
                    "type": "programming",
                    "question": "编写一个函数，检查字符串是否为回文（正读反读都一样）。",
                    "answer": "def is_palindrome(s): return s == s[::-1]",
                    "code_template": "def is_palindrome(s):\n    # 请在此处实现代码\n    pass",
                    "explanation": "使用切片s[::-1]可以反转字符串，然后比较是否相等。",
                    "difficulty": "medium",
                    "tags": ["python", "编程题", "字符串"]
                },
                {
                    "id": "py_010",
                    "type": "single",
                    "question": "PEP 8是什么？",
                    "options": [
                        {"label": "A", "text": "Python的版本号", "is_correct": False},
                        {"label": "B", "text": "Python代码风格指南", "is_correct": True},
                        {"label": "C", "text": "Python的安装程序", "is_correct": False},
                        {"label": "D", "text": "Python的调试工具", "is_correct": False}
                    ],
                    "explanation": "PEP 8是Python的代码风格指南，提供了编写Python代码的约定和建议。",
                    "difficulty": "easy",
                    "tags": ["python", "编码规范"]
                }
            ]
        }
        
        bank_path = self.bank_dir / "python_basics.json"
        with open(bank_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 示例题库已创建: {bank_path}")
        return self.load_bank(bank_path.stem)


class QuizEngine:
    """测验引擎"""
    
    def __init__(self, stats_file: str = "quiz_stats.json"):
        self.stats = self.load_stats(stats_file)
        self.stats_file = stats_file
    
    def load_stats(self, filename: str) -> QuizStats:
        """加载统计信息"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats = QuizStats(
                    total_quizzes=data.get('total_quizzes', 0),
                    total_questions=data.get('total_questions', 0),
                    correct_answers=data.get('correct_answers', 0),
                    wrong_question_ids=data.get('wrong_question_ids', []),
                    topic_stats=data.get('topic_stats', {}),
                    streak_days=data.get('streak_days', 0)
                )
                if data.get('last_quiz_date'):
                    stats.last_quiz_date = datetime.fromisoformat(data['last_quiz_date'])
                return stats
        return QuizStats()
    
    def save_stats(self):
        """保存统计信息"""
        data = {
            'total_quizzes': self.stats.total_quizzes,
            'total_questions': self.stats.total_questions,
            'correct_answers': self.stats.correct_answers,
            'wrong_question_ids': self.stats.wrong_question_ids,
            'topic_stats': self.stats.topic_stats,
            'streak_days': self.stats.streak_days,
            'last_quiz_date': self.stats.last_quiz_date.isoformat() if self.stats.last_quiz_date else None
        }
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def start_quiz(self, questions: List[Question], show_hint: bool = False) -> QuizResult:
        """开始测验"""
        if not questions:
            print("❌ 没有可用的题目！")
            return None
        
        print(f"\n{'='*60}")
        print(f"📝 测验开始！共 {len(questions)} 道题")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        wrong_questions = []
        correct_count = 0
        
        for i, q in enumerate(questions, 1):
            if self._ask_question(q, i, len(questions), show_hint):
                correct_count += 1
            else:
                wrong_questions.append(q)
            
            print()
        
        end_time = time.time()
        time_spent = end_time - start_time
        score = correct_count / len(questions) * 100 if questions else 0
        
        result = QuizResult(
            total_questions=len(questions),
            correct_answers=correct_count,
            wrong_questions=wrong_questions,
            time_spent=time_spent,
            score=score
        )
        
        self._update_stats(result)
        return result
    
    def _ask_question(self, question: Question, current: int, total: int,
                      show_hint: bool) -> bool:
        """答题"""
        print(f"【第 {current}/{total} 题】", end=" ")
        
        # 显示难度
        diff_symbol = {"1": "⭐", "2": "⭐⭐", "3": "⭐⭐⭐"}[str(question.difficulty.value)]
        print(f"{diff_symbol} ", end="")
        
        # 显示标签
        if question.tags:
            print(f"[{'/'.join(question.tags[:2])}]", end=" ")
        print()
        
        print(f"📖 {question.question}")
        
        # 显示提示
        if show_hint and question.hint:
            print(f"💡 提示: {question.hint}")
        
        # 显示选项
        if question.options:
            for opt in question.options:
                print(f"  {opt.label}. {opt.text}")
        
        # 获取答案
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            print("（多选题，输入多个选项如：AB）")
            user_answer = input("👉 你的答案: ").upper().strip()
        else:
            user_answer = input("👉 你的答案: ").upper().strip()
        
        # 判断正误
        is_correct = self._check_answer(question, user_answer)
        
        if is_correct:
            print("✅ 正确！")
        else:
            print(f"❌ 错误！正确答案是: {self._get_correct_answer(question)}")
        
        if question.explanation:
            print(f"📚 解析: {question.explanation}")
        
        return is_correct
    
    def _check_answer(self, question: Question, user_answer: str) -> bool:
        """检查答案"""
        if question.question_type == QuestionType.SINGLE_CHOICE:
            correct = next((opt.label for opt in question.options if opt.is_correct), "")
            return user_answer == correct
        
        elif question.question_type == QuestionType.TRUE_FALSE:
            correct = next((opt.label for opt in question.options if opt.is_correct), "")
            return user_answer == correct
        
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            correct_set = set(opt.label for opt in question.options if opt.is_correct)
            user_set = set(user_answer)
            return correct_set == user_set
        
        elif question.question_type == QuestionType.FILL_BLANK:
            return user_answer.lower().strip() == question.answer.lower().strip()
        
        elif question.question_type == QuestionType.PROGRAMMING:
            # 简单检查：运行用户代码看结果
            return self._check_programming(question, user_answer)
        
        return False
    
    def _get_correct_answer(self, question: Question) -> str:
        """获取正确答案"""
        if question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE]:
            for opt in question.options:
                if opt.is_correct:
                    return f"{opt.label} ({opt.text})"
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            correct_labels = [opt.label for opt in question.options if opt.is_correct]
            return "".join(correct_labels)
        elif question.question_type == QuestionType.FILL_BLANK:
            return question.answer
        elif question.question_type == QuestionType.PROGRAMMING:
            return question.answer
        return ""
    
    def _check_programming(self, question: Question, user_answer: str) -> bool:
        """检查编程题答案"""
        # 这里可以实现更复杂的代码检查逻辑
        # 目前只是简单比较
        if user_answer.strip() == question.answer.strip():
            return True
        
        # 尝试执行用户代码
        try:
            code = question.code_template.replace("pass", user_answer, 1)
            exec(code, {})
            return True
        except:
            return False
    
    def _update_stats(self, result: QuizResult):
        """更新统计信息"""
        self.stats.total_quizzes += 1
        self.stats.total_questions += result.total_questions
        self.stats.correct_answers += result.correct_answers
        
        # 更新错题
        for q in result.wrong_questions:
            if q.qid not in self.stats.wrong_question_ids:
                self.stats.wrong_question_ids.append(q.qid)
        
        # 更新主题统计
        for q in result.wrong_questions:
            for tag in q.tags:
                if tag not in self.stats.topic_stats:
                    self.stats.topic_stats[tag] = {'total': 0, 'wrong': 0}
                self.stats.topic_stats[tag]['total'] += 1
                self.stats.topic_stats[tag]['wrong'] += 1
        
        # 检查连续天数
        today = datetime.now().date()
        if self.stats.last_quiz_date:
            last_date = self.stats.last_quiz_date.date()
            if last_date == today:
                pass  # 同一天
            elif (today - last_date).days == 1:
                self.stats.streak_days += 1  # 连续第二天
            else:
                self.stats.streak_days = 1  # 重新开始
        else:
            self.stats.streak_days = 1
        
        self.stats.last_quiz_date = datetime.now()
        self.save_stats()
    
    def review_wrong_questions(self, question_bank: QuestionBank, count: int = 5):
        """错题复习"""
        if not self.stats.wrong_question_ids:
            print("🎉 没有错题需要复习！继续保持！")
            return
        
        # 获取错题
        all_questions = []
        for questions in question_bank.banks.values():
            all_questions.extend(questions)
        
        wrong_questions = [q for q in all_questions if q.qid in self.stats.wrong_question_ids]
        
        if not wrong_questions:
            print("🎉 所有错题已清除！")
            return
        
        # 随机选择一些错题
        review_questions = random.sample(wrong_questions, min(count, len(wrong_questions)))
        
        print(f"\n{'='*60}")
        print(f"📚 错题复习！共 {len(review_questions)} 道题")
        print(f"{'='*60}\n")
        
        for i, q in enumerate(review_questions, 1):
            print(f"【复习 {i}/{len(review_questions)}】")
            print(f"📖 {q.question}")
            if q.options:
                for opt in q.options:
                    marker = "✅" if opt.is_correct else "  "
                    print(f"  {marker} {opt.label}. {opt.text}")
            print(f"📚 解析: {q.explanation}\n")
            input("按回车继续...")
            print()
        
        print("💪 复习完成！记住这些知识点！")
    
    def show_stats(self):
        """显示统计信息"""
        print(f"\n{'='*60}")
        print(f"📊 学习统计")
        print(f"{'='*60}")
        print(f"总测验次数: {self.stats.total_quizzes}")
        print(f"总答题数: {self.stats.total_questions}")
        print(f"正确答题: {self.stats.correct_answers}")
        print(f"正确率: {self.stats.accuracy:.1f}%")
        print(f"错题数量: {len(self.stats.wrong_question_ids)}")
        print(f"连续学习天数: {self.stats.streak_days} 天")
        
        if self.stats.topic_stats:
            print(f"\n📈 薄弱知识点:")
            for tag, data in sorted(self.stats.topic_stats.items(), 
                                   key=lambda x: x[1]['wrong'], reverse=True)[:5]:
                wrong_rate = data['wrong'] / data['total'] * 100 if data['total'] > 0 else 0
                print(f"  - {tag}: 错题率 {wrong_rate:.0f}%")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Interactive CLI Learning Quiz - 交互式命令行测验学习工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python interactive_quiz.py                    # 交互模式
    python interactive_quiz.py --quiz python      # 指定题库
    python interactive_quiz.py --review           # 错题复习
    python interactive_quiz.py --stats            # 查看统计
    python interactive_quiz.py --create-sample    # 创建示例题库
        """
    )
    
    parser.add_argument('--quiz', '-q', type=str, default='python_basics',
                        help='指定题库名称（默认: python_basics）')
    parser.add_argument('--count', '-c', type=int, default=5,
                        help='题目数量（默认: 5）')
    parser.add_argument('--review', '-r', action='store_true',
                        help='错题复习模式')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='显示学习统计')
    parser.add_argument('--hint', '-H', action='store_true',
                        help='显示提示')
    parser.add_argument('--difficulty', '-d', type=str, choices=['easy', 'medium', 'hard'],
                        help='题目难度')
    parser.add_argument('--create-sample', '-C', action='store_true',
                        help='创建示例题库')
    parser.add_argument('--bank-dir', '-b', type=str, default='question_banks',
                        help='题库目录（默认: question_banks）')
    
    args = parser.parse_args()
    
    # 创建题库目录和示例
    if args.create_sample:
        bank = QuestionBank(args.bank_dir)
        bank.create_sample_bank()
        return
    
    # 初始化
    bank = QuestionBank(args.bank_dir)
    engine = QuizEngine()
    
    # 显示统计
    if args.stats:
        engine.show_stats()
        return
    
    # 错题复习
    if args.review:
        engine.review_wrong_questions(bank)
        return
    
    # 检查是否有题库
    if not bank.banks:
        print("📂 未找到题库，正在创建示例题库...")
        bank.create_sample_bank()
    
    # 获取题目
    difficulty_map = {'easy': Difficulty.EASY, 'medium': Difficulty.MEDIUM, 'hard': Difficulty.HARD}
    difficulty = difficulty_map.get(args.difficulty)
    
    questions = bank.get_questions(args.quiz, args.count, difficulty)
    
    if not questions:
        print(f"❌ 题库 '{args.quiz}' 中没有足够的题目！")
        print(f"可用题库: {', '.join(bank.banks.keys())}")
        return
    
    # 开始测验
    result = engine.start_quiz(questions, args.hint)
    
    if result:
        print(f"\n{'='*60}")
        print(f"📊 测验结果")
        print(f"{'='*60}")
        print(f"得分: {result.score:.0f} 分")
        print(f"正确: {result.correct_answers}/{result.total_questions}")
        print(f"用时: {result.time_spent:.1f} 秒")
        
        if result.wrong_questions:
            print(f"\n❌ 错题 {len(result.wrong_questions)} 道，建议使用 --review 复习")
        else:
            print(f"\n🎉 太棒了！全对！")


if __name__ == "__main__":
    main()
