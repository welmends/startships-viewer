import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from app.db import async_db
from app.models import User

router = APIRouter()


@router.post("/login")
async def login(user: User, Authorize: AuthJWT = Depends()):
    try:
        stored_user = await async_db.users.find_one({"username": user.username})
        if stored_user:
            if bcrypt.checkpw(user.password.encode("utf-8"), stored_user["password"]):
                access_token = Authorize.create_access_token(subject=user.username)
                return JSONResponse(
                    status_code=200, content={"access_token": access_token}
                )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
