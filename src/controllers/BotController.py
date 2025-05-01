from service import TelegramService
from utils import logger
from views.TelegramView import TelegramView

class BotController:
    def __init__ (self, token):
        self.telegram_service = TelegramService(token)
        self.view = TelegramView()

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
                    return {
                        "offset": offset,
                        "type": "callback_query",
                        "chat_id": chat_id,
                        "message_text": None,
                        "callback_data": callback_data
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
        if update["type"] == "message":
            return self.handle_message(update["chat_id"], update["message_text"])
        elif update["type"] == "callback_query":
            return self.handle_callback(update["chat_id"], update["callback_data"])
        return {
            "type": "unknown"
        }

    def handle_message(self, chat_id, message_text):
        if message_text:
            message = message_text.lower()
            
            result = {
                "type": "command",
                "command": None,
                "chat_id": chat_id
            }

            if message == '/start':
                self.telegram_service.send_message(chat_id, self.view.start_message())
            elif message == '/subscribe':
                result["command"] = "subscribe"
            elif message == '/unsubscribe':
                result["command"] = "unsubscribe"
                self.telegram_service.send_message(chat_id, self.view.unsubscribe_message())
            elif message == '/test':
                result["command"] = "startTest"
            else:
                self.telegram_service.send_message(chat_id, "dsa")
                logger(f"Unknown command: {message_text}")
            
            return result

    def handle_callback(self, chat_id, callback_data):
        answer = callback_data
        
        result = {
            "type": "callback",
            "isCorrect": None,
            "chat_id": chat_id
        }

        if answer == "wrong_answer":
            result["isCorrect"] = False
        else:
            result["isCorrect"] = True
        
        return result

    def send_message(self, chat_id, message, options=None):
        self.telegram_service.send_message(chat_id, message, options)