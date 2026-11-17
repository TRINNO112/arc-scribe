import time
from collections import deque
from fastapi import HTTPException
from backend.config import settings

class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter ensuring safe usage below AI Studio free tier limits."""
    
    def __init__(self, max_requests: int = settings.SAFETY_RPM_CEILING, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps = deque()

    def acquire(self) -> float:
        """Checks if a request is allowed. Returns estimated wait time if blocked."""
        now = time.time()
        
        # Purge timestamps outside the sliding window
        while self.timestamps and (now - self.timestamps[0]) > self.window_seconds:
            self.timestamps.popleft()
            
        if len(self.timestamps) >= self.max_requests:
            oldest = self.timestamps[0]
            cooldown = round(self.window_seconds - (now - oldest) + 0.5, 1)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit buffer reached ({self.max_requests} RPM safety cap). Please wait {cooldown} seconds before sending the next scene."
            )
            
        self.timestamps.append(now)
        return 0.0

    def remaining_quota(self) -> int:
        now = time.time()
        while self.timestamps and (now - self.timestamps[0]) > self.window_seconds:
            self.timestamps.popleft()
        return max(0, self.max_requests - len(self.timestamps))

rate_limiter = SlidingWindowRateLimiter()
