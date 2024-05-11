from fastapi import FastAPI
from .api.endpoints import auth , mapdirectory , user
app = FastAPI()
# loading env vars 
from dotenv import load_dotenv
load_dotenv()

app.include_router(auth.router)
app.include_router(mapdirectory.router)
app.include_router(user.router)
@app.get("/")
async def root():
    return {"status":"running"}