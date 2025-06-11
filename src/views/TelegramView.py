class TelegramView:
    def start_message(self):
        return "Привіт!\n\nЦе твій помічник у вивченні англійської мови. Хочеш вивчити нові слова?\n\nТо починай: /subscribe\n\nСтворено студентом групи 4РП-08\n\nСтайкуца Максим | @voidStranger"
    
    def subscribe_message(self):
        return "Дякую за підписку!\n\nТепер ти отримаєш нові тести щодня. Готовий до вивчення? Молодець!\n\nЩоб відписатися, просто напиши /unsubscribe"
    
    def unsubscribe_message(self):
        return "Вже йдеш?\n\nЯкщо захочешь наново почати вирішувати задачки, ласкаво просимо\n\n/subscribe"
    
    def subscribe_first_message(self):
        return "❌ Спочатку треба підписатися!.\n\n/subscribe"

    def theme_and_difficulty_first_message(self):
        return "❌ Спочатку треба обрати теми та складність.\n\n/options."

    def wrong_answer_message(self):
        return "Неправильно!\n\n" 

    def correct_answer_message(self):
        return "Молодець!\n\n" 

    def end_test(self):
        return "🎉Вітаємо!\n\nТест завершено, чекайте на нові тести..." 

    def no_test(self):
        return "Схоже... тест неактивний 😭" 
    
    def error(self):
        return "Сталась якась помилка!\n\nСхоже, я трохи захворів🤒..." 
    
    def send_few_times_message(self):
        return "U cant answer in same question two times!!"
    
    def do_not_rush_message(self):
        return "Не спіши відповідати, встигнеш 😉"

    def starting_theme_message(self, theme: str):
        return f"Тема тесту: {theme}"

    def generating_process_message(self, theme: str):
        return f"Генеруємо тест на тему {theme}"
    
    @staticmethod
    def pick_difficult():
        return f"Обери складність питань"

    @staticmethod
    def pick_themes_message():
        return f"Обери теми для вивчення"