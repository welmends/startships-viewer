import logging
import os

import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import OperationFailure

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
sync_db_client = MongoClient(mongo_uri)
async_db_client = AsyncIOMotorClient(mongo_uri)

sync_db = sync_db_client.onedb
async_db = async_db_client.onedb


async def seed_database():
    try:
        existing_collections = await async_db.list_collection_names()

        if "starships" not in existing_collections:
            await async_db.create_collection("starships")
            await async_db.starships.create_index([("uid")], unique=True)

        if "manufacturers" not in existing_collections:
            await async_db.create_collection("manufacturers")
            await async_db.manufacturers.create_index([("name")], unique=True)

        search = async_db["search"]
        if (await search.count_documents({})) == 0:
            await search.insert_one({"search": "page", "last_page": 1})

        users = async_db["users"]
        if (await users.count_documents({})) == 0:
            await users.insert_one(
                {
                    "username": "admin",
                    "password": bcrypt.hashpw(
                        "admin".encode("utf-8"), bcrypt.gensalt()
                    ),
                }
            )

        logger.info(f"Seeded collections.")
    except OperationFailure as e:
        logger.warning(f"Failed to seed database: {e}")
