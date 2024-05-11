# renewing access token 
from bson import ObjectId
from fastapi import HTTPException,status , Depends
from jose import jwt ,JWTError
from app.api.models.user import EndUser
from app.api.models.common import TokenData , Token, UserRoles
from app.db.mongo_db import end_users,client_user,admins,sub_client_user

from datetime import timedelta , datetime, timezone
import os

def create_access_token(data: TokenData, expires_delta: timedelta | None = None) -> Token:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    # updating expire_at field in tokendata object 
    data.expires_at = expire
    encoded_jwt = jwt.encode(data.model_dump(), os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    new_token = Token(access_token=encoded_jwt,token_type="Bearer")
    return new_token

def update_token(data: TokenData, expires_delta: timedelta | None = None ):
    new_token = create_access_token(data,expires_delta)
    match data.role:
        case UserRoles.user:
            update_result = end_users.update_one({"_id":ObjectId(data.id)},{"$set":{"access_token":new_token.model_dump()}})          
        case UserRoles.client:
            update_result = client_user.update_one({"_id":ObjectId(data.id)},{"$set":{"access_token":new_token.model_dump()}})          
        case UserRoles.sub_client:
            update_result = sub_client_user.update_one({"_id":ObjectId(data.id)},{"$set":{"access_token":new_token.model_dump()}})          
        case UserRoles.admin:
            update_result = admins.update_one({"_id":ObjectId(data.id)},{"$set":{"access_token":new_token.model_dump()}})          
        case _:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Some error occure while updating token")
    if update_result.modified_count == 0:
            return {"status":False,"detail": "Unable to add access-token to the user account"}
    else:
        return {"status":True,"detail": "Token updated successfully","token":new_token}
   
def decrypt_jwt_token(token:str):
    try :
        return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except JWTError as e:
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"}, )

# it returns True if token is expired 
def token_expired(payload):
    # Check if the token is expired
    expiration_datetime = datetime.fromisoformat(payload["expires_at"])
    if expiration_datetime < datetime.utcnow().replace(tzinfo=timezone.utc):
        return True
    else:
        return False