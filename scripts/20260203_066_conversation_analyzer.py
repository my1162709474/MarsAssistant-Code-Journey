#!/usr/bin/env python3
"""
AI Conversation History Analyzer
================================
Analyzes conversation history and generates insights about:
- Activity patterns (hours, days)
- Topic clustering
- Sentiment trends
- Agent usage statistics
- Word frequency analysis

Author: AI Code Journey
Date: 2026-02-03
"""

import json
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib


class ConversationAnalyzer:
    """Analyzes AI conversation history for patterns and insights."""
    
    def __init__(self):
        self.messages = []
        self.hourly_dist = Counter()
        self.daily_dist = Counter()
        self.word_freq = Counter()
        self.sentiment_keywords = {
            'positive': ['great', 'awesome', 'excellent', 'amazing', 'wonderful', 
                        'helpful', 'perfect', 'love', 'thanks', 'appreciate'],
            'negative': ['error', 'fail', 'wrong', 'bad', 'issue', 'problem', 
                        'broken', 'bug', 'hate', 'terrible', 'awful']
        }
        self.sentiment_scores = []
        
    def load_from_json(self, filepath: str) -> bool:
        """Load conversation data from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get('messages', data)
            self._analyze_all()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def load_from_list(self, messages: List[Dict[str, Any]]):
        """Load messages directly from a list."""
        self.messages = messages
        self._analyze_all()
    
    def _extract_timestamp(self, message: Dict) -> datetime:
        """Extract timestamp from message."""
        # Try different common timestamp formats
        ts_fields = ['timestamp', 'created_at', 'date', 'time', 'createdAt']
        for field in ts_fields:
            if field in message:
                try:
                    return datetime.fromisoformat(message[field].replace('Z', '+00:00'))
                except:
                    continue
        # Default to now
        return datetime.now()
    
    def _extract_content(self, message: Dict) -> str:
        """Extract text content from message."""
        content_fields = ['content', 'text', 'message', 'body', 'content_text']
        for field in content_fields:
            if field in message:
                content = message[field]
                if isinstance(content, str):
                    return content
                elif isinstance(content, dict):
                    return content.get('text', '') or content.get('body', '')
                elif isinstance(content, list):
                    # Handle block-based content
                    return ' '.join([c.get('text', '') if isinstance(c, dict) else str(c) 
                                   for c in content])
        return str(message)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and clean text."""
        # Convert to lowercase and extract words
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove special characters, keep only alphanumeric
        words = re.findall(r'\b[a-z]+\b', text)
        # Filter common stopwords
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until',
            'while', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'me', 'him', 'us', 'them'
        }
        return [w for w in words if w not in stopwords and len(w) > 2]
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis based on keywords."""
        text_lower = text.lower()
        pos_count = sum(1 for word in self.sentiment_keywords['positive'] 
                       if word in text_lower)
        neg_count = sum(1 for word in self.sentiment_keywords['negative'] 
                       if word in text_lower)
        if pos_count + neg_count == 0:
            return 0.5  # Neutral
        return pos_count / (pos_count + neg_count)
    
    def _analyze_all(self):
        """Run all analyses on loaded messages."""
        for msg in self.messages:
            timestamp = self._extract_timestamp(msg)
            content = self._extract_content(msg)
            
            # Hourly distribution
            self.hourly_dist[timestamp.hour] += 1
            # Daily distribution
            self.daily_dist[timestamp.strftime('%Y-%m-%d')] += 1
            # Word frequency
            words = self._tokenize(content)
            self.word_freq.update(words)
            # Sentiment
            sentiment = self._analyze_sentiment(content)
            self.sentiment_scores.append(sentiment)
    
    def get_activity_patterns(self) -> Dict[str, Any]:
        """Analyze activity patterns."""
        peak_hour = self.hourly_dist.most_common(1)[0] if self.hourly_dist else (0, 0)
        total_messages = sum(self.hourly_dist.values())
        
        return {
            'total_messages': total_messages,
            'peak_hour': peak_hour[0],
            'peak_hour_count': peak_hour[1],
            'hourly_distribution': dict(self.hourly_dist),
            'active_days': len(self.daily_dist),
            'messages_per_day': round(total_messages / max(len(self.daily_dist), 1), 2)
        }
    
    def get_top_words(self, n: int = 20) -> Dict[str, int]:
        """Get most frequent words."""
        return dict(self.word_freq.most_common(n))
    
    def get_sentiment_trends(self) -> Dict[str, Any]:
        """Analyze sentiment trends."""
        if not self.sentiment_scores:
            return {'average': 0.5, 'trend': 'neutral'}
        
        avg_sentiment = sum(self.sentiment_scores) / len(self.sentiment_scores)
        positive_ratio = sum(1 for s in self.sentiment_scores if s > 0.6) / len(self.sentiment_scores)
        negative_ratio = sum(1 for s in self.sentiment_scores if s < 0.4) / len(self.sentiment_scores)
        
        trend = 'positive' if avg_sentiment > 0.55 else 'negative' if avg_sentiment < 0.45 else 'neutral'
        
        return {
            'average': round(avg_sentiment, 3),
            'positive_ratio': round(positive_ratio, 3),
            'negative_ratio': round(negative_ratio, 3),
            'trend': trend
        }
    
    def generate_report(self) -> str:
        """Generate a human-readable analysis report."""
        activity = self.get_activity_patterns()
        sentiment = self.get_sentiment_trends()
        top_words = self.get_top_words(15)
        
        report = []
        report.append("=" * 60)
        report.append("AI Conversation History Analysis Report")
        report.append("=" * 60)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.append("\n📊 Activity Overview")
        report.append("-" * 40)
        report.append(f"Total Messages: {activity['total_messages']}")
        report.append(f"Active Days: {activity['active_days']}")
        report.append(f"Avg Messages/Day: {activity['messages_per_day']}")
        report.append(f"Peak Activity Hour: {activity['peak_hour']}:00 ({activity['peak_hour_count']} msgs)")
        
        report.append("\n😊 Sentiment Analysis")
        report.append("-" * 40)
        report.append(f"Average Sentiment: {sentiment['average']:.2%}")
        report.append(f"Positive Messages: {sentiment['positive_ratio']:.1%}")
        report.append(f"Negative Messages: {sentiment['negative_ratio']:.1%}")
        report.append(f"Overall Trend: {sentiment['trend'].upper()}")
        
        report.append("\n🔤 Top Keywords")
        report.append("-" * 40)
        for i, (word, count) in enumerate(top_words.items(), 1):
            bar = "█" * min(count, 30)
            report.append(f"{i:2}. {word:<15} {count:>4} {bar}")
        
        report.append("\n📅 Hourly Distribution")
        report.append("-" * 40)
        for hour in range(24):
            count = self.hourly_dist.get(hour, 0)
            bar = "█" * min(count * 2, 40)
            report.append(f"{hour:02d}:00 │{bar} ({count})")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def export_stats_json(self, filepath: str = "conversation_stats.json"):
        """Export statistics as JSON."""
        stats = {
            'generated_at': datetime.now().isoformat(),
            'activity': self.get_activity_patterns(),
            'sentiment': self.get_sentiment_trends(),
            'top_words': self.get_top_words(50),
            'daily_distribution': dict(self.daily_dist)
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"Stats exported to {filepath}")


def demo():
    """Run demonstration with sample data."""
    print("🤖 Conversation Analyzer Demo")
    print("=" * 50)
    
    # Generate sample conversation data
    sample_messages = [
        {
            'id': '1',
            'timestamp': '2026-02-03T10:30:00',
            'content': 'Great progress on the BitNet optimization! The new SIMD implementation shows significant speedups.',
            'role': 'assistant'
        },
        {
            'id': '2',
            'timestamp': '2026-02-03T11:15:00',
            'content': 'I love how the hybrid retrieval combines dense and sparse methods. This improves recall significantly.',
            'role': 'assistant'
        },
        {
            'id': '3',
            'timestamp': '2026-02-03T14:22:00',
            'content': 'Found a bug in the attention mechanism. The softmax overflow needs fixing with proper normalization.',
            'role': 'assistant'
        },
        {
            'id': '4',
            'timestamp': '2026-02-03T15:45:00',
            'content': 'Excellent work on the memory pool optimization! malloc calls reduced by 90%. This is amazing.',
            'role': 'assistant'
        },
        {
            'id': '5',
            'timestamp': '2026-02-03T16:30:00',
            'content': 'The parallel matrix multiplication with pthread shows good scaling across multiple cores.',
            'role': 'assistant'
        }
    ]
    
    # Analyze sample data
    analyzer = ConversationAnalyzer()
    analyzer.load_from_list(sample_messages)
    
    # Generate and print report
    print(analyzer.generate_report())
    
    # Export stats
    analyzer.export_stats_json()


if __name__ == "__main__":
    demo()
