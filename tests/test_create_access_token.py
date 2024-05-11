from preprocessor import loadProject
loadProject()
from bson import ObjectId 
import os

from app.utils.token import create_access_token
from datetime import timedelta 
from app.api.models.common import TokenData


# access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
access_token_expires = timedelta(minutes=1)
token_data = TokenData(id="65be8c310cf35d6094398eeb")
access_token = create_access_token(
    data=token_data, expires_delta=access_token_expires
)
print(type(access_token))
