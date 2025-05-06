from pymongo import MongoClient
from bson import ObjectId

from utils import logger
from .db import db

difficult_collection = db['difficults']

class DifficultModel:
    def __init__(self, title="", _id=None):
        self.title = title
        self._id = ObjectId(_id) if _id else None

    def to_dict(self):
        return {
            "title": self.title,
        }

    def save(self):
        result = difficult_collection.insert_one(self.to_dict())
        return result
    
    @classmethod
    def find_all(cls):
        data = list(difficult_collection.find({}))
        array = []
        for diff in data:
            array.append({'diff_name': diff["title"], 'diff_id': diff["_id"]})
        return array
    
    @classmethod
    def find(cls, id):
        query = {
            "_id": ObjectId(str(id))
        }
        data = difficult_collection.find_one(query)
        if data:
            return data
        return None