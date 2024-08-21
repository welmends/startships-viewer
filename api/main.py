from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import bcrypt
import httpx
import logging

from db import seed_database, async_db
from constants import STORED_USERS
from models import Settings, User

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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


@app.on_event("startup")
async def on_startup():
    await seed_database()


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
async def get_starships(page: int = 1, page_size: int = 10, manufacturer: str = None, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="page and page_size must be a positive integer not equal to zero")

        results, page_previous, page_next = [], -1, None
        while True:
            response = httpx.get(f"https://swapi.dev/api/starships/?page={page}")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Unknown error")
            data = response.json()
            if page_previous == -1:
                page_previous = data.get('previous')
            page_next = data.get('next')
            if data.get('results') == None or data.get('next') == None:
                break
            res_results = data.get('results')
            if manufacturer:
                res_results = [row for row in res_results if manufacturer in row.get('manufacturer')]
            results += res_results[:page_size-len(results)]
            if len(results) == page_size:
                break
            page += 1
        return JSONResponse(
            status_code=200,
            content={
                "next": page_next,
                "previous": page_previous,
                "results": results
            }
        )
    except Exception as e:
        raise e

@app.get("/api/manufacturers")
async def get_all_manufacturers(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        # TODO: I have to create a async task to update other database to give this fresh information
        manufacturers = ['Corellian Engineering Corporation', 'Kuat Drive Yards', 'Sienar Fleet Systems', 'Cyngus Spaceworks']
        return JSONResponse(
            status_code=200,
            content={"results": manufacturers}
        )
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