from datetime import datetime
from bson import ObjectId
from pymongo import DESCENDING
from models import DifficultModel, QuestionModel
from utils import logger

class QuestionService:
    def getPack(id):
        return QuestionModel.findOne({"_id": ObjectId(id)})

    def getPacks():
        return QuestionModel.findAll()
    
    def getUncompletedTasks(completed_models, theme, difficult):
        completed_models = completed_models or []
        ids = [ObjectId(str(model)) for model in completed_models if model]
        query = {
            "theme": ObjectId(str(theme["_id"])),
            "difficult": ObjectId(str(difficult)),
        }
        if ids:
            query["_id"] = {"$nin": ids}
        models = QuestionModel.findAll(query)
        return models
    
    def createPack(self, pack):
        new_pack = QuestionModel(
            theme=pack["theme"],
            questions=pack["questions"],
            difficult=pack["difficult"]
        )
        new_pack.save()

        saved = QuestionModel.findOne({
            "theme": pack["theme"],
            "difficult": pack["difficult"],
            "questions": pack["questions"]
        })
        
        return saved

    def get_questions_by_theme_and_difficult(theme, difficult):
        query = {
            "theme": ObjectId(str(theme)),
            "difficult": ObjectId(str(difficult)),
        }
        packs = QuestionModel.findAll(query)
        all_questions = []
        if packs:
            for pack in packs:
                questions = pack.get("questions", [])
                for question in questions:
                    question_text = question.get("text")
                    if question_text:
                        all_questions.append(question_text)
            return all_questions
        else:
            return []

    def getLastPackTime(self):
        data = QuestionModel.findlast({})
        return data
    
    @staticmethod
    def get_users_packs_usage(user):
        user_theme_ids = user.picked_themes
        completed_packs = user.completed_quizzes
        
        theme_usage = {theme_id: 0 for theme_id in user_theme_ids}
        
        if completed_packs:
            packs = QuestionModel.findAll({"_id": {"$in": [ObjectId(pid) for pid in completed_packs]}})
            for pack in packs:
                theme_id = str(pack.get("theme"))
                if theme_id in theme_usage:
                    theme_usage[theme_id] += 1

        sorted_themes = sorted(theme_usage.items(), key=lambda x: x[1])

        return sorted_themes if sorted_themes else None
    
    @staticmethod
    def get_difficult_name(id):
        return DifficultModel().find(id)