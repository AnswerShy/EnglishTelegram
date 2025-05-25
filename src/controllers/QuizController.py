from bson import ObjectId
from service import AIService, QuestionService
from models import QuestionModel
from utils import logger

class QuizController:
    def __init__(self):
        self.ai_service = AIService()

    def generate_quiz(self, theme, difficult=""):
        if theme:
            history = QuestionService.get_questions_by_theme_and_difficult(theme["id"], difficult)
        if difficult:
            difficult = QuestionService.get_difficult_name(difficult)
        logger([history, theme["title"], difficult])
        data = self.ai_service.get_new_ai_question(history, theme["title"], difficult["title"])
        if data: 
            data = QuestionService().createPack({
                "theme": ObjectId(theme["id"]),
                "questions": data,
                "difficult": difficult["_id"]
            }).to_dict()
            logger("End of generating test")
            return data
        else:
            return "Failed to generate quiz data."

    def generate_themes(self, themes):
        data = self.ai_service.get_new_ai_themes(themes)
        if data: 
            return data
        else:
            return "Failed to generate quiz data."

    def start_quiz(self, user, ready_pack):
        try:
            selected_pack_id = str(ready_pack.get("_id")) if ready_pack else None
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
        index = user["active_session"].get("current_index")
        indexNext = index + 1
        questions = QuestionService.getPack(pack)["questions"] if pack else []

        reason = questions[index].get("reason") or None

        if len(questions) == indexNext:
            return True
        if not questions:
            return False

        return {
            "current": indexNext,
            "selected_pack_id": pack,
            "options": {
                "text": questions[indexNext]["text"],
                "qeustions": questions[indexNext]["options"]
            },
            "reason": reason
        }