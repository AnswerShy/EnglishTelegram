from datetime import datetime
from bson import ObjectId
from pymongo import DESCENDING

from utils import logger
from .db import db

question_packs_collection = db['question_packs']

class QuestionModel:
    def __init__(self, theme, difficult, questions, _id=None):
        self.theme = ObjectId(theme)
        self.questions = questions
        self.created_at = datetime.now()
        self.difficult = difficult
        self._id = ObjectId(_id) if _id else None
    
    @classmethod
    def from_dict(cls, data):
        model = cls(
            theme=data.get("theme"),
            questions=data.get("questions"),
            difficult=data.get("difficult", 0),
            _id=data.get("_id")
        )
        model.created_at = data.get("created_at", datetime.now())
        return model
    
    def to_dict(self):
        return {
            "theme": self.theme,
            "questions": self.questions,
            "difficult": self.difficult,
            "created_at": self.created_at
        }
    
    def save(self):
        result = question_packs_collection.insert_one(self.to_dict())
        self._id = result.inserted_id
        return self

    @classmethod
    def findOne(cls, query):
        data = question_packs_collection.find_one(query)
        return data
        return cls.from_dict(data) if data else None

    @classmethod
    def findlast(cls, query):
        data = question_packs_collection.find().sort("created_at", -1).limit(10)
        for document in data:
            return document.get("created_at")
    
    @staticmethod
    def findAllBy(query):
        return question_packs_collection.distinct(query)

    @classmethod
    def findAll(cls, query):
        cursor = question_packs_collection.find(query)
        return [data for data in cursor]
    
