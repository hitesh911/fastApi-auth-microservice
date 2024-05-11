from fastapi import Depends, HTTPException,APIRouter,status
from fastapi.responses import JSONResponse

# local 
from app.db.mongo_db import otp_collection
from datetime import datetime, timedelta
from app.utils.third_party_apis import send_otp_sms
from app.utils.crypt import get_password_hash ,generate_random_otp
# buildins 
import os

router = APIRouter(prefix="/otp", tags=["Open operations"])



# routes 
@router.post("/sendotp/{number}",description="Primary task is to send otp to the user to verify it numbers authenticity")
async def send_otp(number: str):
    existing_record = otp_collection.find_one({"number": number})
    # Update the existing record with a new OTP and reset expiration time
    otp = str(generate_random_otp())
    # print(otp)
    # updating expiring time 
    expires_at = datetime.utcnow() + timedelta(minutes=int(os.getenv("OTP_EXPIRATION")))
    if existing_record:
        # check to not allow request for the next otp before 5 minutes 
        half_time_after_sending_otp = existing_record["expires_at"] - timedelta(minutes=(int(os.getenv("OTP_EXPIRATION"))-5))
        if(datetime.utcnow() < half_time_after_sending_otp ):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail=f"Can't generate new otp before {(half_time_after_sending_otp - datetime.utcnow()).seconds // 60} minutes")
        else:
            sms = send_otp_sms(otp,number)
            if sms["return"]:
                # updating otp and time 
                otp_collection.update_one(
                    {"number": number},
                    {"$set": {"otp": get_password_hash(otp), "expires_at": expires_at}}
                )
                return {"detail": "OTP updated successfully"} 
            else:
                raise HTTPException(status_code=sms["status_code"],detail=sms["message"])
    else:
        sms = send_otp_sms(otp,number)
        if sms["return"]:
            otp_data = {
                "number": number,
                "otp": get_password_hash(otp),
                "expires_at": expires_at,
            }
            otp_collection.insert_one(otp_data)
            return {"detail": "OTP sent successfully"}
        else:
            raise HTTPException(status_code=sms["status_code"],detail=sms["message"])
    

