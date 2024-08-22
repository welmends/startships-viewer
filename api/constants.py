import bcrypt

SWAPI_STARSHIPS_BASE_URL = "https://swapi.dev/api/starships"

DEFAULT_SECRET_KEY = "default_secret_key"

STORED_USERS = [
    {
        "username": "admin",
        "password": bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()),
    }
]