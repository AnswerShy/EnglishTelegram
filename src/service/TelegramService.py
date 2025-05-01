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

    def send_message(self, chat_id, text, options=None):
        # logger(f"Sending message #{message_id} to {chat_id}: {text}")
        url = self.base_url + "sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
        }
        
        if options:
            payload['reply_markup'] = json.dumps({
                'inline_keyboard': [[
                    {'text': opt['text'], 'callback_data': opt['callback_data']}
                    for opt in options
                ]]
            })
        
        response = requests.post(url, data=payload)
        data = response.json()
        # print (data)
        message_id = data['result']['message_id']

        return message_id

    def delete_message(self, chat_id, message_id):
        url = self.base_url + "deleteMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'message_id': message_id})

        logger(f"Delete message {message_id} to {chat_id}")
        return response.json()

    def edit_message(self, chat_id, message_id, text):
        url = self.base_url + "editMessageText"
        response = requests.post(url, data={'chat_id': chat_id, 'message_id': message_id, 'text': text})
        logger(f"Edit message {message_id} to {chat_id}: {text}")
        return response.json()
