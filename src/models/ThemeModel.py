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
            array.append({'theme_name': theme["title"], 'theme_id': theme["_id"]})
        return array

    @classmethod
    def find_by_name(cls, name):
        return themes_collection.find_one({"name": name})

    def pick_least_used_theme(self, sorted_themes):
        for theme_id, _ in sorted_themes:
            theme = themes_collection.find_one({"_id": ObjectId(theme_id)})
            if theme:
                theme["id"] = str(theme["_id"])
                return theme
        return None