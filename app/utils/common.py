# it has common operation functions of entire app  
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from pydantic import BaseModel, ValidationError
from bson import ObjectId
from app.api.dependencies.dependencies import get_current_admin, get_current_client, get_current_sub_client, verify_otp
from app.api.models.admin import Admin
from app.api.models.client import ClientUser, SubClientUser
from app.api.models.common import MobileNumberAuth, Token, TokenData, UserRoles, UsernamePasswordAuth
from app.api.models.policy import Policy
from app.db.mongo_db import client_user,admins,end_users,sub_client_user
from fastapi import HTTPException,status

from app.utils.crypt import _verify_password
from app.utils.token import token_expired, update_token
def user_exists_with_this_id(user_id:str,role:UserRoles):
    try:
        user_id = ObjectId(user_id) if isinstance(user_id,str) else user_id
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail=f"{role.value} id is not valid")
    # Retrieve the user,client or admin from the database
    match role:
        case UserRoles.user:
             return (True,end_users.find_one({"_id": ObjectId(user_id)}))            
        case UserRoles.client:
            return (True,client_user.find_one({"_id": ObjectId(user_id)}))
        case UserRoles.sub_client:
            return (True,sub_client_user.find_one({"_id": ObjectId(user_id)}))
        case UserRoles.admin:
            return (True,admins.find_one({"_id": ObjectId(user_id)}))
        case _:
            return (False,None)
def is_valid_data(data:any,model: BaseModel):
    try:
        model(**data)
        return True
    except ValidationError:
        return False


def _check_user_non_existance(auth_data:UsernamePasswordAuth|MobileNumberAuth,user_role:UserRoles):
    # checking for the existance if user already exists with the username either number
    match user_role:
        case UserRoles.user:
            existance= end_users.find_one({"auth_data.number":auth_data.number})       
        case UserRoles.client:
            existance= client_user.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else client_user.find_one({"auth_data.number":auth_data.number})
        case UserRoles.sub_client:
            existance= sub_client_user.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else sub_client_user.find_one({"auth_data.number":auth_data.number})
        case UserRoles.admin:
            existance= admins.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else admins.find_one({"auth_data.number":auth_data.number})
        case _:
            existance= None
    if(existance):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists with same number either user-name")
   
def _check_user_existance(auth_data:UsernamePasswordAuth|MobileNumberAuth,user_role:UserRoles):
    # checking for the existance if user already exists with the username either number
    match user_role:
        case UserRoles.user:
            existance= end_users.find_one({"auth_data.number":auth_data.number})       
        case UserRoles.client:
            existance= client_user.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else client_user.find_one({"auth_data.number":auth_data.number})
        case UserRoles.sub_client:
            existance= sub_client_user.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else sub_client_user.find_one({"auth_data.number":auth_data.number})
        case UserRoles.admin:
            existance= admins.find_one({"auth_data.username":auth_data.username}) if isinstance(auth_data,UsernamePasswordAuth) else admins.find_one({"auth_data.number":auth_data.number})
        case _:
            existance= None
    if(existance):
        return existance
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User doesn't exists")
def _set_owner_and_get_creator(payload:dict,table:SubClientUser|Policy,token:Token):
    if(payload["role"] == UserRoles.client):
        # if client is creating sub client then that client will be the owner 
        creator = get_current_client(token)
        table.client_id = str(creator["_id"])
    elif(payload["role"] == UserRoles.sub_client):
        # if subclient will be making new subclient then owner will be same for both 
        creator = get_current_sub_client(token)
        table.client_id = creator["client_id"]
    else:
        # admin can create sub-client for any valid Client only 
        creator = get_current_admin(token)
        # if creator is admin so he/she must has to mention Valid client_id (One of the client)
        if(table.client_id == None or (not user_exists_with_this_id(table.client_id,UserRoles.client)[0])):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User must have valid client_id pre-defined")
    return creator,table
    

def _validate_token_not_expired(payload):
    if(token_expired(payload)):
        raise ExpiredSignatureError("Token has expired")    


def _login_with_user_name(user:SubClientUser|ClientUser|Admin,auth_data:UsernamePasswordAuth,user_role:UserRoles):
    try:
        # verifying password 
        _verify_password(hashed_password=user["auth_data"]["password"],plain_password=auth_data.password)
        # renewing access token
        token_data = TokenData(id=str(user["_id"]),role=user_role)
        update = update_token(token_data)
        if(update["status"]):
            return JSONResponse({"detail":"Logged in successfully","token":update["token"].model_dump()})
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=update["detail"])
    except HTTPException as ex:
        return ex
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=e)

def _login_with_number(user:SubClientUser|ClientUser|Admin,auth_data:MobileNumberAuth,user_role:UserRoles,otp:str|None = None):
    try:
        if(otp):
            if(verify_otp(auth_data.number,otp)):
                # renewing access token
                token_data = TokenData(id=str(user["_id"]),role=user_role)
                update = update_token(token_data)
                if(update["status"]):
                    return JSONResponse({"detail":"Logged in successfully","token":update["token"].model_dump()})
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=update["detail"])
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Otp verification failed")

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Otp is required")
    except HTTPException as ex:
        return ex
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=e)

        
def _login(user:SubClientUser|ClientUser|Admin,auth_data:UsernamePasswordAuth|MobileNumberAuth,user_role:UserRoles,otp:str|None=None):
    # if auth type is username password 
    if(isinstance(auth_data,UsernamePasswordAuth)):
        return _login_with_user_name(user,auth_data,user_role)
    # or if auth type is mobile number 
    elif(isinstance(auth_data,MobileNumberAuth)):
        return _login_with_number(auth_data,user,otp,user_role)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Request format not matched")
        