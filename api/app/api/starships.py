from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pymongo import ASCENDING
import re

from app.db import async_db
from app.models import StarshipQueryParams

router = APIRouter()


@router.get("/starships")
async def get_starships(params: StarshipQueryParams = Depends(), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        
        if params.page < 1 or params.page_size < 1:
            raise HTTPException(status_code=400, detail="page and page_size must be positive integers greater than zero")
        
        query_filter = {}
        if params.manufacturer:
            filter_regex = re.compile(params.manufacturer, re.IGNORECASE)
            query_filter["manufacturer"] = filter_regex

        total = await async_db.starships.count_documents(query_filter)
        skip = (params.page - 1) * params.page_size
        cursor = async_db.starships.find(query_filter, projection={"_id": False}).sort("uid", ASCENDING).skip(skip).limit(params.page_size)
        starships = await cursor.to_list(length=params.page_size)
        return JSONResponse(
            status_code=200,
            content={
                "next": params.page + 1 if (params.page-1)*params.page_size + len(starships) < total else None,
                "previous": params.page if params.page > 1 else None,
                "results": starships
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
