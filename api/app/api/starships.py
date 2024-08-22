from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pymongo import ASCENDING
import re
from fastapi.responses import JSONResponse

from app.db import async_db

router = APIRouter()

@router.get("/starships")
async def get_starships(page: int = 1, page_size: int = 10, manufacturer: str = None, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="page and page_size must be a positive integer not equal to zero")

        query_filter = {}
        if manufacturer:
            filter_regex = re.compile(manufacturer, re.IGNORECASE)
            query_filter = {"manufacturer": filter_regex}

        total = await async_db.starships.count_documents(query_filter)
        skip = (page - 1) * page_size
        cursor = async_db.starships.find(query_filter, projection={"_id": False}).sort("uid", ASCENDING).skip(skip).limit(page_size)
        starships = await cursor.to_list(length=page_size)
        return JSONResponse(
            status_code=200,
            content={
                "next": page + 1 if (page-1)*page_size + len(starships) < total else None,
                "previous": page if page > 1 else None,
                "results": starships
            }
        )
    except Exception as e:
        raise e
