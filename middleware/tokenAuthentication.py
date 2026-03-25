import jwt
from fastapi import Request
from core.config import jwt_settings
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from functools import lru_cache

# Cache excluded paths as frozenset for O(1) lookup
EXCLUDED_PATHS = frozenset([
    "/admin/login",
    "/docs",
    "/redoc",
    "/openapi.json",
])

# Pre-create error responses to avoid repeated object creation
ERROR_RESPONSES = {
    "no_token": JSONResponse({"msg": "token not present"}, status_code=401),
    "expired": JSONResponse({"msg": "Token has expired"}, status_code=401),
    "invalid": JSONResponse({"msg": "Invalid token"}, status_code=401),
}

class AccessTokenAuthenticatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle OPTIONS requests first (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Fast path check using frozenset
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # Get the token from headers
        token = request.headers.get("token")
        if not token:
            return JSONResponse({"msg": "token not present"}, status_code=401)

        try:
            # Decode the token using the secret key
            decoded_token = jwt.decode(
                token, jwt_settings.SUGAR_VALUE, algorithms=["HS256"]
            )
            # Attach userId and otpId to the request state
            request.state.userId = decoded_token.get("id")
            request.state.otpId = decoded_token.get("otpId")
        except jwt.ExpiredSignatureError:
            return JSONResponse({"msg": "Token has expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"msg": "Invalid token"}, status_code=401)
        except Exception as e:
            return JSONResponse(
                {"msg": "Something went wrong", "error": str(e)}, status_code=500
            )

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response