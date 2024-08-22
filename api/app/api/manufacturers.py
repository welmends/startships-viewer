from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from pymongo import ASCENDING
from fastapi.responses import JSONResponse

from app.db import async_db

router = APIRouter()

@router.get("/manufacturers")
async def get_all_manufacturers(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        manufacturers = [d["name"] async for d in async_db.manufacturers.find(projection={"_id": False}).sort("name", ASCENDING)]
        return JSONResponse(
            status_code=200,
            content={"results": manufacturers}
        )
    except Exception as e:
        raise e
