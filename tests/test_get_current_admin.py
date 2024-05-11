import os
from jose import jwt
from preprocessor import loadProject
loadProject()
from dotenv import load_dotenv
load_dotenv()

# from app.api.dependencies.dependencies import get_current_admin
from app.api.models.common import Token , TokenData

# new_token = Token(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1ZGM5MjBiYzA4ZDkxZTZhYTI1MTJlMiIsImV4cGlyZXNfYXQiOiIyMDI0LTAzLTA0VDEzOjI4OjQzLjIwNzkwNiswMDowMCIsInJvbGUiOiJhZG1pbiJ9.uF7Uwbc4SxPScRPIIHMN74UocZUoMdPMGvALH20AYcs",token_type="bearer")
# result = get_current_admin(new_token)
# for key,values in result.items():
#     print(f"{key} value is : {type(values)}")

from app.api.models.common import UsernamePasswordAuth, MobileNumberAuth , UserRoles
# auth_data = {"number":"12334"}
# obj = MobileNumberAuth(**auth_data)
# print(obj.number)
token_data = TokenData(expires_at=None,id="some",role=UserRoles.user)
print(token_data.model_dump())
encoded_jwt = jwt.encode(token_data.model_dump(), os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
payload = jwt.decode(encoded_jwt, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
print(payload)
