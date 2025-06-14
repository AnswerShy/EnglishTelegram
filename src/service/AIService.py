import json
import os
import random
import re
from dotenv import load_dotenv, find_dotenv
import requests

from utils import logger

load_dotenv(find_dotenv())

def build_theme_prompt(themes):
    themeData = f"Не повторюй такі як: {json.dumps(themes, ensure_ascii=False, indent=2)}" if themes else ""
    return f"""
    Згенеруй масив із 10 унікальних тем для тестування знань з англійської мови.
    Кожна тема повинна бути короткою (1-3 слова) і зрозумілою (наприклад: "Подорожі", "Інтернет", "Кіно", "Ресторан").
    
    Формат відповіді — ЧИСТИЙ JSON масив рядків:
    [
        "тема1",
        "тема2",
        ...
    ]
    {themeData}
    """

def build_quiz_prompt(history, theme, difficult):
    themeData = theme if theme else "IT"
    difficultData = difficult if difficult else "Begginer"
    historyData = f"Не повторюй такі питання: {json.dumps(history, ensure_ascii=False, indent=2)}" if history else ""
    return f"""
        Згенеруй масив із 10 об'єктів для тестування знань з англійської мови на рівні {difficultData} на тему {themeData} у форматі:
        ```json
        [
        {{
            "question": "Текст питання",
            "answers": ["варіант 1", "варіант 2", "варіант 3", "варіант 4"],
            "correctAnswer": "правильний варіант",
            "reasonOfAnswer": "аргументована відповіть чому відповідь саме така"
        }}
        ]
        ```
        {historyData}
        Формат відповіді — ЧИСТИЙ JSON, без додаткового тексту.
    """

class AIService:
    def __init__(self):
        self.url = os.getenv("AI_API_URL")
        self.key = os.getenv("AI_API_KEY")
        self.model = os.getenv("AI_API_MODEL")

    def get_questions(self, prompt):
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
            data = response.json().get('choices', [{}])[0].get('message', {}).get('content')
            logger(data)
            return data
        except Exception as e:
            logger(f"Error fetching AI question: {e}")
            return None

    def get_new_ai_question(self, history, theme, difficult):
        logger(f"Started generation new qestion pack: theme={theme} difficult={difficult}")
        prompt = build_quiz_prompt(history, theme, difficult)
        data = self.get_questions(prompt)
        return self.parse_ai_questions(data) if data else None
    
    def get_new_ai_themes(self, themes):
        logger("Started generation new themes")
        prompt = build_theme_prompt(themes)
        data = self.get_questions(prompt)
        return self.parse_ai_themes(data) if data else None

    @staticmethod
    def parse_ai_questions(ai_message):
        logger("parsing new qestion pack")
        try:
            match = re.search(r'```json\s*(.*?)\s*```', ai_message, re.DOTALL)
            
            if match:
                json_content = match.group(1)
            else:
                logger("No JSON block found.")
                return None
            
            parsed = json.loads(json_content)

            quizzes = []
            for quiz in parsed:
                question_text = quiz.get('question', 'No question provided')
                answers = quiz.get('answers', quiz.get('answer', []))
                correct_answer = quiz.get('correctAnswer')
                reason = quiz.get('reasonOfAnswer')

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
                    'options': options,
                    'reason': reason
                })
            
            return quizzes
        
        except Exception as e:
            logger(f"Error parsing AI question: {e}")
            return None

    @staticmethod
    def parse_ai_themes(ai_message):
        logger("parsing new themes")
        try:
            match = re.search(r'```json\s*(.*?)\s*```', ai_message, re.DOTALL)
            
            if match:
                json_content = match.group(1)
            else:
                logger("No JSON block found.")
                return None
            
            try:
                themes = json.loads(json_content)
                if isinstance(themes, list) and all(isinstance(t, str) for t in themes):
                    return themes
                else:
                    raise ValueError("AI response is not a valid list of strings")
            except json.JSONDecodeError as e:
                logger(f"JSON decode error: {e}")
            except Exception as e:
                logger(f"Error parsing AI themes: {e}")
            return []
        
        except Exception as e:
            logger(f"Error parsing AI question: {e}")
            return None