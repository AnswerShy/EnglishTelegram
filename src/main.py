from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, find_dotenv

from utils import logger
from views.TelegramView import TelegramView

os.environ.clear()
load_dotenv(find_dotenv())

from models import ThemeModel
from service import QuestionService, TelegramService, UserService
from controllers import BotController, QuizController, SubscribeController

serverData = {
    "offset": 0,
    "lastQuiz": 0
}

def main():
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        raise ValueError("Telegram Bot token is not provided. Set TELEGRAM_API_KEY in the .env file or pass it as an argument.")
    VeiwInstance = TelegramView()
    QuizControllerInstance = QuizController()
    TelegramServiceInstance = TelegramService(token)
    QuestionServiceInstance = QuestionService()
    ThemeServiceInstance = ThemeModel()
    SubscribeControllerInstance = SubscribeController(TelegramServiceInstance)
    bot = BotController(TelegramServiceInstance, QuizControllerInstance, SubscribeControllerInstance)
    lastPackTime = QuestionServiceInstance.getLastPackTime()

    while True:
        updateChecker = bot.handle_updates(offset=serverData["offset"])
        serverData["offset"] = updateChecker["offset"]
        data = bot.process_message(updateChecker)
        if data and data["type"] == "command":
            if data["command"] == 'sub':
                SubscribeControllerInstance.subscribeUser(data["chat_id"])
            elif data["command"] == 'unsub':
                SubscribeControllerInstance.unsubscribeUser(data["chat_id"])
            elif data["command"] == 'options':
                SubscribeControllerInstance.pickThemesMessage(data["chat_id"])
            elif data["command"] == 'stop':
                UserService.delete_session(data["chat_id"])
            elif data["command"] == 'test':
                user = UserService.getOne(data["chat_id"]).to_dict()

                if not user or not user.get("subscribed"):
                    TelegramServiceInstance.send_message(data["chat_id"], "❌ You must subscribe first with /subscribe.")
                elif not user.get("picked_themes"): 
                    TelegramServiceInstance.send_message(data["chat_id"], "❌ You must schoose themes first /options.")
                    
                active_session = user["active_session"]

                if active_session:
                    logger("form active session")
                    pack = QuestionService.getPack(user["active_session"]["question_pack_id"])
                    if pack:
                        quizData = QuizControllerInstance.start_quiz(user, pack)
                    else:
                        UserService.delete_session(data["chat_id"])
                else:
                    sortedUserThemesUsage = QuestionService.get_users_packs_usage(user)
                    theme = ThemeServiceInstance.pick_least_used_theme(sortedUserThemesUsage)
                    
                    completed_packs = user.get("completed_quizzes", [])
                    uncompletedTasks = QuestionService.getUncompletedTasks(completed_packs, theme)
                    if not uncompletedTasks:
                        TelegramServiceInstance.send_message(data["chat_id"], VeiwInstance.generatingProcess(theme["title"]))
                        
                        logger([sortedUserThemesUsage, theme["_id"]])
                        
                        newPack = QuizControllerInstance.generate_quiz(theme)
                        print(newPack)
                        quizData = QuizControllerInstance.start_quiz(user, newPack)
                    else:
                        pack = uncompletedTasks[0]
                        quizData = QuizControllerInstance.start_quiz(user, pack)
                        TelegramServiceInstance.send_message(data["chat_id"], VeiwInstance.StartingTheme(theme["title"]))

                if isinstance(quizData, str):
                    UserService.delete_session(data["chat_id"])
                    TelegramServiceInstance.send_message(data["chat_id"], quizData)
                else:
                    quizMessage = TelegramServiceInstance.send_message(data["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                    UserService.update_session(data["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"], quizData["options"].get("text"))
                
                if not active_session and theme and uncompletedTasks and len(uncompletedTasks) < 2:
                    print(theme and uncompletedTasks and len(uncompletedTasks) < 2)
                    newPack = QuizControllerInstance.generate_quiz(theme)

        if data and data["type"] == "callback":
            if data["command"] == 'theme_pick':
                changedTheme = SubscribeControllerInstance.addTheme(data["chat_id"], data["data"])
                SubscribeControllerInstance.pickThemesMessage(data["chat_id"], data["callback_message_id"])
                logger(f"{changedTheme}")
            if data["command"] == 'T' or data["command"] == 'F':
                user = UserService.getOne(data["chat_id"]).to_dict()
                if not user["active_session"]["last_question"] == data["callback_text"]:
                    TelegramServiceInstance.send_message(data["chat_id"], VeiwInstance.doNotRush())
                else:
                    TelegramServiceInstance.send_message(data["chat_id"], data["callback_text"], data["updated_reply_markup"], user["active_session"]["message_id"])
                    quizData = QuizControllerInstance.next_quiz(user)
                    if isinstance(quizData, bool):
                        if quizData == True:
                            UserService.pushCompletedTask(data["chat_id"], user["active_session"].get("question_pack_id"))
                            UserService.delete_session(data["chat_id"])
                            TelegramServiceInstance.send_message(data["chat_id"], VeiwInstance.endTest())
                        else:
                            TelegramServiceInstance.send_message(data["chat_id"], VeiwInstance.error())
                    else:
                        quizMessage = TelegramServiceInstance.send_message(data["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                        UserService.update_session(data["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"], quizData["options"].get("text"))
if __name__ == "__main__":
    main()
