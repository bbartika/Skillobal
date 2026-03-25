from core.routes import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.allowedHostsMiddleware import AllowedHostsMiddleware
from middleware.checkUserExistsMiddleware import CheckUserExistsMiddleware
from middleware.tokenAuthentication import AccessTokenAuthenticatorMiddleware

app = FastAPI()
allowed_hosts = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace with frontend domains
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AllowedHostsMiddleware, allowed_hosts)
app.add_middleware(AccessTokenAuthenticatorMiddleware)
app.add_middleware(CheckUserExistsMiddleware)

# all routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    try:
        from core.database import client
        await client.admin.command('ping')
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="error"
    ) 
