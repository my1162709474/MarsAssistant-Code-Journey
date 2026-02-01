import hashlib
import random
import string

def generate_secure_password(length=16, use_special=True):
    """Generate a secure random password"""
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if use_special:
        chars = lowercase + uppercase + digits + special
    else:
        chars = lowercase + uppercase + digits
    
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special) if use_special else random.choice(digits)
    ]
    password.extend(random.choice(chars) for _ in range(length - len(password)))
    random.shuffle(password)
    return "".join(password)

def hash_text(text, algorithm="sha256"):
    """Hash text using specified algorithm"""
    hasher = getattr(hashlib, algorithm)()
    hasher.update(text.encode())
    return hasher.hexdigest()

if __name__ == "__main__":
    pwd = generate_secure_password(20)
    print(f"Generated Password: {pwd}")
    print(f"SHA256: {hash_text(pwd)}")
