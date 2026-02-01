#!/usr/bin/env python3
"""
AI Conversational Programming Assistant
AI对话式编程助手

A tool that understands natural language requirements and generates appropriate code.
一个能够理解自然语言需求并生成相应代码的工具。

Features / 功能:
- 自然语言转代码
- 代码解释器
- 算法思路助手
- 编程问题诊断
"""

import re
import ast
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class CodeRequest:
    """代码请求"""
    description: str
    language: str = "python"
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    include_comments: bool = True
    include_tests: bool = False


class ConversationalCoder:
    """对话式编程助手"""
    
    # 关键词到算法/功能的映射
    KEYWORD_MAPPINGS = {
        # 排序算法
        "排序": {
            "quick": ("快速排序", "quicksort"),
            "merge": ("归并排序", "mergesort"),
            "bubble": ("冒泡排序", "bubblesort"),
            "heap": ("堆排序", "heapsort"),
            "counting": ("计数排序", "countingsort"),
        },
        # 搜索算法
        "搜索": {
            "binary": ("二分查找", "binary_search"),
            "linear": ("线性搜索", "linear_search"),
            "bfs": ("广度优先搜索", "bfs"),
            "dfs": ("深度优先搜索", "dfs"),
        },
        # 数据结构
        "数据结构": {
            "stack": ("栈", "stack"),
            "queue": ("队列", "queue"),
            "linked_list": ("链表", "linked_list"),
            "tree": ("树", "tree"),
            "graph": ("图", "graph"),
            "heap": ("堆", "heap"),
            "hash": ("哈希表", "hash_table"),
        },
        # 字符串处理
        "字符串": {
            "reverse": ("反转字符串", "reverse_string"),
            "palindrome": ("回文检查", "palindrome_check"),
            "anagram": ("字母异位词", "anagram_check"),
            "substring": ("子串查找", "substring_search"),
        },
        # 动态规划
        "动态规划": {
            "fibonacci": ("斐波那契", "fibonacci"),
            "knapsack": ("背包问题", "knapsack"),
            "lcs": ("最长公共子序列", "lcs"),
            "edit_distance": ("编辑距离", "edit_distance"),
        },
        # 数学运算
        "数学": {
            "prime": ("素数判断", "prime_check"),
            "factorial": ("阶乘", "factorial"),
            "gcd": ("最大公约数", "gcd"),
            "power": ("幂运算", "power"),
        },
        # 文件操作
        "文件": {
            "read": ("读取文件", "file_read"),
            "write": ("写入文件", "file_write"),
            "csv": ("CSV处理", "csv_handler"),
            "json": ("JSON处理", "json_handler"),
        }
    }
    
    def __init__(self):
        self.generated_codes = []
        self.request_history = []
    
    def understand_request(self, description: str) -> CodeRequest:
        """理解用户请求"""
        desc_lower = description.lower()
        
        # 检测语言
        language = "python"
        if "java" in desc_lower or "javascript" in desc_lower:
            language = "javascript"
        elif "c++" in desc_lower or "cpp" in desc_lower:
            language = "cpp"
        elif "go" in desc_lower:
            language = "go"
        
        # 检测难度
        difficulty = Difficulty.INTERMEDIATE
        if any(word in desc_lower for word in ["简单", "基础", "入门", " beginner", " basic"]):
            difficulty = Difficulty.BEGINNER
        elif any(word in desc_lower for word in ["复杂", "高级", "困难", " advanced", " hard"]):
            difficulty = Difficulty.ADVANCED
        
        # 检测是否需要测试
        include_tests = any(word in desc_lower for word in ["测试", "test", "单元", "unit"])
        
        return CodeRequest(
            description=description,
            language=language,
            difficulty=difficulty,
            include_tests=include_tests
        )
    
    def generate_code(self, request: CodeRequest) -> str:
        """根据需求生成代码"""
        code_templates = self._get_code_template(request)
        return code_templates
    
    def _get_code_template(self, request: CodeRequest) -> str:
        """获取代码模板"""
        templates = {
            "python": self._python_template,
            "javascript": self._javascript_template,
            "cpp": self._cpp_template,
        }
        return templates.get(request.language, self._python_template)(request)
    
    def _python_template(self, request: CodeRequest) -> str:
        """Python代码模板"""
        filename = self._generate_filename(request.description)
        
        template = f'''#!/usr/bin/env python3
"""
{self._get_cn_description(request.description)}
Generated by AI Conversational Programming Assistant
"""

from typing import List, Optional, Dict


class Solution:
    """解决方案类"""
    
    def __init__(self):
        self.test_cases = []
    
    def main(self, data):
        """
        主处理函数
        
        Args:
            data: 输入数据
            
        Returns:
            处理结果
        """
        # TODO: 实现核心逻辑
        pass
    
    def add_test_case(self, input_data, expected_output):
        """添加测试用例"""
        self.test_cases.append({
            "input": input_data,
            "expected": expected_output
        })
    
    def run_tests(self) -> bool:
        """运行所有测试用例"""
        print("Running tests...")
        for i, test in enumerate(self.test_cases):
            result = self.main(test["input"])
            if result == test["expected"]:
                print(f"✓ Test {i+1} passed")
            else:
                print(f"✗ Test {i+1} failed")
                print(f"  Expected: {{test['expected']}}")
                print(f"  Got:      {{result}}")
                return False
        print("All tests passed!")
        return True


def main():
    """主函数入口"""
    solution = Solution()
    
    # 示例使用
    example_input = []
    result = solution.main(example_input)
    print(f"Result: {{result}}")
    
    # 运行测试
    solution.run_tests()


if __name__ == "__main__":
    main()
'''
        return template
    
    def _javascript_template(self, request: CodeRequest) -> str:
        """JavaScript代码模板"""
        return '''// JavaScript Code Template
// Generated by AI Conversational Programming Assistant

class Solution {
    constructor() {
        this.testCases = [];
    }
    
    main(data) {
        // TODO: 实现核心逻辑
        return null;
    }
    
    addTestCase(inputData, expectedOutput) {
        this.testCases.push({
            input: inputData,
            expected: expectedOutput
        });
    }
    
    runTests() {
        console.log("Running tests...");
        for (let i = 0; i < this.testCases.length; i++) {
            const test = this.testCases[i];
            const result = this.main(test.input);
            if (JSON.stringify(result) === JSON.stringify(test.expected)) {
                console.log(`✓ Test ${i+1} passed`);
            } else {
                console.log(`✗ Test ${i+1} failed`);
                console.log(`  Expected: ${JSON.stringify(test.expected)}`);
                console.log(`  Got:      ${JSON.stringify(result)}`);
                return false;
            }
        }
        console.log("All tests passed!");
        return true;
    }
}

// 示例使用
const solution = new Solution();
const result = solution.main([]);
console.log(`Result: ${JSON.stringify(result)}`);
solution.runTests();

module.exports = Solution;
'''
    
    def _cpp_template(self, request: CodeRequest) -> str:
        """C++代码模板"""
        return '''// C++ Code Template
// Generated by AI Conversational Programming Assistant

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {
public:
    Solution() {}
    
    // 主处理函数
    vector<int> main(vector<int> data) {
        // TODO: 实现核心逻辑
        return data;
    }
    
    void addTestCase(vector<int> input, vector<int> expected) {
        testCases.push_back({input, expected});
    }
    
    bool runTests() {
        cout << "Running tests..." << endl;
        for (size_t i = 0; i < testCases.size(); i++) {
            auto result = main(testCases[i].input);
            if (result == testCases[i].expected) {
                cout << "✓ Test " << i+1 << " passed" << endl;
            } else {
                cout << "✗ Test " << i+1 << " failed" << endl;
                return false;
            }
        }
        cout << "All tests passed!" << endl;
        return true;
    }

private:
    struct TestCase {
        vector<int> input;
        vector<int> expected;
    };
    vector<TestCase> testCases;
};

int main() {
    Solution solution;
    
    // 示例使用
    vector<int> exampleInput = {};
    auto result = solution.main(exampleInput);
    cout << "Result: [";
    for (size_t i = 0; i < result.size(); i++) {
        cout << result[i];
        if (i < result.size() - 1) cout << ", ";
    }
    cout << "]" << endl;
    
    solution.runTests();
    
    return 0;
}
'''
    
    def _generate_filename(self, description: str) -> str:
        """生成文件名"""
        # 提取关键词
        keywords = re.findall(r'[\w\u4e00-\u9fff]+', description)
        meaningful_words = [w for w in keywords if len(w) > 2 and w not in ['python', '代码', '实现', '什么', '如何', '怎么']]
        
        if meaningful_words:
            filename = '_'.join(meaningful_words[:3]).lower()
        else:
            filename = 'generated_code'
        
        return filename
    
    def _get_cn_description(self, description: str) -> str:
        """获取中文描述"""
        return f"Generated code for: {description}"
    
    def explain_code(self, code: str) -> str:
        """解释代码"""
        try:
            tree = ast.parse(code)
            explanation = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    explanation.append(f"- 函数 '{node.name}': 行 {node.lineno}")
                elif isinstance(node, ast.ClassDef):
                    explanation.append(f"- 类 '{node.name}': 行 {node.lineno}")
            
            return "代码结构分析:\n" + "\n".join(explanation)
        except:
            return "无法解析代码结构"
    
    def get_similar_examples(self, description: str) -> List[str]:
        """获取类似示例"""
        keywords = self._extract_keywords(description)
        return [code for code in self.generated_codes 
                if any(kw in code.lower() for kw in keywords)]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取长度大于2的单词
        return re.findall(r'\b\w+\b', text.lower())


