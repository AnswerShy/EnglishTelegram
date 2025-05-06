from bson import ObjectId
from service import AIService, QuestionService
from models import QuestionModel
from utils import logger

class QuizController:
    def __init__(self):
        self.ai_service = AIService()

    def generate_quiz(self, theme, difficult=0):
        if theme:
            history = QuestionService.getQuestionsByTheme(theme["id"])
        logger([history, theme["title"]])
        data = self.ai_service.getNewAiQuestion(history, theme["title"])
        if data: 
            return QuestionService().createPack({
                "theme": ObjectId(theme["id"]),
                "questions": data,
                "difficult": difficult
            })
        else:
            return "Failed to generate quiz data."

    def generate_themes(self, themes):
        data = self.ai_service.getNewAiThemes(themes)
        if data: 
            return data
        else:
            return "Failed to generate quiz data."

    def start_quiz(self, user, ready_pack):
        try:
            selected_pack_id = ready_pack.get("_id") if ready_pack else None
            selected_question_index = user["active_session"]["current_index"] if user["active_session"] else 0
        except Exception as ex:
            import traceback
            traceback.print_exc()
            logger(f"🔥 Exception occurred: {repr(ex)}")
            return "Something went wrong when starting the quiz."
        
        questions = ready_pack

        if not questions:
            return "⚠️ Could not load the quiz. Try again later."
        
        return {
            "current": selected_question_index,
            "selected_pack_id": selected_pack_id,
            "options": {
                "text": questions["questions"][selected_question_index]["text"],
                "qeustions": questions["questions"][selected_question_index]["options"]
            }
        }
        
    def next_quiz(self, user):
        pack = user["active_session"].get("question_pack_id")
        index = user["active_session"].get("current_index") + 1
        questions = QuestionService.getPack(pack)["questions"] if pack else []
        if len(questions) == index:
            return True
        if not questions:
            return False
        return {
            "current": index,
            "selected_pack_id": pack,
            "options": {
                "text": questions[index]["text"],
                "qeustions": questions[index]["options"]
            }
        }