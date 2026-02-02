#!/usr/bin/env python3
"""
智能聊天机器人框架
Smart Chatbot Framework

支持多种聊天API、上下文管理、对话历史、插件扩展
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """消息"""
    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {})
        )


class ChatProvider(ABC):
    """聊天提供商基类"""

    @abstra\�method
    def chat(self, messages: List[Message], **kwargs) -> Message:
        """发送聊天请求"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取提供商名称"""
        pass


class OpenAIProvider(ChatProvider):
    """OpenAI API提供商"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        import openai
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, messages: List[Message], (*kwargs) -> Message:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            **kwargs
        )
        return Message(
            role=MessageRole.ASSISTANT,
            content=response.choices[0].message.content,
            metadata={"model": self.model}
        )

    def get_name(self) -> str:
        return f"OpenAI ({self.model})"


class AnthropicProvider(ChatProvider):
    """Anthropic API提供商"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

    def chat(self, messages: List[Message], **kwargs) -> Message:
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": m.role.value, "content": m.content} for m in messages],
            (*kwargs
        )
        return Message(
            role=MessageRole.ASSISTANT,
            content=response.content[0].text,
            metadata={"model": self.model}
        )

    def get_name(self) -> str:
        return f"Anthropic ({self.model})"


class Chatbot:
    """智能聊天机器人"""

    def __init__(self, provider: ChatProvider, system_prompt: str = None):
        self.provider = provider
        self.conversations: Dict[str, List[Message]] = {}
        self.system_prompt = system_prompt
        self.plugins: List['ChatPlugin'] = []

    def create_conversation(self, conversation_id: str = None) -> str:
        """创建新对话"""
        conv_id = conversation_id or hashlib.md5(f"{time.time()}".encode()).hexdigest()
        self.conversations[conv_id] = []
        return conv_id

    def add_message(self, conversation_id: str, message: Message):
        """添加消息到对话"""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        self.conversations[conversation_id].append(message)

    def chat(self, conversation_id: str, user_message: str, 
             use_history: bool = True, max_history: int = 20) -> str:
        """发送消息"""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)

        # 构建消息列表
        messages = []
        if self.system_prompt:
            messages.append(Message(role=MessageRole.SYSTEM, content=self.system_prompt))

        # 添加历史消息
        if use_history:
            history = self.conversations[conversation_id][-max_history:]
            messages.extend(history)

        # 添加用户消息
        user_msg = Message(role=MessageRole.USER, content=user_message)
        messages.append(user_msg)

        # 执行插件前置处理
        for plugin in self.plugins:
            messages = plugin.pre_process(messages)

        # 发送请求
        response = self.provider.chat(messages)

        # 添加到历史
        self.conversations[conversation_id].append(user_msg)
        self.conversations[conversation_id].append(response)

        # 执行插件后置处理
        response = plugin.post_process(response) if (plugin := self.plugins[-1]) else response

        return response.content

    def get_history(self, conversation_id: str) -> List[Message]:
        """获取对话历史"""
        return self.conversations.get(conversation_id, [])

    def clear_history(self, conversation_id: str):
        """清空对话历史"" ��b6��fW'6F�����B��6V�b�6��fW'6F���3��6V�b�6��fW'6F���5�6��fW'6F�����E���Р�FVbFE��Vv��6V�b��Vv��t6�E�Vv��r���"".k{�X�h�.K�b"""
        self.plugins.append(plugin)


class ChatPlugin(ABC):
    """聊天插件基类"""

    @abstra\�method
    def pre_process(self, messages: List[Message]) -> List[Message]:
        """前置处理"""
        pass

    @abstractmethod
    def post_process(self, response: Message) -> Message:
        """后置处理"""
        pass


class MemoryPlugin(ChatPlugin):
    """记忆插件 - 总结对话内容"""

    def __init__(self, max_summary_length: int = 500):
        self.max_summary_length = max_summary_length

    def pre_process(self, messages: List[Message]) -> List[Message]:
        return messages

    def post_process(self, response: Message) -> Message:
        # 简单的记忆压缩
        if len(response.content) > self.max_summary_length:
            response.content = response.content[:self.max_summary_length] + "..."
        return response


class SensitivityPlugin(ChatPlugin):
    """敏感词过滤插件"""

    def __init__(self, sensitive_words: List[str] = None):
        self.sensitive_words = sensitive_words or ["敏感词1", "敏感词2"]

    def pre_process(self, messages: List[Message]) -> List[Message]:
        return messages

    def post_process(self, response: Message) -> Message:
        for word in self.sensitive_words:
            response.content = response.content.replace(word, "***")
        return response


class ConversationManager:
    """对话管理器 - 管理多个机器人"""

    def __init__(self):
        self.bots: Dict[str, Chatbot] = {}

    def create_bot(self, bot_id: str, provider: ChatProvider, 
                   system_prompt: str = None) -> Chatbot:
        """创建机器人"""
        bot = Chatbot(provider, system_prompt)
        self.bots[bot_id] = bot
        return bot

    def get_bot(self, bot_id: str) -> Optional[Chatbot]:
        """获取机器人"""
        return self.bots.get(bot_id)

    def delete_bot(self, bot_id: str):
        """删除机器人"""
        if bot_id in self.bots:
            del self.bots[bot_id]


# 演示
def demo():
    print("=" * 60)
    print("智能聊天机器人框架演示")
    print("=" * 60)

    # 创建对话管理器
    manager = ConversationManager()

    # 模拟提供商 (实际使用需要真实API Key)
    class MockProvider(ChatProvider):
        def chat(self, messages: List[Message], **kwargs) -> Message:
            last_msg = messages[-1].content if messages else ""
            response = f"收到消息: {last_msg[:50]}..."
            return Message(role=MessageRole.ASSISTANT, content=response)

        def get_name(self) -> str:
            return "Mock"

    provider = MockProvider()
    bot = manager.create_bot("demo_bot", provider, "你是一个友好的助手")

    # 添加插件
    bot.add_plugin(MemoryPlugin())
    bot.add_plugin(SensitivityPlugin(["坏词"]))

    # 创建对话
    conv_id = bot.create_conversation()

    # 发送消息
    questions 9
{
        "你好!",
        "今天天气怎么样?",
        *请说一个包含'坏词'的句子测试过滤",
        "总结一下我们的对话"
    ]

    for q in questions:
        print(f"\n👤 用户: {q}")
        response = bot.chat(conv_id, q)
        print(f"🤖 机器人: {response}")

    print("\n" + "=" * 60)
    print("对话历史:")
    for msg in bot.get_history(conv_id):
        print(f"  [{msg.role.value}] {msg.content[:60]}...")

    print("\n演示完成!")


if __name__ == "__main__":
    demo()
