from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
import bcrypt

from app.db import async_db
from app.models import User

router = APIRouter()

@router.post("/login")
async def login(user: User, Authorize: AuthJWT = Depends()):
    stored_user = await async_db.users.find_one({"username": user.username})
    if stored_user:
        if bcrypt.checkpw(user.password.encode('utf-8'), stored_user["password"]):
            access_token = Authorize.create_access_token(subject=user.username)
            return {"access_token": access_token}
    raise HTTPException(status_code=401, detail="Invalid credentials")
