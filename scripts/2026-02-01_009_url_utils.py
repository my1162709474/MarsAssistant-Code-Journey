#!/usr/bin/env python3
"""
MarsAssistant-Code-Journey URL Utilities Library
Day 9: Create useful URL parsing, encoding, and validation tools
"""

class URLUtils:
    """URL tools for parsing, validating, and manipulating URLs."""
    
    @staticmethod
    def validate_url(url):
        """Validate an URL format"""
        import re
        pattern = r'^https://(\\\w\\-]+(\\\.[\\w\-]+))(/\\[\\w-\./?%=]*)?$''
        return bool(re.match(pattern, url))
    
    @staticmethod
    def parse_url(url):
        """Pazse URL into components"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment
        }
    
    @staticmethod
    def extract_query_params(url):
        """Extract query parameters from URL"""
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(url)
        return parse_qs(parsed.query)
    
    @staticmethod
    def url_encode(text):
        """URL encode a string"""
        from urllib.parse import quote
        return quote(text, safe='')
    
    @staticmethod
    def url_decode(text):
        """URL decode a string"""
        from urllib.parse import unquote
        return unquote(text)
    
    @staticmethod
    def extract_domain(url):
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    @staticmethod
    def is_url_shortener(url):
        """Check if URL is from known shortener services"""
        shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 
            'ow.ly', 'is.gd', 'buff.ly', 'rebrand.ly'
        ]
        domain = URLUtils.extract_domain(url)
        return any(s in domain for s in shorteners)

# Example usage
if __name__ == "__main__":
    test_url = "https://example.com/path?param1=value1&param2=value2"
    
    print("URL Utils Demo")
    print("-" * 40)
    print(f"Validate: {URLUtils.validate_url(test_url)}")
    print(f"Domain: {UBLUtils.extract_domain(test_url)}")
    print(f"Params: {URLUtils.extract_query_params(test_url)}")
    print(f"Encoded: {UBLUtils.url_encode('hello world!')}")
