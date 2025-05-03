from models import UserModel

class UserService:
    def __init__(self, chat_id, questions):
        self.chat_id = chat_id
        self.questions = questions
        self.current_question_index = 0
        self.message_id = None

    def subscribe_user(chat_id, username=None):
        user = UserModel.find_one({"chat_id": chat_id})
        if user:
            UserModel.update_user(chat_id, {"subscribed": True})
            return False
        
        new_user = UserModel(
            chat_id=chat_id,
            name=username,
            experience=0,
            completed_quizzes=None,
            active_session=None
        )
        
        new_user.save()
        return True
    
    def unsubscribe_user(chat_id):
        return UserModel.update_user(chat_id, {"subscribed": False})
        
    def update_session(chat_id, packId, message_id, index=0, remove=False):
        active_session = {
            "question_pack_id": packId,
            "current_index": index,
            "wrong_answers": [],
            "message_id": message_id
        }
        if remove:
            UserModel.update_user(chat_id, {"$set": {"active_session": active_session}})
        else:
            return UserModel.update_user(chat_id, {"$set": {"active_session": active_session}})

    def pushCompletedTask(chat_id, task_id):
        return UserModel.update_user(chat_id, {"$push": {"completed_quizzes": task_id}})

    def getOne(chat_id):
        return UserModel.find_one({"chat_id": chat_id})