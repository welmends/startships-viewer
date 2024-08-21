from pydantic import BaseModel

from constants import DEFAULT_SECRET_KEY

class Settings(BaseModel):
    AUTHJWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    authjwt_access_token_expires: int = 3600 # 1 hour

class User(BaseModel):
    username: str
    password: str

class Starship(BaseModel):
    name: str
    model: str
    starship_class: str
    manufacturer: str
    cost_in_credits: str
    length: str
    crew: str
    passengers: str
    max_atmosphering_speed: str
    hyperdrive_rating: str
    MGLT: str
    cargo_capacity: str
    consumables: str