import logging

import httpx
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready
from pydantic import ValidationError

from app.constants import SWAPI_STARSHIPS_BASE_URL
from app.db import sync_db
from app.models import Starship

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


def parse_manufacturers(manufacturer_string, special_names=["Inc", "Inc."]):
    """
    Parses a manufacturer string into a list of manufacturer names, handling cases where
    manufacturers might include commas in their names.

    Args:
        manufacturer_string (str): A comma-separated string of manufacturer names.

    Returns:
        list: A list of manufacturer names, with leading and trailing whitespace removed.
    """
    # Split the string by commas
    parts = manufacturer_string.split(",")

    # Strip leading and trailing whitespace from each part
    manufacturers = [part.strip() for part in parts if part.strip()]
    filtered_manufacturers = []
    for i in range(len(manufacturers)):
        append = True
        for s in special_names:
            if s == manufacturers[i] and len(filtered_manufacturers) > 0:
                if s.endswith("."):
                    s = s[:-1]
                filtered_manufacturers[-1] += f", {s}"
                append = False
                continue
        if append:
            filtered_manufacturers.append(manufacturers[i])

    return filtered_manufacturers


@celery.task
def consume_swapi():
    """
    Fetches starship data from the SWAPI (Star Wars API) and updates the local database.

    This Celery task performs the following operations:

    1. Retrieves the current page number to fetch from the `sync_db.search` collection.
    2. Makes HTTP GET requests to the SWAPI to retrieve starship data.
    3. Processes the retrieved data, filtering and organizing it into a format compatible with the local database schema.
    4. Checks for existing records in the `sync_db.starships` and `sync_db.manufacturers` collections and inserts only new records.
    5. Updates the `sync_db.search` collection with the latest page number if there are no more pages available from SWAPI.

    The function handles pagination by continuously fetching new pages until there are no more pages left.
    It also ensures that only new starships and manufacturers are added to the database to avoid duplication.

    Returns:
        dict: A dictionary with a status key indicating the result of the operation. Possible values are:
            - {"status": "success"} if the operation was successful.
            - {"status": "failed"} if there was an error during the HTTP request.
            - {"status": "exception"} if there was an unhandled error during the HTTP request.
    """

    def validate_starship(data):
        """Validate starship data using the Starship model."""
        try:
            return Starship(**data)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return None

    try:
        logger.info("Start consuming swapi..")
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
                validated_item = validate_starship(filtered_item)

                if validated_item:
                    uid = int(item.get("url").split("/")[-2])
                    uids.add(uid)
                    filtered_item["uid"] = uid
                    valid_data.append(filtered_item)
                    manufacturers.update(
                        parse_manufacturers(filtered_item["manufacturer"])
                    )

            # Check if any uid already exists in the database
            existing_uids = sync_db.starships.find(
                {"uid": {"$in": list(uids)}}
            ).distinct("uid")
            new_data = [doc for doc in valid_data if doc["uid"] not in existing_uids]

            # Insert only new documents on starships collection
            if new_data:
                sync_db.starships.insert_many(new_data)

            # Check if any manufacturer already exists in the database
            existing_manufacturers = sync_db.manufacturers.find(
                {"name": {"$in": list(manufacturers)}}
            ).distinct("name")
            manufacturers_data = [
                {"name": m} for m in manufacturers if m not in existing_manufacturers
            ]

            # Insert only new documents on manufacturers collection
            if manufacturers_data:
                sync_db.manufacturers.insert_many(manufacturers_data)

            # Check if there is new pages
            if data.get("next"):
                page += 1
            else:
                sync_db.search.update_one(
                    {"search": "page"}, {"$set": {"last_page": page}}
                )
                break
        return {"status": "success"}
    except Exception as e:
        logger.error(e)
        return {"status": "exception"}


@worker_ready.connect
def at_start(sender, **kwargs):
    """
    Runs the consume_swapi Celery task as soon as we start the Celery worker using the @worker_ready.connect signal.
    """
    celery.send_task("app.celery_app.consume_swapi")


# Celery configurations: Beat schedule and timezone
celery.conf.beat_schedule = {
    "daily-task": {
        "task": "app.celery_app.consume_swapi",
        "schedule": crontab(
            hour=0, minute=0
        ),  # Runs consume_swapi Celery task once a day
    }
}

celery.conf.timezone = "UTC"
