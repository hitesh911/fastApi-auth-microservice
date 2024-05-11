from pydantic import BaseModel , ConfigDict , Field
from app.api.models.common import Token
from .common import UsernamePasswordAuth , MobileNumberAuth
from typing import Union



class Admin(BaseModel):
    name: str
    auth_data: Union[UsernamePasswordAuth, MobileNumberAuth]
    access_token: Token | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)