from fastapi import APIRouter , Depends , HTTPException,status
from app.api.models.user import EndUser
from app.api.dependencies.dependencies import get_current_user
from app.db.mongo_db import places


router = APIRouter(prefix="/places",tags=["Data Directory"],dependencies=[Depends(get_current_user)])

@router.get("/all",description="Get all the records of places of EV-chargers and swap stations")
async def all_places():
    all_places_cursor = places.find({})
    # iterating all the documents of cursor and parsing _id to string 
    documents_list = []
    async for document in all_places_cursor:
        document.update({"_id": str(document["_id"])})
        documents_list.append(document)
    return {"detail":"All data fetched","places":documents_list}