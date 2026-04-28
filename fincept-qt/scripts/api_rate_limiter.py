#!/usr/bin/env python3
"""
api_rate_limiter.py - Rate Limiter for Free API Sources

Prevents hitting rate limits on free APIs (Yahoo Finance, FRED, World Bank, etc.)
Uses token bucket algorithm with configurable limits per source.

Usage:
    from api_rate_limiter import RateLimiter
    
    limiter = RateLimiter()
    
    # Check if request is allowed
    if limiter.allow_request("yahoo_finance"):
        # Make API call
        data = fetch_yahoo_data(symbol)
        limiter.record_request("yahoo_finance")
    else:
        wait_time = limiter.get_wait_time("yahoo_finance")
        print(f"Rate limited. Wait {wait_time:.1f}s before retry")

Configuration:
    Edit RATE_LIMITS dict below to adjust limits per API source.
"""

import time
import threading
from typing import Dict, Optional
from collections import defaultdict


class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Args:
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        
        if new_tokens > 0:
            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = now
    
    def allow_request(self) -> bool:
        """Check if a request is allowed"""
        with self.lock:
            self._refill()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before next request is allowed"""
        with self.lock:
            self._refill()
            
            if self.tokens >= 1:
                return 0.0
            
            tokens_needed = 1 - self.tokens
            return tokens_needed / self.refill_rate


# [FREE-MODE] Rate limits for free API sources
# Format: {source_name: (requests_per_minute, requests_per_hour)}
RATE_LIMITS = {
    # Yahoo Finance - generous but not unlimited
    "yahoo_finance": (60, 2000),
    
    # FRED - Federal Reserve Economic Data
    "fred": (120, 10000),
    
    # World Bank Open Data
    "world_bank": (60, 5000),
    
    # IMF Statistics
    "imf": (30, 2000),
    
    # OECD Statistics
    "oecd": (60, 5000),
    
    # AKShare (China data) - be conservative
    "akshare": (30, 1000),
    
    # ECB Statistical Data Warehouse
    "ecb": (60, 5000),
    
    # BIS Global Debt Statistics
    "bis": (30, 2000),
    
    # Reddit API (if using PRAW)
    "reddit": (60, 1000),
    
    # CoinGecko (crypto data)
    "coingecko": (50, 3000),
    
    # Default fallback
    "default": (30, 1000),
}


class RateLimiter:
    """Global rate limiter for all API sources"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
        
        # Initialize buckets for each source
        for source, (rpm, rph) in RATE_LIMITS.items():
            # Use the more restrictive limit (per minute or per hour)
            tokens_per_second = min(rpm / 60.0, rph / 3600.0)
            self.buckets[source] = TokenBucket(max_tokens=rpm, refill_rate=tokens_per_second)
    
    def allow_request(self, source: str = "default") -> bool:
        """
        Check if a request to the given source is allowed
        
        Args:
            source: API source name (e.g., "yahoo_finance", "fred")
            
        Returns:
            True if request is allowed, False if rate limited
        """
        if source not in self.buckets:
            source = "default"
        
        return self.buckets[source].allow_request()
    
    def record_request(self, source: str = "default"):
        """Record that a request was made (for tracking/monitoring)"""
        with self.lock:
            now = time.time()
            self.request_counts[source].append(now)
            
            # Clean old entries (older than 1 hour)
            cutoff = now - 3600
            self.request_counts[source] = [
                t for t in self.request_counts[source] if t > cutoff
            ]
    
    def get_wait_time(self, source: str = "default") -> float:
        """
        Get seconds to wait before next request is allowed
        
        Args:
            source: API source name
            
        Returns:
            Seconds to wait (0.0 if request is allowed now)
        """
        if source not in self.buckets:
            source = "default"
        
        return self.buckets[source].get_wait_time()
    
    def get_usage_stats(self, source: str = "default") -> Dict[str, any]:
        """
        Get usage statistics for a source
        
        Args:
            source: API source name
            
        Returns:
            Dictionary with usage stats
        """
        with self.lock:
            now = time.time()
            counts = self.request_counts.get(source, [])
            
            # Count requests in last minute and hour
            minute_ago = now - 60
            hour_ago = now - 3600
            
            rpm_count = sum(1 for t in counts if t > minute_ago)
            rph_count = sum(1 for t in counts if t > hour_ago)
            
            limits = RATE_LIMITS.get(source, RATE_LIMITS["default"])
            max_rpm, max_rph = limits
            
            return {
                "source": source,
                "requests_last_minute": rpm_count,
                "requests_last_hour": rph_count,
                "limit_per_minute": max_rpm,
                "limit_per_hour": max_rph,
                "minute_usage_pct": (rpm_count / max_rpm * 100) if max_rpm > 0 else 0,
                "hour_usage_pct": (rph_count / max_rph * 100) if max_rph > 0 else 0,
            }
    
    def wait_if_needed(self, source: str = "default", timeout: float = 30.0) -> bool:
        """
        Wait until request is allowed or timeout is reached
        
        Args:
            source: API source name
            timeout: Max seconds to wait
            
        Returns:
            True if request is now allowed, False if timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.allow_request(source):
                return True
            
            wait_time = self.get_wait_time(source)
            if wait_time > 0:
                sleep_time = min(wait_time + 0.1, timeout - (time.time() - start_time))
                if sleep_time > 0:
                    time.sleep(sleep_time)
            else:
                return True
        
        return False
    
    def reset(self, source: Optional[str] = None):
        """Reset rate limiter for a source or all sources"""
        if source:
            if source in self.buckets:
                rpm, _ = RATE_LIMITS.get(source, RATE_LIMITS["default"])
                self.buckets[source] = TokenBucket(max_tokens=rpm, 
                                                   refill_rate=rpm / 60.0)
                with self.lock:
                    self.request_counts[source] = []
        else:
            # Reset all
            for src, (rpm, rph) in RATE_LIMITS.items():
                tokens_per_second = min(rpm / 60.0, rph / 3600.0)
                self.buckets[src] = TokenBucket(max_tokens=rpm, 
                                                refill_rate=tokens_per_second)
            with self.lock:
                self.request_counts.clear()


# Global singleton instance
_limiter_instance = None
_limiter_lock = threading.Lock()


def get_limiter() -> RateLimiter:
    """Get global rate limiter instance (thread-safe singleton)"""
    global _limiter_instance
    
    if _limiter_instance is None:
        with _limiter_lock:
            if _limiter_instance is None:
                _limiter_instance = RateLimiter()
    
    return _limiter_instance


def check_and_wait(source: str = "default", timeout: float = 30.0) -> bool:
    """
    Convenience function: check rate limit and wait if needed
    
    Args:
        source: API source name
        timeout: Max seconds to wait
        
    Returns:
        True if request can proceed, False if should skip
    """
    limiter = get_limiter()
    return limiter.wait_if_needed(source, timeout)


# Example usage and testing
if __name__ == "__main__":
    import sys
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("🧪 Testing Rate Limiter\n")
    
    limiter = RateLimiter()
    
    # Test basic functionality
    print("Test 1: Basic allow/deny")
    for i in range(5):
        allowed = limiter.allow_request("test_api")
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Denied'}")
    
    print("\nTest 2: Wait time")
    wait = limiter.get_wait_time("test_api")
    print(f"  Wait time: {wait:.2f}s")
    
    print("\nTest 3: Usage stats")
    stats = limiter.get_usage_stats("test_api")
    print(f"  Stats: {stats}")
    
    print("\nTest 4: Multiple sources")
    sources = ["yahoo_finance", "fred", "world_bank"]
    for source in sources:
        allowed = limiter.allow_request(source)
        wait = limiter.get_wait_time(source)
        print(f"  {source}: {'✅ Allowed' if allowed else '❌ Denied'}, wait={wait:.2f}s")
    
    print("\nTest 5: Wait and retry")
    import time
    print("  Making rapid requests...")
    success_count = 0
    for i in range(10):
        if limiter.allow_request("yahoo_finance"):
            limiter.record_request("yahoo_finance")
            success_count += 1
        else:
            wait = limiter.get_wait_time("yahoo_finance")
            print(f"    Request {i+1}: Rate limited, would wait {wait:.1f}s")
    
    print(f"  Successful requests: {success_count}/10")
    
    print("\n✅ All tests completed!")
