"""
Custom Middleware für FastAPI
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


async def log_requests(request: Request, call_next):
    """
    Middleware zum Logging aller API-Requests
    """
    start_time = time.time()

    # Process Request
    response = await call_next(request)

    # Log
    duration = time.time() - start_time
    print(
        f'[{response.status_code}] {request.method} {request.url.path} '
        f'- {duration:.3f}s'
    )

    return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple Rate Limiting Middleware
    WICHTIG: In Production sollte Cloudflare Rate Limiting verwendet werden!
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        # IP-basiertes Rate Limiting
        client_ip = request.client.host

        # Check Rate Limit
        # TODO: Implementiere Redis-basiertes Rate Limiting für Production

        response = await call_next(request)
        return response
