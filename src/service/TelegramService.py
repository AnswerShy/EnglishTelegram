import json
import requests
from utils.logger import logger

class TelegramService:
    def __init__(self, token):
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset=None):
        url = self.base_url + "getUpdates"
        params = {'offset': offset, "timeout": 1000}
        response = requests.get(url, params=params)
        return response.json()
    
    """
        send_message
        explames:
            simple message:
                send_message(chat_id, "Hello world")
            message with inline keyboard:
                send_message(
                    chat_id=123456789,
                    text="What is the capital of France?",
                    options=[
                        {'text': 'Berlin', 'callback_data': 'wrong_answer'},
                    ]
                )
    """

    def send_message(self, chat_id, text, options=None, message_id=None):
        """
            Send Message
            Parameters:
                chat_id (int | str): The user's unique chat ID.
                text (str): Message Text.
                options (array): Array of options for keyboard
                    Example:
                    [{ 'text': 'text for button', 'callback_data': 'callback data' }]
                message_id (str): For editing message.
            Returns:
                Message ID (str)
        """
        if message_id:
            url = self.base_url + "editMessageText"
            payload = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
            }
        else:
            url = self.base_url + "sendMessage"            
            payload = {
                'chat_id': chat_id,
                'text': text,
            }
        if options:
            inline_keyboard = []
            short_buttons = []
            
            for opt in options:
                button = {'text': opt['text'], 'callback_data': opt['callback_data']}
                if len(opt['text']) < 6:
                    short_buttons.append(button)
                else:
                    inline_keyboard.append([button])

            if short_buttons:
                inline_keyboard.insert(0, short_buttons)

            payload['reply_markup'] = json.dumps({
                'inline_keyboard': inline_keyboard
            })


        response = requests.post(url, data=payload)
        data = response.json()
        if message_id:
            return message_id
        else:
            return data['result']['message_id']


    def delete_message(self, chat_id, message_id):
        url = self.base_url + "deleteMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'message_id': message_id})

        logger(f"Delete message {message_id} to {chat_id}")
        return response.json()
