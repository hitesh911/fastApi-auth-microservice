from datetime import datetime , timezone
from fastapi import APIRouter, Depends,HTTPException,status
from bson import ObjectId

# Local imports 
from app.api.dependencies.dependencies import get_current_user
from app.api.dependencies.scheme import TokenValidationScheme
from app.api.models.user import EndUser
from app.api.models.common import Token
from app.db.mongo_db import end_users
from app.utils.token import decrypt_jwt_token,update_token
from app.utils.crypt import _verify_password, get_password_hash

# router 
router = APIRouter(prefix="/access",tags=["Access Management"])


@router.post("/setrefreshkey/{new_key}",description="Refresh key is used to renew jwt_token without verifying mobile number")
def set_refresh_key(new_key:str,old_key: str = "0",user: dict = Depends(get_current_user)):
    if(new_key.isdigit() and len(new_key) >= 4):
        _verify_password(old_key,user["refresh_key"])
        if user["refresh_key"] == "0":
            update_status = end_users.update_one({"_id":user["id"]},{"$set":{"refresh_key":get_password_hash(new_key)}})
            if update_status.modified_count > 0:
                # updated successfully 
                return {"detail":"Refresh key set successfully"}
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to update key")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Old key didn't match")
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Only numeric keys with minimun 4 digits are valid")
        


@router.post("/regeneratetoken/{refresh_key}",description="This to regenerate new  jwt token without verifying number directly through secret refresh key ")
def get_regenerated_token(refresh_key : str,token :Token=Depends(TokenValidationScheme())):
    # getting payload from jwt_token 
    payload = decrypt_jwt_token(token.access_token)
    if payload:
        current_user = end_users.find_one({"_id":ObjectId(payload["id"])})
        # first checking wheather token is in current user account 
        if(current_user["access_token"]["access_token"] == token.access_token):
            # Check if the token is not expired 
            expiration_datetime = datetime.fromisoformat(payload["expires_at"])
            if expiration_datetime < datetime.utcnow().replace(tzinfo=timezone.utc):
                # checking wheather user has settup the refresh key or not 
                if(current_user["refresh_key"] != "0"):
                    # verifying refreshkey 
                    _verify_password(refresh_key,current_user["refresh_key"])
                    result = update_token(current_user["_id"])
                    if(result["status"]):
                        return {"detail":result["detail"],"token":result["token"]}
                    else:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=result["detail"])
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Refresh key is not set for this user yet")
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN ,detail="Token is not expired yet, Can't renew before expiration")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials", )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials", )

