from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from pydantic import ValidationError

from app.api.dependencies.dependencies import get_current_admin
from app.api.models.client import ClientUser
from app.api.models.common import MobileNumberAuth, TokenData, UserRoles, UsernamePasswordAuth
from app.db.mongo_db import client_user
from app.utils.common import _check_user_existance, _check_user_non_existance, _login
from app.utils.crypt import get_password_hash
from app.utils.token import create_access_token, update_token
router = APIRouter(prefix="/client",tags=["Auth"])


def _create_new_client(client:ClientUser):
    # hashing password if auth type is username password 
    if(isinstance(client.auth_data,UsernamePasswordAuth)):
        client.auth_data.password = get_password_hash(password=client.auth_data.password)
    new_client_doc = client_user.insert_one(client.model_dump())
    # generating new access token for this admin
    token_data = TokenData(id=str(new_client_doc.inserted_id),role=UserRoles.client)
    access_token = create_access_token(data=token_data)
    # update document with access_token 
    update_result = client_user.update_one({"_id":new_client_doc.inserted_id},{"$set":{"access_token":access_token.model_dump()}})
    # if any thing wrong while adding accesstoken to the user. We will delete that user account from database so user will not get created without any access token
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to add access-token to the client's account")
    return access_token
@router.post("/create" ,description="Only admins are allowed to create clients")
def create_client(new_client: ClientUser,admin: dict = Depends(get_current_admin)):
    try:
        # checking for the existance if admin already exists with the username either number
        _check_user_non_existance(new_client.auth_data,UserRoles.client)
        # adding admin id to the new_client object 
        new_client.admin_id = str(admin["_id"])
        # creating client 
        access_token = _create_new_client(new_client)
        return JSONResponse(status_code=status.HTTP_201_CREATED,content={"detail":"Client created successfully","token":access_token.model_dump()})
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@router.post("/login")
async def login_client(auth_data: UsernamePasswordAuth | MobileNumberAuth,otp:str = None):
    try:
        client = _check_user_existance(auth_data,UserRoles.client)
        return _login(client,auth_data,UserRoles.client,otp)
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

