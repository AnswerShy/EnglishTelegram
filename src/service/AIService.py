import json
import os
import random
import re
from dotenv import load_dotenv, find_dotenv
import requests

from utils import logger

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
        logger("fetching new qestion pack")
        try:
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
        except Exception as e:
            print  (f"Error fetching AI question: {e}")
            return None

    def getNewAiQuestion(self):
        logger("Started generation new qestion pack")
        data = self.get_questions()
        return self.parse_ai_questions(data) if data else None
    
    @staticmethod
    def parse_ai_questions(ai_message):
        logger("parsing new qestion pack")
        try:
            match = re.search(r'```json\s*(.*?)\s*```', ai_message, re.DOTALL)
            
            if match:
                json_content = match.group(1)
            else:
                # print ("No JSON block found.")
                return None
            
            parsed = json.loads(json_content)

            quizzes = []
            for quiz in parsed:
                question_text = quiz.get('question', 'No question provided')
                answers = quiz.get('answers', quiz.get('answer', []))
                correct_answer = quiz.get('correctAnswer')

                options = []
                for i, answer in enumerate(answers):
                    isCorrect = 'T' if answer == correct_answer else 'F'
                    callback = f"{isCorrect}:{i}"
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
            print  (f"Error parsing AI question: {e}")
            return None