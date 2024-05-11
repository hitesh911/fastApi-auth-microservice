from pydantic import BaseModel, ConfigDict
from bson import ObjectId
# local imports 
from app.api.models.common import ClientResources,ClientResourcesSets,PolicyActions


class PolicyRules(BaseModel):
    resouce: ClientResources
    set_of_resources: list | ClientResourcesSets
    actions: list[PolicyActions]
    
class Policy(BaseModel):
    name: str
    creator_id: str | None = None
    client_id: str|None =  None #Foreign key // It will be id of client 
    doc: list[PolicyRules]



class ClientPolicy(BaseModel):
    client_id: str
    policy_id: str
