import json
import random
import re
from service.UserService import UserService
from service.TelegramService import TelegramService
from service.AIService import AIService
from utils.logger import logger
from views.TelegramView import TelegramView

user_sessions = {}

class BotController:
    def __init__(self, token):
        self.telegram_service = TelegramService(token)
        self.view = TelegramView()
        self.ai_service = AIService()
    
    def start_quiz(self, chat_id):
        questions = self.getNewAiQuestion()
        session = UserService(chat_id, questions)
        user_sessions[chat_id] = session
        current_question = session.get_current_question()
        if current_question:
            message_id = self.telegram_service.send_message(
                chat_id=chat_id,
                text=current_question['text'],
                options=current_question['options']
            )
            session.message_id = message_id

    def handle_answer(self, chat_id, callback_data):
        session = user_sessions.get(chat_id)

        if not session:
            print(f"No active session for {chat_id}")
            return

        answer = callback_data

        if answer == "wrong_answer":
            self.wrong_answer(chat_id)
        else:
            self.correct_answer(chat_id)

        session.move_to_next_question()

        current_question = session.get_current_question()
        if current_question:
            message_id = self.telegram_service.send_message(
                chat_id=chat_id,
                text=current_question['text'],
                options=current_question['options']
            )
            session.message_id = message_id
        else:
            self.telegram_service.send_message(chat_id, "Quiz completed! 🎉")
            del user_sessions[chat_id]

    def handle_updates(self, offset=None):
        updates = self.telegram_service.get_updates(offset)
        if updates['result']:
            for update in updates['result']:
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message'].get('text')
                    return {
                        "offset": offset,
                        "type": "message",
                        "chat_id": chat_id,
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

    def process_message(self, chat_id, message_text):
        if message_text:
            message = message_text.lower()
            if message == '/start':
                self.telegram_service.send_message(chat_id, self.view.start_message())
            elif message == '/subscribe':
                self.telegram_service.send_message(chat_id, self.view.subscribe_message())
            elif message == '/unsubscribe':
                self.telegram_service.send_message(chat_id, self.view.unsubscribe_message())
            elif message == '/test':
                self.start_quiz(chat_id)
            else:
                logger(f"Unknown command: {message_text}")
                # return self.view.send_unknown_command_message()
    
    def wrong_answer(self, chat_id):
        self.telegram_service.send_message(chat_id, self.view.wrong_answer_message())

    def correct_answer(self, chat_id):
        self.telegram_service.send_message(chat_id, self.view.correct_answer_message())
        
    def getNewAiQuestion(self):
        data = self.ai_service.get_questions()
        return parse_ai_questions(data) if data else None


def parse_ai_questions(ai_message):
    try:
        print("ssssssssss")
        print(ai_message)
        match = re.search(r'```json\s*(.*?)\s*```', ai_message, re.DOTALL)
        
        if match:
            json_content = match.group(1)
        else:
            print("No JSON block found.")
            return None
        
        parsed = json.loads(json_content)

        quizzes = []
        for quiz in parsed:
            question_text = quiz.get('question', 'No question provided')
            answers = quiz.get('answers', quiz.get('answer', []))
            correct_answer = quiz.get('correctAnswer')

            options = []
            for answer in answers:
                callback = 'correct_answer' if answer == correct_answer else 'wrong_answer'
                options.append({
                    'text': answer,
                    'callback_data': callback
                })

            random.shuffle(options)

            quizzes.append({
                'text': question_text,
                'options': options
            })

        return quizzes
    
    except Exception as e:
        print(f"Error parsing AI question: {e}")
        return None
