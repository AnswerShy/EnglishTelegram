from pymongo import MongoClient
from bson import ObjectId
from .db import db

users_collection = db['users']

class UserModel:
    def __init__(self, chat_id, name, experience=0, completed_quizzes=None, active_session=None, _id=None):
        self.chat_id = chat_id
        self.name = name
        self.experience = experience
        self.subscribed = True
        self.completed_quizzes = completed_quizzes
        self.active_session = active_session
        self._id = ObjectId(_id) if _id else None
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            chat_id=data["chat_id"],
            name=data.get("name"),
            experience=data.get("experience", 0),
            completed_quizzes=data.get("completed_quizzes"),
            active_session=data.get("active_session"),
            _id=data.get("_id")
        )

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "name": self.name,
            "experience": self.experience,
            "completed_quizzes": self.completed_quizzes,
            "active_session": self.active_session,
            "subscribed": self.subscribed
        }

    @classmethod
    def find_one(cls, query):
        data = users_collection.find_one(query)
        return cls.from_dict(data) if data else None

    def save(self):
        result = users_collection.insert_one(self.to_dict())
        self._id = result.inserted_id
        return self

    @classmethod
    def update_user(cls, chat_id, update_fields):
        """
            Update a user's data in the users collection.
            Parameters:
                chat_id (int | str): The user's unique chat ID.
                update_fields (dict): A MongoDB update operator and its corresponding fields.
                    Example formats:
                        {"$set": {"key": value}}       # Set field(s)
                        {"$addToSet": {"key": value}}  # Add to array, avoiding duplicates
                        {"$push": {"key": value}}      # Append to array
            Returns:
                bool: True if the document was modified, False otherwise.
        """
        result = users_collection.update_one(
            {"chat_id": chat_id},
            update_fields
        )
        return result.modified_count > 0
