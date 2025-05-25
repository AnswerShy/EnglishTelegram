from service import TelegramService, UserService
from utils import logger
from views.TelegramView import TelegramView

class BotController:
    def __init__ (self, TGService, QuizController, SubscribeController):
        self.telegram_service = TGService
        self.view = TelegramView()
        self.quiz_controller = QuizController
        self.sc = SubscribeController

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
                    callback_message_id = update['callback_query']['message']['message_id']
                    return {
                        "offset": offset,
                        "type": "callback_query",
                        "chat_id": chat_id,
                        "message_text": None,
                        "callback_data": callback_data,
                        "callback_text": callback_text,
                        "callback_questions": callback_questions,
                        "callback_message_id": callback_message_id
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
                return self.handle_callback(update["chat_id"], update["callback_data"], update["callback_text"], update["callback_questions"], update["callback_message_id"])
            return {
                "type": "unknown"
            }
        except Exception as e:
            logger(f"error: {e}")
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
                result["command"] = 'sub'
                return result
            elif message == '/unsubscribe':
                result["command"] = 'unsub'
                return result
            elif message == '/options':
                result["command"] = 'options'
                return result
            elif message == '/stop':
                result["command"] = 'stop'
                return result
            elif message == '/test':
                result["command"] = 'test'
                return result
            else:
                self.send_message(data["chat_id"], "Unknown command")
                logger(f"Unknown command: {message_text}")
            return result

    def handle_callback(self, chat_id, callback_data, callback_text, callback_options, callback_message_id):
        correctness_flag, pressed_index = callback_data.split(":")
        if correctness_flag == "theme_pick":
            return {
                "type": "callback",
                "command": correctness_flag,
                "data": pressed_index,
                "chat_id": chat_id,
                "callback_message_id": callback_message_id
            }
        elif correctness_flag == "difficult_pick":
            return {
                "type": "callback",
                "command": correctness_flag,
                "data": pressed_index,
                "chat_id": chat_id,
                "callback_message_id": callback_message_id
            }
        elif correctness_flag == "T" or correctness_flag == "F":
            pressed_index = int(pressed_index)
            is_correct = correctness_flag == "T"
            original_buttons = callback_options['inline_keyboard']
            updated_buttons = []
            for row in original_buttons:
                for button in row:
                    if "✅" in button['text'] or "❌" in button['text']:
                        self.send_message(chat_id, self.view.send_few_times_message())
                        return
                    new_text = button['text']
                    new_callback = button['callback_data']
                    if new_callback == callback_data:
                        new_text += " ✅" if is_correct else " ❌"
                    updated_buttons.append({"text": new_text, "callback_data": new_callback})
            return {
                "type": "callback",
                "command": correctness_flag,
                "isCorrect": is_correct,
                "chat_id": chat_id,
                "callback_text": callback_text,
                "updated_reply_markup": updated_buttons,
                "pressed_index": pressed_index
            }

    def send_message(self, chat_id, text, options=None, message_id=None):
        return self.telegram_service.send_message(chat_id, text, options, message_id)

    def edit_message(self, chat_id, message_id, message, options=None):
        self.telegram_service.send_message(chat_id, message, options, message_id)
