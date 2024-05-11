# functions starts with _ are the utility functions of a particular route
import os
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from jose import jwt
from pydantic import ValidationError
from app.api.dependencies.scheme import TokenValidationScheme
from app.api.models.admin import Admin
from app.api.models.client import ClientUser, SubClientUser
from app.api.models.common import MobileNumberAuth, TokenData, UserRoles, UsernamePasswordAuth,Token
from app.db.mongo_db import sub_client_user
from app.utils.crypt import get_password_hash
from app.utils.common import  _validate_token_not_expired,_login,_check_user_existance,_check_user_non_existance,_set_owner_and_get_creator
from app.utils.token import create_access_token, token_expired

router = APIRouter(prefix="/subclient",tags=["Auth"])

token_validation_scheme = TokenValidationScheme()

def _create_new_subclient(sub_client:ClientUser): 
    # hashing password if auth type is username password 
    if(isinstance(sub_client.auth_data,UsernamePasswordAuth)):
        sub_client.auth_data.password = get_password_hash(password=sub_client.auth_data.password)
    new_client_doc = sub_client_user.insert_one(sub_client.model_dump())
    # generating new access token for this admin
    token_data = TokenData(id=str(new_client_doc.inserted_id),role=UserRoles.client)
    access_token = create_access_token(data=token_data)
    # update document with access_token 
    update_result = sub_client_user.update_one({"_id":new_client_doc.inserted_id},{"$set":{"access_token":access_token.model_dump()}})
    # if any thing wrong while adding accesstoken to the user. We will delete that user account from database so user will not get created without any access token
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to add access-token to the client's account")
    return access_token

        
@router.post("/create" ,description="Only admins and clients , Sub_client are allowed to create sub-clients")
def create_sub_client(new_sub_client: SubClientUser,token: Token = Depends(token_validation_scheme)) -> JSONResponse:
    try:
        payload = jwt.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        _validate_token_not_expired(payload)
        creator,new_sub_client= _set_owner_and_get_creator(payload,new_sub_client,token)
        _check_user_non_existance(new_sub_client.auth_data,UserRoles.sub_client)
        # adding creator_id to new sub_client obj
        new_sub_client.creator_id = str(creator["_id"])
        # creating client 
        access_token = _create_new_subclient(new_sub_client)
        return JSONResponse(status_code=status.HTTP_201_CREATED,content={"detail":"Sub-Client created successfully","token":access_token.model_dump()})
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@router.post("/login")
async def login_sub_client(auth_data: UsernamePasswordAuth | MobileNumberAuth,otp:str = None):
    try:
        # checking existance 
        sub_client = _check_user_existance(auth_data,UserRoles.sub_client)
        return _login(sub_client,auth_data,UserRoles.sub_client,otp)
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


