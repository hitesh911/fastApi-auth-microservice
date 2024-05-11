from fastapi import APIRouter , Depends, HTTPException,status
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from pydantic import ValidationError
from app.api.models.admin import Admin
from app.db.mongo_db import admins
from app.api.models.common import TokenData, UserRoles,UsernamePasswordAuth, MobileNumberAuth
from app.api.dependencies.dependencies import get_current_admin 
from app.utils.common import _check_user_existance, _check_user_non_existance, _login
from app.utils.token import create_access_token
from app.utils.crypt import get_password_hash

router = APIRouter(prefix="/admin",tags=["Auth"])


# routes and respective function 
def create_new_admin(admin:Admin):
    # hashing password if auth type is username password 
    if(isinstance(admin.auth_data,UsernamePasswordAuth)):
        admin.auth_data.password = get_password_hash(password=admin.auth_data.password)
    new_admin_doc = admins.insert_one(admin.model_dump())
    # generating new access token for this admin
    token_data = TokenData(id=str(new_admin_doc.inserted_id),role=UserRoles.admin)
    access_token = create_access_token(data=token_data)
    # update document with access_token 
    update_result = admins.update_one({"_id":new_admin_doc.inserted_id},{"$set":{"access_token":access_token.model_dump()}})
    # if any thing wrong while adding accesstoken to the user. We will delete that user account from database so user will not get created without any access token
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to add access-token to the admin's account")
    # Retrieve the updated document
    return access_token
def _check_root_admin(admin:Admin):
    if(admin["name"] != "root"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only root operation")

@router.post("/create",description="Only super admin is able to create admin")
async def create_admin(new_admin: Admin,current_admin:dict=Depends(get_current_admin)):
    try:
        _check_root_admin(current_admin)
        # checking for the existance if admin already exists with the username either number
        _check_user_non_existance(new_admin.auth_data,UserRoles.admin)
        access_token = create_new_admin(new_admin)
        return JSONResponse(status_code=status.HTTP_201_CREATED,content={"detail":"Admin created successfully","token":access_token.model_dump()})
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


    
@router.post("/login")
async def login_admin(auth_data: UsernamePasswordAuth | MobileNumberAuth,otp:str = None):
    try:
        admin =_check_user_existance(auth_data,UserRoles.admin)
        return _login(admin,auth_data,UserRoles.admin,otp)
    except ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))



   


    

