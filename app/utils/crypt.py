from fastapi import HTTPException,status
from passlib.hash import sha256_crypt
import string , random


def get_password_hash(password:str):
    return sha256_crypt.using(rounds=23456).hash(password)

def _verify_password(plain_password :str, hashed_password:str):
    pas_status = sha256_crypt.verify(plain_password, hashed_password)
    if pas_status != True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong username password combination")


def generate_random_otp(length=6):
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp  # Generating a 6-digit OTP
