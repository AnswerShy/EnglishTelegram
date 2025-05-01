class TelegramView:
    def start_message(self):
        return "Привіт!\n\nЦе твій помічник у вивченні англійської мови. Хочеш вивчити нові слова?\n\nТо починай: /subscribe"
    
    def subscribe_message(self):
        return "Дякую за підписку!\n\nТепер ти отримаєш нові тести щодня. Готовий до вивчення? Молодець!\n\nЩоб відписатися, просто напиши /unsubscribe"
    
    def unsubscribe_message(self):
        return "Вже йдеш?\n\nЯкщо захочешь наново почати вирішувати задачки, ласкаво просимо\n\n/subscribe"
    
    def wrong_answer_message(self):
        return "Неправильно!\n\n" 

    def correct_answer_message(self):
        return "Молодець!\n\n" 