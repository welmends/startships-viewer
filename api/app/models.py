from pydantic import BaseModel

from app.constants import DEFAULT_SECRET_KEY

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