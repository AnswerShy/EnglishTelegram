from bson import ObjectId
from service import AIService, QuestionService
from models import QuestionModel
from utils import logger

class QuizController:
    def __init__(self):
        self.ai_service = AIService()

    def generate_quiz(self, history, theme):
        data = self.ai_service.getNewAiQuestion(history, theme["title"])
        if data: 
            return {
                "theme": ObjectId(theme["id"]),
                "questions": data
            }
        else:
            return "Failed to generate quiz data."

    def generate_themes(self, themes):
        data = self.ai_service.getNewAiThemes(themes)
        if data: 
            return data
        else:
            return "Failed to generate quiz data."

    def start_quiz(self, user):
        if user["active_session"] != None:
            pack = user["active_session"]["question_pack_id"]
            index = user["active_session"]["current_index"]

        completed_packs = user.get("completed_quizzes", [])
        uncompletedTasks = QuestionService.getUncompletedTasks(completed_packs)
        
        if not uncompletedTasks:
            return "🎉 You've completed all available quiz packs!"

        try:
            selected_pack_id = pack if pack else uncompletedTasks[0].get("_id") if uncompletedTasks else None
            selected_question_index = index if index else 0
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print(f"🔥 Exception occurred: {repr(ex)}")
            return "Something went wrong when starting the quiz."
        
        questions = QuestionService.getPack(selected_pack_id)

        if not questions:
            return "⚠️ Could not load the quiz. Try again later."
        
        return {
            "selected_pack_id": selected_pack_id,
            "options": {
                "text": questions["questions"][selected_question_index]["text"],
                "qeustions": questions["questions"][selected_question_index]["options"]
            }
        }
        
    def next_quiz(self, user):
        pack = user["active_session"].get("question_pack_id")
        index = user["active_session"].get("current_index") + 1
        questions = QuestionService.getPack(pack)["questions"]
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