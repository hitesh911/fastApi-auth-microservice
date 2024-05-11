from .mongo_config import sync_mongo_client , async_mongo_client
# -------------------------------databases -------------------------
# main database 
db = sync_mongo_client["MYeKIGAI"]
# database to store places of bettery swapping or charging stations . Note directory data could be very large to using async client to fetch data asyncronsly 
directory_db = async_mongo_client["Directory"]
# ------------creating collections ---------------

#collection to store generated otps for finite time frame
otp_collection = db["otp_collection"] 
# Create a Time to live index on the 'expires_at' field
index_key = [("expires_at", 1)]
index_options = {"expireAfterSeconds": 0}  # 0 means use the value from 'expires_at' field
otp_collection.create_index(index_key, **index_options)

# collections for different users
end_users = db["end_users"]
admins = db["admins"]
client_user = db["client_users"]
sub_client_user = db["sub_clients"]
policies = db["policies"]
client_policies = db["client_policies"]




# --------------------Collection to store places of battery swapping or charging stations -----------
places = directory_db["Places"]



