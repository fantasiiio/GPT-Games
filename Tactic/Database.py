
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

        
class Database:       
    def connect_mongo(self, collection_name):
        uri = "mongodb+srv://fgirard:tdk2hdD!@cluster0.5lvemwu.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        self.client = MongoClient(uri)
        db = self.client.BattleGrid
        collection = db[collection_name]
        return collection


    def get_user_by_email(self, collection, email):
        user = collection.find_one({"email": email})
        return user

    def create_user(self, collection, user):
        collection.insert_one(user)

    def update_user(self, collection, user):
        collection.find_one_and_update({"email": user.email}, {"$set": user})

    def delete_user(self, collection, user):
        collection.delete_one({"email": user.email})

    def get_user_by_valide_token(self, collection, token):
        user = collection.find_one({"validate_token": token})
        return user

    def get_user_by_guid(self, collection, guid):
        user = collection.find_one({"guid": guid})
        return user
