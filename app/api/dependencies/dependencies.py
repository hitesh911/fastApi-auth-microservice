from fastapi import Depends, HTTPException, status
from bson import ObjectId
from typing import Annotated

# buitins 
from datetime import datetime,timezone
import os
from jose import jwt,JWTError,ExpiredSignatureError
from bson import ObjectId

# Locals 
from app.api.models.common import Token
from app.api.models.user import EndUser
from app.api.models.client import ClientUser
from app.api.dependencies.scheme import TokenValidationScheme
from app.db.mongo_db import end_users , client_user , admins,sub_client_user
from app.api.models.common import UserRoles
from app.utils.token import token_expired


from app.utils.crypt import _verify_password
from app.db.mongo_db import otp_collection,end_users

token_validation_scheme = TokenValidationScheme()



        
def get_current_user(token: Annotated[Token,Depends(token_validation_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        # Decode the token
        payload = jwt.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # Check if the token is expired
        if token_expired(payload):
            raise ExpiredSignatureError("Token has expired")
        else:
            # checking if role is correct
            if(payload["role"] == UserRoles.user):
                return end_users.find_one({"_id": ObjectId(payload["id"])})
            else:
                raise credentials_exception

    except JWTError as e:
        raise credentials_exception from e
def get_current_admin(token: Annotated[Token,Depends(token_validation_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        # Decode the token
        payload = jwt.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # Check if the token is expired
        if token_expired(payload):
            raise ExpiredSignatureError("Token has expired")
        else:
            # checking if role is correct
            if(payload["role"] == UserRoles.admin):
                return admins.find_one({"_id": ObjectId(payload["id"])})
            else:
                raise credentials_exception

    except JWTError as e:
        raise credentials_exception from e
def get_current_client(token: Annotated[Token,Depends(token_validation_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        # Decode the token
        payload = jwt.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # Check if the token is expired
        if token_expired(payload):
            raise ExpiredSignatureError("Token has expired")
        else:
            # checking if role is correct
            if(payload["role"] == UserRoles.client):
                return client_user.find_one({"_id": ObjectId(payload["id"])})
            else:
                raise credentials_exception

    except JWTError as e:
        raise credentials_exception from e
    
def get_current_sub_client(token: Annotated[Token,Depends(token_validation_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        # Decode the token
        payload = jwt.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # Check if the token is expired
        if token_expired(payload):
            raise ExpiredSignatureError("Token has expired")
        else:
            # checking if role is correct
            if(payload["role"] == UserRoles.sub_client):
                return sub_client_user.find_one({"_id": ObjectId(payload["id"])})
            else:
                raise credentials_exception

    except JWTError as e:
        raise credentials_exception from e

def _check_number_with_otp_exists(number):
    existing_record = otp_collection.find_one({"number": number})
    if(existing_record):
        return existing_record
    else:
        raise HTTPException(status_code=404, detail="Otp expired either not generated. Please re-send and try again")

def verify_otp(number: str, otp: str):
    try:
        otp_data = _check_number_with_otp_exists(number)
        _verify_password(str(otp),otp_data["otp"])
        # Delete OTP record after successful verification
        otp_collection.delete_one({"_id": otp_data["_id"]})
        return {"detail":"otp verified successfully","number":number}
    except HTTPException as ex:
        return ex
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