def interactive_demo():
    """交互式演示"""
    print("=" * 60)
    print("🤖 AI Conversational Programming Assistant")
    print("   AI 对话式编程助手")
    print("=" * 60)
    print()
    print("输入你的需求，例如:")
    print("  - '实现一个快速排序算法'")
    print("  - '写一个函数检查回文数'")
    print("  - '帮我实现栈的数据结构'")
    print("  - '用Python写个二分查找'")
    print()
    print("输入 'quit' 退出")
    print("-" * 60)
    
    coder = ConversationalCoder()
    
    while True:
        print()
        user_input = input("👤 你想要什么功能? ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("再见! 👋")
            break
        
        if not user_input:
            continue
        
        # 理解请求
        request = coder.understand_request(user_input)
        print(f"📋 理解需求:")
        print(f"   语言: {request.language}")
        print(f"   难度: {request.difficulty.value}")
        print(f"   包含测试: {'是' if request.include_tests else '否'}")
        print()
        
        # 生成代码
        code = coder.generate_code(request)
        print("💻 生成的代码:")
        print("-" * 60)
        print(code)
        print("-" * 60)
        
        # 保存到历史
        coder.generated_codes.append(code)
        coder.request_history.append(user_input)


if __name__ == "__main__":
    interactive_demo()
