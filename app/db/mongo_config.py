from motor import motor_asyncio as motor
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from dotenv import load_dotenv
import os
load_dotenv()
# MongoDB database Configuration
# Clients  
sync_mongo_client = MongoClient(os.getenv("MONGODB_URI"))
async_mongo_client = motor.AsyncIOMotorClient(os.getenv("MONGODB_URI"))

