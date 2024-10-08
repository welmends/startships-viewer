import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError
from pymongo import ASCENDING

from app.db import async_db

router = APIRouter()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@router.get("/manufacturers")
async def get_all_manufacturers(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        manufacturers = [
            d["name"]
            async for d in async_db.manufacturers.find(projection={"_id": False}).sort(
                "name", ASCENDING
            )
        ]
        return JSONResponse(status_code=200, content={"results": manufacturers})
    except MissingTokenError as e:
        raise HTTPException(status_code=401, detail="Missing token")
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
