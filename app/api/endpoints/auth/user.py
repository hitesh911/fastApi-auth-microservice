from fastapi import APIRouter, Depends,HTTPException,status
from fastapi.responses import JSONResponse
from fastapi import status,HTTPException
from datetime import timedelta
import os

from jose import ExpiredSignatureError
from pydantic import ValidationError

# Local imports
from app.api.dependencies.dependencies import verify_otp
from app.api.models.user import EndUser
from app.utils.token import update_token
from app.utils.token import update_token 
from app.utils.token import create_access_token
from app.api.models.common import TokenData , UserRoles
from app.db.mongo_db import end_users
from app.api.models.user import EndUser


# router 
router = APIRouter(prefix="/user",tags=["Auth"])


# routes path operations and their respective functions
def create_new_user(number):
    existing_user = end_users.find_one({"number":number})
    if not existing_user:
        try:
            # creating new user in database 
            new_user = EndUser(number=number)
            user_document = end_users.insert_one(new_user.model_dump())
            # generating new access token for this user
            token_data = TokenData(id=str(user_document.inserted_id),role=UserRoles.user)
            access_token = create_access_token(data=token_data)
            # update document with access_token 
            update_result = end_users.update_one({"_id":user_document.inserted_id},{"$set":{"access_token":access_token.model_dump()}})
            # if any thing wrong while adding accesstoken to the user. We will delete that user account from database so user will not get created without any access token
            if update_result.modified_count == 0:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to add access-token to the user account")
            return {"status":status.HTTP_201_CREATED,"detail":"Account created successfully","token":access_token}
        except Exception as e:
            # if any thing wrong while adding accesstoken to the user. We will delete that user account from database so user will not get created without any access token
            end_users.delete_one({"number":number})
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Server error while creating new user")
    else:
        return {"status":status.HTTP_409_CONFLICT,"user":existing_user,"detail":"User already exists"}

@router.post("/login/{number}/{otp}",description="After sending otp, user will verify otp and new account will get created if not exists already. and token is created/refreshed")
# this function will verify otp send to the number and create account if not exists 
async def login_or_create_user(verification_status: dict = Depends(verify_otp)):
        try:
            # trying creating new user account 
            user_status = create_new_user(verification_status["number"])
            if user_status["status"] == 201: 
                return JSONResponse(status_code=user_status["status"],content={"detail":user_status["detail"],"token":user_status["token"].model_dump()})
            else:
                # renewing just access token beacuse user already exists 
                token_data = TokenData(id=str(user_status["user"]["_id"]),role=UserRoles.user)
                update = update_token(token_data)
                if(update["status"]):
                    return {"detail":"Logged in successfully","token":update["token"].model_dump()}
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=update["detail"])
        except ExpiredSignatureError as ex:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
        except ValidationError as ex:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))





        

