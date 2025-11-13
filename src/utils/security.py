"""
Security Configuration
Implements rate limiting and security headers
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # {ip_address: [timestamp1, timestamp2, ...]}

    def is_allowed(self, identifier, max_requests=100, window_seconds=3600):
        """
        Check if request is allowed based on rate limit

        Args:
            identifier: IP address or user identifier
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            tuple: (allowed, remaining, reset_time)
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier]
                if ts > cutoff
            ]
        else:
            self.requests[identifier] = []

        # Check if allowed
        current_count = len(self.requests[identifier])

        if current_count >= max_requests:
            # Calculate reset time
            oldest_request = min(self.requests[identifier])
            reset_time = oldest_request + timedelta(seconds=window_seconds)
            return False, 0, reset_time

        # Add current request
        self.requests[identifier].append(now)

        remaining = max_requests - (current_count + 1)
        reset_time = now + timedelta(seconds=window_seconds)

        return True, remaining, reset_time


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=100, window_seconds=3600):
    """
    Decorator for rate limiting endpoints

    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address)
            identifier = request.remote_addr

            # Check rate limit
            allowed, remaining, reset_time = rate_limiter.is_allowed(
                identifier, max_requests, window_seconds
            )

            if not allowed:
                response = jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'retry_after': int((reset_time - datetime.now()).total_seconds())
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
                return response

            # Execute function
            result = f(*args, **kwargs)

            # Add rate limit headers to response
            if hasattr(result, 'headers'):
                result.headers['X-RateLimit-Limit'] = str(max_requests)
                result.headers['X-RateLimit-Remaining'] = str(remaining)
                result.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))

            return result

        return decorated_function
    return decorator


def add_security_headers(response):
    """
    Add security headers to response

    Usage in Flask:
        @app.after_request
        def apply_security_headers(response):
            return add_security_headers(response)
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Content Security Policy (adjust as needed)
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https:;"

    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    return response


def sanitize_input(text, max_length=1000):
    """
    Sanitize user input to prevent XSS and injection attacks

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ''

    # Limit length
    text = str(text)[:max_length]

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')']
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()


def generate_csrf_token():
    """Generate CSRF token"""
    import secrets
    return secrets.token_urlsafe(32)


def validate_csrf_token(token, expected_token):
    """Validate CSRF token"""
    return token == expected_token
