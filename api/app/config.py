from app.constants import DEFAULT_SECRET_KEY
from pydantic import BaseModel


class Settings(BaseModel):
    AUTHJWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    authjwt_access_token_expires: int = 3600  # 1 hour
