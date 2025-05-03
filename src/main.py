from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, find_dotenv

os.environ.clear()
load_dotenv(find_dotenv())

from models import ThemeModel
from service import QuestionService, TelegramService
from controllers import BotController, QuizController

serverData = {
    "offset": 0,
    "lastQuiz": 0
}

def main():
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        raise ValueError("Telegram Bot token is not provided. Set TELEGRAM_API_KEY in the .env file or pass it as an argument.")
    QuizControllerInstance = QuizController()
    TelegramServiceInstance = TelegramService(token)
    QuestionServiceInstance = QuestionService()
    ThemeServiceInstance = ThemeModel()
    bot = BotController(TelegramServiceInstance, QuizControllerInstance)
    lastPackTime = QuestionServiceInstance.getLastPackTime()
    while True:
        now = datetime.now()
        if not lastPackTime or (now - lastPackTime) >= timedelta(hours=12):
            theme = ThemeServiceInstance.pick_least_used_theme()
            quesionts = QuestionService.getQuestionsByTheme(theme["title"])
            print(theme.get("title"), quesionts)
            newPack = QuizControllerInstance.generate_quiz(quesionts, theme)
            if isinstance(newPack, str):
                print(newPack)
            else:
                QuestionService().createPack(newPack)
                lastPackTime = now
        elif not lastPackTime or (now - lastPackTime) >= timedelta(hours=240):
            theme = ThemeServiceInstance.find_all()
            newThemes = QuizControllerInstance.generate_themes(theme)
            if not isinstance(newThemes, str):
                for data in newThemes:
                    new_theme = ThemeModel(
                        title=data,
                        description=f"{data} questions pack"
                    )
                    new_theme.save()
        updateChecker = bot.handle_updates(offset=serverData["offset"])
        serverData["offset"] = updateChecker["offset"]
        bot.process_message(updateChecker)

if __name__ == "__main__":
    main()
