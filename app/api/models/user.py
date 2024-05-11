from pydantic import BaseModel , EmailStr
from app.api.models.common import Token


class EndUser(BaseModel):
    _id = None  #mongo will auto generate unique id 
    name: str | None = None
    image: str | None = None
    number: str | None = None
    gender: str | None = None
    email: EmailStr | None = None
    driving_licence: str | None = None
    access_token: Token | None = None
    refresh_key : str = "0" 
    # preferred_locations: List[Location] = []


    
