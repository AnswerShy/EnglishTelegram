from bson import ObjectId
from models import QuestionModel
from utils import logger

class QuestionService:
    def getPack(id):
        return QuestionModel.findOne({"_id": id})

    def getPacks():
        return QuestionModel.findAll()
    
    def getUncompletedTasks(completed_models):
        completed_models = completed_models or []
        ids = [ObjectId(str(model._id)) for model in completed_models if model and model._id]
        
        query = {"_id": {"$nin": ids}} if ids else {}

        return QuestionModel.findAll(query)


    
    def createPack(pack):
        new_pack = QuestionModel(
            theme=pack["theme"],
            questions=pack["questions"],
        )
        new_pack.save()