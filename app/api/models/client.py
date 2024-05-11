from pydantic import BaseModel , EmailStr, ConfigDict
from typing import Union
from .common import Token

from app.api.models.common import MobileNumberAuth, UsernamePasswordAuth
# ---------------Client stuff ---------
class ClientUser(BaseModel):
    name: str | None = None
    image: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    auth_data: Union[UsernamePasswordAuth, MobileNumberAuth]
    number: str | None = None
    access_token: Token | None = None
    admin_id: str |None = None #Foreign key
    model_config = ConfigDict(arbitrary_types_allowed=True)


# -------------sub client ---------------
class SubClientUser(BaseModel):
    name: str | None = None
    image: str | None = None
    auth_data: Union[UsernamePasswordAuth, MobileNumberAuth]
    access_token: str| None = None
    creator_id: str|None = None #Foreign key  // Create could be either client , another subclient or even admin
    client_id: str|None =  None #Foreign key // It will be id of client 
    model_config= ConfigDict(arbitrary_types_allowed=True)


