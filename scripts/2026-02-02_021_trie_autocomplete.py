# Trie-based Auto-Complete Tool
# Day 21: Intelligent text completion using Trie data structure

import re
from collections import Counter
from typing import List, Optional, Dict


class TrieNode:
    """A node in the Trie tree."""
    
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False
        self.frequency: int = 1  # Word frequency for ranking


class Trie:
    """Trie data structure for efficient prefix-based word lookup."""
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        if not node.is_end_of_word:
            node.is_end_of_word = True
            node.frequency = 1
            self.word_count += 1
        else:
            node.frequency += 1
    
    def search(self, prefix: str) -> List[str]:
        """Search for all words starting with the given prefix."""
        node = self.root
        prefix = prefix.lower().strip()
        
        # Navigate to the prefix node
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words from this node
        results = []
        self._collect_words(node, prefix, results)
        
        # Sort by frequency (most frequent first)
        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, freq in results]
    
    def _collect_words(self, node: TrieNode, prefix: str, results: List[tuple]) -> None:
        """Recursively collect all words from a node."""
        if node.is_end_of_word:
            results.append((prefix, node.frequency))
        
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, results)
    
    def get_suggestions(self, prefix: str, max_suggestions: int = 5) -> List[str]:
        """Get top autocomplete suggestions for a prefix."""
        words = self.search(prefix)
        return [word for word, freq in words[:max_suggestions]]
    
    def build_from_text(self, text: str) -> None:
        """Build trie from a large text corpus."""
        # Extract words using regex
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Insert unique words with their frequencies
        for word, freq in word_freq.items():
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            if not node.is_end_of_word:
                node.is_end_of_word = True
                node.frequency = freq
                self.word_count += 1
    
    def load_dictionary(self, file_path: str) -> None:
        """Load words from a dictionary file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    self.insert(word)
    
    def get_word_count(self) -> int:
        """Return the total number of words in the trie."""
        return self.word_count


class AutoComplete:
    """High-level auto-complete interface."""
    
    def __init__(self):
        self.trie = Trie()
        self.history: List[str] = []
    
    def train(self, texts: List[str]) -> None:
        """Train the autocomplete system on multiple texts."""
        for text in texts:
            self.trie.build_from_text(text)
    
    def train_from_file(self, file_path: str) -> None:
        """Train from a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            self.trie.build_from_text(text)
    
    def suggest(self, prefix: str, max_suggestions: int = 5) -> List[str]:
        """Get autocomplete suggestions."""
        if not prefix.strip():
            return []
        
        suggestions = self.trie.get_suggestions(prefix, max_suggestions)
        
        # Add to history if it is a new suggestion
        for suggestion in suggestions:
            if suggestion not in self.history:
                self.history.insert(0, suggestion)
                if len(self.history) > 100:
                    self.history.pop()
        
        return suggestions
    
    def add_word(self, word: str) -> None:
        """Add a new word to the dictionary."""
        self.trie.insert(word)
    
    def complete_word(self, prefbÄ: str) -> Optional[str]:
        """Get the single best completion for a prefix."""
        suggestions = self.suggest(prefix, 1)
        return suggestions[0] if suggestions else None
    
    def get_stats(self) -> Dict:
        """Get statistics about the autocomplete system."""
        return {
            'total_words': self.trie.get_word_count(),
            'history_count': len(self.history),
        }


def demo():
    """Demonstrate the auto-complete tool."""
    print("=== Trie Auto-Complete Demo ===\n")
    
    # Create autocomplete system
    ac = AutoComplete()
    
    # Train with sample data
    training_texts = [
        "Python is a great programming language for beginners",
        "JavaScript is used for web development",
        "Machine learning and artificial intelligence are growing fields",
        "Data structures and algorithms are essential for coding interviews",
        "The quick brown fox jumps over the lazy dog"
    ]
    
    print("Training on sample texts...")
    ac.train(training_texts)
    
    stats = ac.get_stats()
    print(f"Dictionary size: {stats['total_words']} words\n")
    
    # Test suggestions
    test_prefixes = ["p", "pro", "mac", "data", "qu"]
    
    for prefix in test_prefixes:
        suggestions = ac.suggest(prefix, 3)
        print(f"'{prefix}' -> {suggestions}")
    
    print("\n=== Interactive Mode ===")
    print("Type 'quit' to exit, 'stats' for dictionary stats")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                stats = ac.get_stats()
                print(f"Words: {stats['total_words']}, History: {stats['history_count']}")
                continue
            
            if user_input:
                # Add to dictionary
                ac.add_word(user_input)
                print(f"Added: '{user_input}'")
                
                # Get suggestions for current input
                suggestions = ac.suggest(user_input, 3)
                if suggestions:
                    print(f"Suggestions: {suggestions}")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    demo()
