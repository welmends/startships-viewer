from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import bcrypt
import httpx

DEFAULT_SECRET_KEY = "default_secret_key"
STORED_USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()),
    }
]

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

class Settings(BaseModel):
    AUTHJWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    authjwt_access_token_expires: int = 60 # seconds

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    if exc.status_code == 422:
        return JSONResponse(
            status_code=401,
            content={"detail": "Credentials have expired"}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

class User(BaseModel):
    username: str
    password: str

@app.post("/api/login")
async def login(user: User, Authorize: AuthJWT = Depends()):
    stored_user = [u for u in STORED_USERS if u.get("username") == user.username]
    if len(stored_user) == 1:
        if bcrypt.checkpw(user.password.encode('utf-8'), stored_user[0].get("password")):
            access_token = Authorize.create_access_token(subject=user.username)
            return {"access_token": access_token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/ping")
async def ping(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return 'pong', 200
    except Exception as e:
        raise e

@app.get("/api/starships")
async def get_starships(page: int = 1, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        response = httpx.get(f"https://swapi.dev/api/starships/?page={page}")
        return response.json()
    except Exception as e:
        raise e

# Function to modify OpenAPI schema to include the security scheme
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
            "description": "Please provide the token with the 'Bearer' prefix. Example: `Bearer your_token_here`"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi