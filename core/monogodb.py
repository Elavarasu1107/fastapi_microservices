from pymongo import MongoClient
from settings import settings

client = MongoClient(host=settings.mongo_host, port=settings.mongo_port)

db = client[settings.mongo_db_name]

User = db['user']
User.create_index(keys=['username'], unique=True)

Notes = db['notes']
Label = db['label']
