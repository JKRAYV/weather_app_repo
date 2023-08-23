import pymongo

MONGO_URL = "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_URL)

weatherdb = client["WeatherDB"]
user = weatherdb["User"]

user.create_index([("username", pymongo.ASCENDING)], unique=True)
