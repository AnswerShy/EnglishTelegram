from service import TelegramService, UserService
from utils import logger
from views.TelegramView import TelegramView

class BotController:
    def __init__ (self, TGService, QuizController):
        self.telegram_service = TGService
        self.view = TelegramView()
        self.quiz_controller = QuizController

    def handle_updates(self, offset=None):
        updates = self.telegram_service.get_updates(offset)
        if updates['result']:
            for update in updates['result']:
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message'].get('text')
                    name = update['message']['chat']['first_name']
                    return {
                        "offset": offset,
                        "type": "message",
                        "chat_id": chat_id,
                        "username": name,
                        "message_text": message_text,
                        "callback_data": None
                    }
                
                elif 'callback_query' in update:
                    chat_id = update['callback_query']['message']['chat']['id']
                    callback_data = update['callback_query']['data']
                    callback_text = update['callback_query']['message']['text']
                    callback_questions = update['callback_query']['message']['reply_markup']
                    return {
                        "offset": offset,
                        "type": "callback_query",
                        "chat_id": chat_id,
                        "message_text": None,
                        "callback_data": callback_data,
                        "callback_text": callback_text,
                        "callback_questions": callback_questions,
                    }
        else:
            return {
                "offset": offset,
                "type": None,
                "chat_id": None,
                "message_text": None,
                "callback_data": None
            }
    
    def process_message(self, update):
        try:
            if update["type"] == "message":
                return self.handle_message(update["message_text"], update)
            elif update["type"] == "callback_query":
                return self.handle_callback(update["chat_id"], update["callback_data"], update["callback_text"], update["callback_questions"])
            return {
                "type": "unknown"
            }
        except Exception as e:
            return e

    def handle_message(self, message_text, data):
        if message_text:
            message = message_text.lower()
            result = {
                "type": "command",
                "command": None,
                "chat_id": data["chat_id"]
            }
            if message == '/start':
                self.send_message(data["chat_id"], self.view.start_message())
            elif message == '/subscribe':
                UserService.subscribe_user(data["chat_id"], data["username"])
                self.send_message(data["chat_id"], self.view.subscribe_message())
            elif message == '/unsubscribe':
                UserService.unsubscribe_user(data["chat_id"])
                self.send_message(data["chat_id"], self.view.unsubscribe_message())
            elif message == '/test':
                user = UserService.getOne(data["chat_id"]).to_dict()
                if not user or not user.get("subscribed"):
                    self.send_message(data["chat_id"], "❌ You must subscribe first with /subscribe.")
                quizData = self.quiz_controller.start_quiz(user)
                if isinstance(quizData, str):
                    self.send_message(data["chat_id"], quizData)
                else:
                    quizMessage = self.send_message(data["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                    UserService.update_session(data["chat_id"], quizData["selected_pack_id"], quizMessage)
            else:
                self.send_message(data["chat_id"], "dsa")
                logger(f"Unknown command: {message_text}")
            return result

    def handle_callback(self, chat_id, callback_data, callback_text, callback_options):
        correctness_flag, pressed_index = callback_data.split(":")
        pressed_index = int(pressed_index)

        is_correct = correctness_flag == "T"
        
        original_buttons = callback_options['inline_keyboard']
        updated_buttons = []
        
        for row in original_buttons:
            for button in row:
                new_text = button['text']
                new_callback = button['callback_data']
                if new_callback == callback_data:
                    new_text += " ✅" if is_correct else " ❌"
                updated_buttons.append({"text": new_text, "callback_data": new_callback})

        updateChecker = {
            "type": "callback",
            "isCorrect": is_correct,
            "chat_id": chat_id,
            "callback_text": callback_text,
            "updated_reply_markup": updated_buttons,
            "pressed_index": pressed_index
        }
        
        user = UserService.getOne(updateChecker["chat_id"]).to_dict()
        if updateChecker["isCorrect"]:
            logger(f"correct!")
        else:
            logger(f"wrong!")
        print(updateChecker["chat_id"], user["active_session"]["message_id"], updateChecker["callback_text"], updateChecker["updated_reply_markup"])
        self.editMessage(updateChecker["chat_id"], user["active_session"]["message_id"], updateChecker["callback_text"], updateChecker["updated_reply_markup"])
        quizData = self.quiz_controller.next_quiz(user)
        if isinstance(quizData, str):
            self.send_message(updateChecker["chat_id"], quizData)
        else:
            quizMessage = self.send_message(updateChecker["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
            UserService.update_session(updateChecker["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"])

    def send_message(self, chat_id, message, options=None):
        return self.telegram_service.send_message(chat_id, message, options)
    
    def editMessage(self, chat_id, message_id, message, options=None):
        self.telegram_service.send_message(chat_id, message, options, message_id)