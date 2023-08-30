from pymongo import MongoClient
from settings import settings

client = MongoClient(settings.mongo_host)

db = client[settings.mongo_db_name]

User = db['user']
User.create_index(keys=['username'], unique=True)

Notes = db['notes']
Label = db['label']
