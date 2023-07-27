from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017)

db = client['fundoo_microservices']

User = db['user']
User.create_index(keys=['username'], unique=True)

Notes = db['notes']
Label = db['label']
