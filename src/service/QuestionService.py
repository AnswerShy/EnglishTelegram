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
    
    def getUncompletedTasks(completed_models):
        completed_models = completed_models or []
        ids = [ObjectId(str(model)) for model in completed_models if model]
        query = {"_id": {"$nin": ids}} if ids else {}
        models = QuestionModel.findAll(query)
        return models
    
    def createPack(self, pack):
        new_pack = QuestionModel(
            theme=pack["theme"],
            questions=pack["questions"],
            difficult=0,
        )
        new_pack.save()

    def getQuestionsByTheme(theme):
        packs = QuestionModel.findAll({"theme": theme})
        if packs:
            packs = packs.get("questions", [])
            all_questions = []

            for question in packs:
                question_text = question.get("text")
                if question_text:
                    all_questions.append(question_text)

            return all_questions
        else:
            return []


    def getLastPackTime(self):
        data = QuestionModel.findlast({})
        return data