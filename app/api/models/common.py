from typing import Optional
from datetime import datetime
from pydantic import BaseModel ,ConfigDict
from enum import Enum
class UserRoles(str, Enum):
    user = "user"
    admin = "admin"
    client = "client"
    sub_client = "sub-client"

class ClientResources(str,Enum):
    charging_station= "charging_stations"
    chargers = "chargers"
# these are the special resources set to represent like all charger, all stations etc
class ClientResourcesSets(str,Enum):
    all = "all"
class PolicyActions(str,Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"
    
class UsernamePasswordAuth(BaseModel):
    username: str
    password: str

class MobileNumberAuth(BaseModel):
    number: str 
    

class Token(BaseModel):
    access_token: str
    token_type: str
class  TokenData(BaseModel):
    # modifying pydantic model to accept other object types like ObjectId of pymongo (in this case)
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str | None = None  # id of user, client or admin
    expires_at: datetime | None = None
    role: UserRoles
    # making expires_at feild as string to make it json seriazable 
    # overriding BaseModel method model_dump 
    def model_dump(self, **kwargs):
        expires_at_str = None
        if self.expires_at:
            expires_at_str = self.expires_at.isoformat()

        basic_model_dump = super().model_dump(**kwargs)
        # changing objects in to string 
        basic_model_dump["expires_at"] = expires_at_str

        return basic_model_dump