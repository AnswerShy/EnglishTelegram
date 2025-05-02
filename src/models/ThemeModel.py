from pymongo import MongoClient
from bson import ObjectId
from .db import db

themes_collection = db['themes']

class ThemeModel:
    def __init__(self, title="", description="", _id=None):
        self.title = title
        self.description = description
        self._id = ObjectId(_id) if _id else None

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description
        }

    def save(self):
        result = themes_collection.insert_one(self.to_dict())
        self._id = result.inserted_id
        return self

    @classmethod
    def find_all(cls):
        data = list(themes_collection.find({}))
        array = []
        for theme in data:
            array.append(theme.get("title"))
        return array

    @classmethod
    def find_by_name(cls, name):
        return themes_collection.find_one({"name": name})
    
    @staticmethod
    def get_all_themes_with_count():
        pipeline = [
            {
                "$lookup": {
                    "from": "question_packs",
                    "localField": "_id",
                    "foreignField": "theme",
                    "as": "packs"
                }
            },
            {
                "$project": {
                    "title": 1,
                    "packCount": {"$size": "$packs"}
                }
            },
            {
                "$sort": {"packCount": 1}
            }
        ]
        return list(themes_collection.aggregate(pipeline))
    
    @staticmethod
    def pick_least_used_theme():
        themes = ThemeModel.get_all_themes_with_count()
        if themes:
            theme = themes[0]
            theme["id"] = str(theme["_id"])
            return theme
        return None