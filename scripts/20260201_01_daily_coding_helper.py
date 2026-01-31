#!/usr/bin/env python3
"""
Daily Coding Helper - A utility script for coding practice and learning
Created as part of MarsAssistant Code Journey
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Callable, Any


class CodingChallenge:
    """Represents a coding challenge with difficulty levels"""
    
    DIFFICULTIES = ["Easy", "Medium", "Hard"]
    CATEGORIES = ["Array", "String", "Tree", "Graph", "DP", "Stack", "Queue"]
    
    def __init__(self, title: str, difficulty: str, category: str, description: str):
        self.title = title
        self.difficulty = difficulty
        self.category = category
        self.description = description
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "description": self.description
        }


class DailyCodingHelper:
    """Main helper class for daily coding practice"""
    
    def __init__(self):
        self.challenges_solved = []
        self.streak_days = 0
        self.start_date = datetime.now()
        self._initialize_challenge_bank()
    
    def _initialize_challenge_bank(self):
        """Initialize the challenge bank with sample challenges"""
        self.challenge_bank = [
            CodingChallenge(
                "Two Sum", "Easy", "Array",
                "Find two numbers in an array that add up to a target"
            ),
            CodingChallenge(
                "Reverse String", "Easy", "String",
                "Reverse a string without using built-in reverse()"
            ),
            CodingChallenge(
                "Valid Parentheses", "Medium", "Stack",
                "Check if a string of brackets is valid"
            ),
            CodingChallenge(
                "Binary Tree Inorder Traversal", "Medium", "Tree",
                "Return inorder traversal of a binary tree"
            ),
            CodingChallenge(
                "Longest Increasing Subsequence", "Medium", "DP",
                "Find the length of the longest increasing subsequence"
            ),
            CodingChallenge(
                "Merge K Sorted Lists", "Hard", "Heap",
                "Merge k sorted linked lists into one sorted list"
            ),
            CodingChallenge(
                "Word Ladder", "Hard", "Graph",
                "Transform one word to another by changing one letter at a time"
            ),
        ]
    
    def get_daily_challenge(self) -> CodingChallenge:
        """Get a random challenge for today"""
        return random.choice(self.challenge_bank)
    
    def get_multiple_challenges(self, count: int = 3) -> List[CodingChallenge]:
        """Get multiple random challenges"""
        return random.sample(self.challenge_bank, min(count, len(self.challenge_bank)))
    
    def mark_solved(self, challenge: CodingChallenge):
        """Mark a challenge as solved and track progress"""
        self.challenges_solved.append({
            "challenge": challenge.to_dict(),
            "solved_at": datetime.now().isoformat()
        })
        self.streak_days += 1
    
    def get_progress_report(self) -> Dict[str, Any]:
        """Generate a progress report"""
        return {
            "total_solved": len(self.challenges_solved),
            "current_streak": self.streak_days,
            "start_date": self.start_date.isoformat(),
            "completion_rate": len(self.challenges_solved) / len(self.challenge_bank) * 100
            if self.challenge_bank else 0
        }
    
    def generate_practice_schedule(self, days: int = 7) -> List[Dict[str, str]]:
        """Generate a practice schedule for the next N days"""
        schedule = []
        for i in range(days):
            challenge = self.get_daily_challenge()
            schedule.append({
                "day": i + 1,
                "date": f"Day {i + 1}",
                "challenge": challenge.title,
                "difficulty": challenge.difficulty,
                "category": challenge.category
            })
        return schedule


def quick_sort(arr: List[int]) -> List[int]:
    """Quick sort implementation"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def binary_search(arr: List[int], target: int) -> int:
    """Binary search implementation"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number using dynamic programming"""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome"""
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


# Demo usage
if __name__ == "__main__":
    print("=== Daily Coding Helper Demo ===\n")
    
    helper = DailyCodingHelper()
    
    # Get today's challenge
    today_challenge = helper.get_daily_challenge()
    print(f"Today's Challenge: {today_challenge.title}")
    print(f"Difficulty: {today_challenge.difficulty}")
    print(f"Category: {today_challenge.category}")
    print(f"Description: {today_challenge.description}\n")
    
    # Show sorting demo
    unsorted = [64, 34, 25, 12, 22, 11, 90]
    sorted_arr = quick_sort(unsorted.copy())
    print(f"Quick Sort Demo: {unsorted} → {sorted_arr}")
    
    # Show binary search demo
    sorted_nums = [1, 3, 5, 7, 9, 11, 13]
    idx = binary_search(sorted_nums, 7)
    print(f"Binary Search Demo: Found 7 at index {idx}")
    
    # Show fibonacci demo
    print(f"Fibonacci Demo: fib(10) = {fibonacci(10)}")
    
    # Show palindrome demo
    print(f"Palindrome Demo: 'A man, a plan, a canal: Panama' → {is_palindrome('A man, a plan, a canal: Panama')}")
    
    # Mark challenge as solved
    helper.mark_solved(today_challenge)
    print(f"\nProgress: {helper.get_progress_report()['total_solved']} challenges solved!")
