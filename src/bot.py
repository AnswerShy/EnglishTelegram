import threading
import time
from dotenv import load_dotenv, find_dotenv
import os

from utils import logger
from views.TelegramView import TelegramView
from models import ThemeModel
from service import QuestionService, TelegramService, UserService
from controllers import BotController, QuizController, SubscribeController

def init_bot():
    load_dotenv(find_dotenv())
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        raise ValueError("TELEGRAM_API_KEY is not set")

    telegram_view = TelegramView()
    quiz_controller = QuizController()
    telegram_service = TelegramService(token)
    theme_service = ThemeModel()
    subscribe_controller = SubscribeController(telegram_service)
    bot_controller = BotController(telegram_service, quiz_controller, subscribe_controller)

    run_bot_loop(bot_controller, VeiwInstance=telegram_view, QuizControllerInstance=quiz_controller, TelegramBotController=bot_controller, ThemeServiceInstance=theme_service, SubscribeControllerInstance=subscribe_controller)

serverData = {
    "offset": 0,
    "lastQuiz": 0
}

def run_bot_loop(bot, VeiwInstance, QuizControllerInstance, TelegramBotController, ThemeServiceInstance, SubscribeControllerInstance):
    while True:
        try:
            updateChecker = bot.handle_updates(offset=serverData["offset"])
            serverData["offset"] = updateChecker["offset"]
            data = bot.process_message(updateChecker)

            if data and data["type"] == "command":
                logger(f"Bot: {data}")
                handle_command(data=data, SubscribeControllerInstance=SubscribeControllerInstance, TelegramBotController=TelegramBotController, QuizControllerInstance=QuizControllerInstance, VeiwInstance=VeiwInstance, ThemeServiceInstance=ThemeServiceInstance)
            elif data and data["type"] == "callback":
                handle_callback(data, SubscribeControllerInstance, TelegramBotController, VeiwInstance, QuizControllerInstance)
        
        except Exception as e:
            logger(f"Bot encountered an error: {e}")
            time.sleep(1)

def handle_command(data, SubscribeControllerInstance, TelegramBotController, QuizControllerInstance, ThemeServiceInstance, VeiwInstance):
    if data["command"] == 'subscribe':
        SubscribeControllerInstance.subscribe_user(data["chat_id"])
    elif data["command"] == 'unsubscribe':
        SubscribeControllerInstance.unsubscribe_user(data["chat_id"])
    elif data["command"] == 'options':
        SubscribeControllerInstance.pick_themes_message(data["chat_id"])
        SubscribeControllerInstance.pick_difficult(data["chat_id"])
    elif data["command"] == 'stop':
            UserService.delete_session(data["chat_id"])
    elif data["command"] == 'test':
        user = UserService.get_one(data["chat_id"])
        if not user or not user.subscribed:
            TelegramBotController.send_message(data["chat_id"], VeiwInstance.subscribe_first_message())
        elif not user.picked_themes or not user.difficult: 
            TelegramBotController.send_message(data["chat_id"], VeiwInstance.theme_and_difficulty_first_message())
        else:
            active_session = user.active_session
            if active_session:
                pack = QuestionService.getPack(user.active_session["question_pack_id"])
                if pack:
                    quizData = QuizControllerInstance.start_quiz(user, pack)
                else:
                    UserService.delete_session(data["chat_id"])
            else:
                sortedUserThemesUsage = QuestionService.get_users_packs_usage(user)
                theme = ThemeServiceInstance.pick_least_used_theme(sortedUserThemesUsage)
                
                completed_packs = user.completed_quizzes
                difficult = user.difficult
                uncompletedTasks = QuestionService.getUncompletedTasks(completed_packs, theme, difficult)

                if not uncompletedTasks:
                    TelegramBotController.send_message(data["chat_id"], VeiwInstance.generating_process_message(theme["title"]))
                    newPack = QuizControllerInstance.generate_quiz(theme, difficult)
                    quizData = QuizControllerInstance.start_quiz(user, newPack)
                else:
                    pack = uncompletedTasks[0]
                    quizData = QuizControllerInstance.start_quiz(user, pack)
                    TelegramBotController.send_message(data["chat_id"], VeiwInstance.starting_theme_message(theme["title"]))
            if isinstance(quizData, str):
                UserService.delete_session(data["chat_id"])
                TelegramBotController.send_message(data["chat_id"], quizData)
            else:
                quizMessage = TelegramBotController.send_message(data["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                UserService.update_session(data["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"], quizData["options"].get("text"))
            
            if not active_session and theme and uncompletedTasks and len(uncompletedTasks) < 2:
                def generate_second_quiz():
                    try:
                        logger(f"starting genereting new pack on second thread...")
                        QuizControllerInstance.generate_quiz(theme, difficult)
                    except Exception as e:
                        logger(f"Failed to pre-generate second quiz pack: {e}")
                threading.Thread(target=generate_second_quiz).start()

def handle_callback(data, SubscribeControllerInstance, TelegramBotController, VeiwInstance, QuizControllerInstance):
    if data["command"] == 'theme_pick':
        SubscribeControllerInstance.add_theme(data["chat_id"], data["data"])
        SubscribeControllerInstance.pick_themes_message(data["chat_id"], data["callback_message_id"])
    if data["command"] == 'difficult_pick':
        SubscribeControllerInstance.set_difficult(data["chat_id"], data["data"])
        SubscribeControllerInstance.pick_difficult(data["chat_id"], data["callback_message_id"])
    if data["command"] == 'T' or data["command"] == 'F':
        user = UserService.get_one(data["chat_id"])
        if user.active_session and not user.active_session["last_question"] == data["callback_text"]:
            TelegramBotController.send_message(data["chat_id"], VeiwInstance.do_not_rush_message())
        elif not user.active_session:
            TelegramBotController.send_message(data["chat_id"], VeiwInstance.no_test())
        else:
            quizData = QuizControllerInstance.next_quiz(user)

            textString = f'{data["callback_text"]}:\n\n{quizData["reason"] if quizData["reason"] else ""}'
            TelegramBotController.send_message(data["chat_id"], textString, data["updated_reply_markup"], user.active_session["message_id"])

            if isinstance(quizData["current"], bool):
                print(quizData["current"])
                if quizData["current"] == True:
                    UserService.push_completed_task(data["chat_id"], user.active_session.get("question_pack_id"))
                    UserService.delete_session(data["chat_id"])
                    TelegramBotController.send_message(data["chat_id"], VeiwInstance.end_test())
                else:
                    return
                    TelegramBotController.send_message(data["chat_id"], VeiwInstance.error())
            else:
                quizMessage = TelegramBotController.send_message(data["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                UserService.update_session(data["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"], quizData["options"].get("text"))