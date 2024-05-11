import os
from fastapi import APIRouter, Depends, HTTPException,status
from jose import JWTError , jwt
from pydantic import ValidationError
from app.api.dependencies.dependencies import get_current_client
from app.api.dependencies.scheme import TokenValidationScheme
from app.api.models.common import Token, UserRoles

from app.utils.common import _set_owner_and_get_creator, _validate_token_not_expired
from app.api.models.policy import Policy
from app.db.mongo_db import policies
token_validation_scheme = TokenValidationScheme()
router = APIRouter(prefix="/policy",tags=["Auth"])

@router.post("/create")
def create_new_policy(new_policy: Policy,token: Token = Depends(token_validation_scheme)):
    try:
        payload = JWTError.decode(token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        _validate_token_not_expired(payload)
        creator,new_policy = _set_owner_and_get_creator(payload,new_policy,token)
        # adding creator id to new policy 
        new_policy.creator_id = str(creator["_id"])
        policies.insert_one(new_policy.model_dump())
        return {"hello":"world"}
    except jwt.ExpiredSignatureError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ex))
    except ValidationError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

