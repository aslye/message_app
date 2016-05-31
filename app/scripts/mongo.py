import pymongo

# api access
# https://mongolab.com/home
MONGODB_URI = '' 
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_default_database()

