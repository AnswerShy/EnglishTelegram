import os
from dotenv import load_dotenv, find_dotenv

os.environ.clear()
load_dotenv(find_dotenv())

from models import QuestionModel
from service import UserService
from controllers import BotController, QuizController
from utils import logger
from views.TelegramView import TelegramView

serverData = {
    "offset": 0,
    "lastQuiz": 0
}

def main():
    token = os.getenv("TELEGRAM_API_KEY")

    if not token:
        raise ValueError("Telegram Bot token is not provided. Set TELEGRAM_API_KEY in the .env file or pass it as an argument.")

    bot = BotController(token)
    view = TelegramView()
    quiz_controller = QuizController()
    # newPack = quiz_controller.generate_quiz()
    # QuestionModel.create_pack(newPack.get("theme"), newPack.get("questions"))
    while True:
        updateChecker = bot.handle_updates(offset=serverData["offset"])
        # print (updateChecker)
        serverData["offset"] = updateChecker["offset"]
        processed = bot.process_message(updateChecker)
        if processed["type"] == "command":
            # print (processed["command"])
            if processed["command"] == "subscribe":
                UserService.subscribe_user(updateChecker["chat_id"], updateChecker["username"])
                bot.send_message(updateChecker["chat_id"], view.subscribe_message())
            elif processed["command"] == "unsubscribe":
                UserService.unsubscribe_user(updateChecker["chat_id"])
                bot.send_message(updateChecker["chat_id"], view.unsubscribe_message())
            elif processed["command"] == "startTest":
                user = UserService.getOne(updateChecker["chat_id"]).to_dict()
                if not user or not user.get("subscribed"):
                    bot.send_message(updateChecker["chat_id"], "❌ You must subscribe first with /subscribe.")
                # print (user)
                quizData = quiz_controller.start_quiz(user)
                print (quizData)
                if isinstance(quizData, str):
                    bot.send_message(updateChecker["chat_id"], quizData)
                else:
                    quizMessage = bot.send_message(updateChecker["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                    UserService.update_session(updateChecker["chat_id"], quizData["selected_pack_id"], quizMessage)
        elif processed["type"] == "callback":
            user = UserService.getOne(updateChecker["chat_id"]).to_dict()
            if processed["isCorrect"]:
                bot.send_message(updateChecker["chat_id"], view.correct_answer_message())
            else:
                bot.send_message(updateChecker["chat_id"], view.wrong_answer_message())
            quizData = quiz_controller.next_quiz(user)
            
            if isinstance(quizData, str):
                bot.send_message(updateChecker["chat_id"], quizData)
            else:
                quizMessage = bot.send_message(updateChecker["chat_id"], quizData["options"].get("text"), quizData["options"].get("qeustions"))
                UserService.update_session(updateChecker["chat_id"], quizData["selected_pack_id"], quizMessage, quizData["current"])


if __name__ == "__main__":
    main()
