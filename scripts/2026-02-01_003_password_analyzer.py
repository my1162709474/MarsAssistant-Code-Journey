# Password Strength Analyzer
# Detects password strength and provides improvement suggestions

import re
import hashlib

class PasswordAnalyzer:
    """Analyze password strength and provide feedback."""
    
    def __init__(self):
        self.min_length = 8
        self.common_passwords = {
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        }
    
    def check_strength(self, password: str) -> dict:
        """Analyze password and return strength score and suggestions."""
        if not password:
            return {
                'score': 0,
                'strength': 'Empty',
                'suggestions': ['Please enter a password']
            }
        
        score = 0
        suggestions = []
        checks = {
            'length': len(password) >= self.min_length,
            'lowercase': bool(re.search(r'[a-z]', password)),
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'digit': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            'no_common': password.lower() not in self.common_passwords,
            'no_repeat': len(set(password)) >= len(password) * 0.5
        }
        
        # Calculate base score
        score = sum(checks.values()) * 12.5  # Max 100
        
        # Length bonus/penalty
        if len(password) >= 12:
            score += 10
            suggestions.append('Great length (12+ characters)')
        elif len(password) < 8:
            suggestions.append('Too short (minimum 8 characters)')
        
        # Check for patterns
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            suggestions.append('Avoid repeated characters')
        
        if re.search(r'^[0-9]+$', password):
            score -= 15
            suggestions.append('Do not use only numbers')
        
        # Strength labels
        if score >= 80:
            strength = 'Strong'
        elif score >= 60:
            strength = 'Medium'
        elif score >= 40:
            strength = 'Weak'
        else:
            strength = 'Very Weak'
        
        # Generate suggestions
        if not checks['uppercase']:
            suggestions.append('Add uppercase letters')
        if not checks['lowercase']:
            suggestions.append('Add lowercase letters')
        if not checks['digit']:
            suggestions.append('Add numbers')
        if not checks['special']:
            suggestions.append('Add special characters')
        if not checks['no_common']:
            suggestions.append('This is a common password!')
        
        # Clamp score
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'strength': strength,
            'checks': checks,
            'suggestions': suggestions,
            'entropy': self._calculate_entropy(password)
        }
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        if not password:
            return 0
        
        pool_size = 0
        if re.search(r'[a-z]', password):
            pool_size += 26
        if re.search(r'[A-Z]', password):
            pool_size += 26
        if re.search(r'\d', password):
            pool_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            pool_size += 32
        
        if pool_size == 0:
            return 0
        
        return len(password) * (pool_size ** 0.5)
    
    def generate_strong_password(self, length: int = 16) -> str:
        """Generate a strong random password."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            if (re.search(r'[A-Z]', password) and 
                re.search(r'[a-z]', password) and 
                re.search(r'\d', password) and 
                re.search(r'[!@#$%^&*]', password)):
                return password
    
    def estimate_crack_time(self, password: str) -> str:
        """Estimate time to crack password (assuming 10B guesses/sec)."""
        entropy = self._calculate_entropy(password)
        combinations = 2 ** entropy
        guesses_per_second = 10_000_000_000
        seconds = combinations / guesses_per_second
        
        if seconds < 1:
            return 'Instant'
        elif seconds < 60:
            return f'{int(seconds)} seconds'
        elif seconds < 3600:
            return f'{int(seconds/60)} minutes'
        elif seconds < 86400:
            return f'{int(seconds/3600)} hours'
        elif seconds < 86400 * 365:
            return f'{int(seconds/86400)} days'
        elif seconds < 86400 * 365 * 100:
            return f'{int(seconds/(86400*365))} years'
        else:
            return 'Centuries'


def main():
    """Interactive password analyzer."""
    analyzer = PasswordAnalyzer()
    
    print('=' * 50)
    print('  Password Strength Analyzer')
    print('=' * 50)
    print()
    
    while True:
        password = input('Enter password (or q to quit): ')
        if password.lower() == 'q':
            break
        
        result = analyzer.check_strength(password)
        
        print()
        print(f"Strength: {result['strength']} ({result['score']}%)")
        print(f"Entropy:  {result['entropy']:.1f} bits")
        print(f"Crack time: ~{analyzer.estimate_crack_time(password)}")
        print()
        
        if result['suggestions']:
            print('Suggestions:')
            for s in result['suggestions']:
                print(f'  - {s}')
        
        print()
        
        if result['score'] < 60:
            print(f'Suggested strong password: {analyzer.generate_strong_password()}')
        print('-' * 50)
        print()


if __name__ == '__main__':
    main(
