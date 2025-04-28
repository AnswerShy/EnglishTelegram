import json
import os
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

prompt = """
    Згенеруй масив із 10 об'єктів для тестування знань з англійської мови на рівні Beginner у форматі:
    ```json
    [
    {
        "question": "Текст питання",
        "answers": ["варіант 1", "варіант 2", "варіант 3", "варіант 4"],
        "correctAnswer": "правильний варіант"
    }
    ]
    ```
    Формат відповіді — ЧИСТИЙ JSON, без додаткового тексту.
"""

class AIService:
    def __init__(self):
        self.url = os.getenv("AI_API_URL")
        self.key = os.getenv("AI_API_KEY")
        self.model = os.getenv("AI_API_MODEL")

    def get_questions(self):
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": f"{self.model}",
                "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
                ],
                
            })
        )
        data = response.json()
        return data.get('choices', [{}])[0].get('message', {}).get('content')