from models import UserModel
from utils import logger

class UserService:
    def __init__(self, chat_id, questions):
        self.chat_id = chat_id
        self.questions = questions
        self.current_question_index = 0
        self.message_id = None

    def subscribe_user(chat_id, username=None):
        user = UserModel.find_one({"chat_id": chat_id})
        if user:
            UserModel.update_user(chat_id, {"$set": {"subscribed": True}})
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
        return UserModel.update_user(chat_id, {"$set": {"subscribed": False}})
        
    def update_session(chat_id, pack_id, message_id, index=0, last_question=""):
        """
            Update a user's session
            Parameters:
                chat_id (int | str): The user's unique chat ID.
                pack_id (str): pack id.
                message_id (str): last quiz message id.
                index (int): index of qestion.
                last_question (str): last question for addition check
            Returns:
                bool: True if the document was modified, False otherwise.
        """
        active_session = {
            "question_pack_id": pack_id,
            "current_index": index,
            "last_question": last_question,
            "wrong_answers": [],
            "message_id": message_id
        }
        logger(f"updating session... \v\r{active_session}")
        return UserModel.update_user(chat_id, {"$set": {"active_session": active_session}})

    def delete_session(chat_id,):
        return UserModel.update_user(chat_id, {"$set": {"active_session": []}})
            
    def update_theme(chat_id, theme_id):
        user = UserModel.find_one({"chat_id": chat_id})
        if user:
            user = user.to_dict()
        if user and theme_id in user["picked_themes"]:
            UserModel.update_user(chat_id, {"$pull": {"picked_themes": theme_id}})
            return False
        elif user:
            UserModel.update_user(chat_id, {"$push": {"picked_themes": theme_id}})
            return True
        return False

    def update_difficult(chat_id, difficult):
        return UserModel.update_user(chat_id, {"$set": {"difficult": difficult}})

    def get_subscribed_themes(chat_id):
        user = UserModel.find_one({"chat_id": chat_id})
        if not user or not user.to_dict()["picked_themes"]:
            return []
        else:
            return user.to_dict()["picked_themes"]

    def push_completed_task(chat_id, task_id):
        return UserModel.update_user(chat_id, {"$push": {"completed_quizzes": task_id}})

    def get_one(chat_id):
        return UserModel.find_one({"chat_id": chat_id}).to_dict()