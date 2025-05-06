from datetime import datetime
from bson import ObjectId
from pymongo import DESCENDING
from models import QuestionModel
from utils import logger

class QuestionService:
    def getPack(id):
        return QuestionModel.findOne({"_id": id})

    def getPacks():
        return QuestionModel.findAll()
    
    def getUncompletedTasks(completed_models, theme):
        completed_models = completed_models or []
        ids = [ObjectId(str(model)) for model in completed_models if model]
        query = {
            "theme": ObjectId(str(theme["_id"]))
        }
        if ids:
            query["_id"] = {"$nin": ids}
        models = QuestionModel.findAll(query)
        return models
    
    def createPack(self, pack):
        new_pack = QuestionModel(
            theme=pack["theme"],
            questions=pack["questions"],
            difficult=0,
        )
        new_pack.save()
        return new_pack

    def getQuestionsByTheme(theme):
        query = {
            "theme": ObjectId(str(theme))
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
        user_theme_ids = user.get("picked_themes", [])
        completed_packs = user.get("completed_quizzes", [])
        
        theme_usage = {theme_id: 0 for theme_id in user_theme_ids}
        
        if completed_packs:
            packs = QuestionModel.findAll({"_id": {"$in": [ObjectId(pid) for pid in completed_packs]}})
            for pack in packs:
                theme_id = str(pack.get("theme"))
                if theme_id in theme_usage:
                    theme_usage[theme_id] += 1

        sorted_themes = sorted(theme_usage.items(), key=lambda x: x[1])

        return sorted_themes if sorted_themes else None