
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
        collection.find_one_and_update({"email": user["email"]}, {"$set": user})

    def delete_user(self, collection, user):
        collection.delete_one({"email": user.email})

    def get_user_by_valide_token(self, collection, token):
        user = collection.find_one({"validate_token": token})
        return user

    def get_user_by_guid(self, collection, guid):
        user = collection.find_one({"guid": guid})
        return user
    
    def set_user_as_verified(self, collection, user_guid):
        collection.update_one({"guid": user_guid}, {"$set": {"is_verified": True}})    

    def get_dict_property(self, dict, property, default):
        if property in dict:
            return dict[property]
        else:
            return default

    def get_serializable_user(self, user):
        return {
            "email": self.get_dict_property(user,"email",""),
            "guid": self.get_dict_property(user,"guid", ""),
            "is_verified": self.get_dict_property(user,"is_verified", False),
            "display_name": self.get_dict_property(user,"display_name", ""),
            "country": self.get_dict_property(user,"country", "CA")
        }
    
    
