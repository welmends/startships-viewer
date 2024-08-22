from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready
import logging
import httpx

from app.constants import SWAPI_STARSHIPS_BASE_URL
from app.db import sync_db
from app.models import Starship

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery.task
def consume_swapi():
    logger.info('Start consuming swapi..')
    doc = sync_db.search.find_one({"search": "page"})
    page = doc["last_page"]
    model_fields = Starship.__annotations__.keys()
    
    while True:
        # Call SWAPI
        response = httpx.get(f"{SWAPI_STARSHIPS_BASE_URL}/?page={page}")
        if response.status_code != 200:
            return {"status": "failed"}
        data = response.json()
        results = data["results"]

        # Create an array of starships
        valid_data, uids, manufacturers = [], set(), set()
        for item in results:
            filtered_item = {key: item.get(key, "unknown") for key in model_fields}
            uid = int(item.get("url").split('/')[-2])
            uids.add(uid)
            filtered_item["uid"] = uid
            valid_data.append(filtered_item)
            manufacturers.update([m.strip() for m in filtered_item["manufacturer"].split(",")])
        
        # Check if any uid already exists in the database
        existing_uids = sync_db.starships.find({"uid": {"$in": list(uids)}}).distinct("uid")
        new_data = [doc for doc in valid_data if doc["uid"] not in existing_uids]

        # Insert only new documents on starships collection
        if new_data:
            sync_db.starships.insert_many(new_data)

        # Check if any manufacturer already exists in the database
        existing_manufacturers = sync_db.manufacturers.find({"name": {"$in": list(manufacturers)}}).distinct("name")
        manufacturers_data = [{"name": m} for m in manufacturers if m not in existing_manufacturers]

        # Insert only new documents on manufacturers collection
        if manufacturers_data:
            sync_db.manufacturers.insert_many(manufacturers_data)

        # Check if there is new pages
        if data.get("next"):
            page += 1
        else:
            sync_db.search.update_one(
                {"search": "page"},
                {"$set": {"last_page": page}}
            )
            break
    return {"status": "success"}

celery.conf.beat_schedule = {
    'daily-task': {
        'task': 'app.celery_app.consume_swapi',
        'schedule': crontab(hour=0, minute=0),
    }
}

celery.conf.timezone = 'UTC'

@worker_ready.connect
def at_start(sender, **kwargs):
    celery.send_task("app.celery_app.consume_swapi")