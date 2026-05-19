"""
Middleware de diagnóstico — loga cada request na API.
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("altaclp.routes")


class RouteLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            body_preview = ""
            if request.method in ("POST", "PUT", "PATCH"):
                try:
                    body_bytes = await request.body()
                    body_preview = body_bytes[:500].decode("utf-8", errors="replace")
                    async def receive():
                        return {"type": "http.request", "body": body_bytes, "more_body": False}
                    request = Request(request.scope, receive)
                except Exception:
                    body_preview = "<unreadable>"
            logger.info(
                "[ROUTE HIT] %s %s — body: %s",
                request.method,
                request.url.path,
                body_preview or "{}",
            )
            print(f"[ROUTE HIT] {request.method} {request.url.path} — body: {body_preview or '{}'}")

        response = await call_next(request)
        return response
