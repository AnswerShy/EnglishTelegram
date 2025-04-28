import os
from dotenv import load_dotenv, find_dotenv
os.environ.clear()
load_dotenv(find_dotenv())

from controllers.bot_controller import BotController
from dotenv import load_dotenv
from utils.logger import logger

def main():
    token = os.getenv("TELEGRAM_API_KEY")

    if not token:
        raise ValueError("Telegram Bot token is not provided. Set TELEGRAM_API_KEY in the .env file or pass it as an argument.")
    
    bot = BotController(token)
    logger("bot started")
    offset = 0

    while True:
        result = bot.handle_updates(offset)
        offset = result["offset"]
        if result["type"] == "message":
            chat_id = result["chat_id"]
            message_text = result["message_text"]
            bot.process_message(chat_id, message_text)

        elif result["type"] == "callback_query":
            chat_id = result["chat_id"]
            callback_data = result["callback_data"]
            bot.handle_answer(chat_id, callback_data)

if __name__ == "__main__":
    main()
