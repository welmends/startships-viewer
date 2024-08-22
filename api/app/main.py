import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException, MissingTokenError

from app.api.routes import router as api_router
from app.config import Settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    from .db import seed_database

    await seed_database()


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
async def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    if exc.status_code == 422:
        raise HTTPException(status_code=401, detail="Credentials have expired")
    return HTTPException(status_code=exc.status_code, content=exc.message)


@app.get("/api/ping")
async def ping(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return "pong", 200
    except MissingTokenError as e:
        raise HTTPException(status_code=401, detail="Missing token")
    except Exception as e:
        raise e


app.include_router(api_router, prefix="/api")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="BFF Starships API",
        version="0.0.1",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Please provide the token with the 'Bearer' prefix. Example: `Bearer your_token_here`",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
