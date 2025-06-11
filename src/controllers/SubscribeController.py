from models import DifficultModel, ThemeModel
from service import UserService
from utils import logger
from views.TelegramView import TelegramView

class SubscribeController:
    def __init__(self, telegramService):
        self.telegram = telegramService
        self.view = TelegramView()

    def subscribe_user(self, chatID, username=None):
        try:
            user = UserService.get_one(chatID)
            if not user or not user.picked_themes:
                UserService.subscribe_user(chatID, username)
                self.pick_themes_message(chatID)
                self.pick_difficult(chatID)
            else:
                UserService.subscribe_user(chatID, username)
                self.telegram.send_message(chatID, self.view.subscribe_message())
        except Exception as e:
            logger(f"{e}")

    def unsubscribe_user(self, chadID):
        UserService.unsubscribe_user(chadID)
        self.telegram.send_message(chadID, self.view.unsubscribe_message())

    def pick_themes_message(self, chatID, messageID=None):
        userPickedThemes = UserService.get_subscribed_themes(chatID)
        themes = ThemeModel.find_all()
        options = []
        for theme in themes:
            name = theme["theme_name"]
            id = str(theme["theme_id"])
            
            if id in userPickedThemes:
                display_name = f"{name} ✅"
            else:
                display_name = name
            options.append({ 'text': display_name, 'callback_data': f"theme_pick:{id}" })
        if messageID:
            self.telegram.send_message(chatID, self.view.pick_themes_message(), options, messageID)
        else:
            self.telegram.send_message(chatID, self.view.pick_themes_message(), options)

    def pick_difficult(self, chatID, messageID=None):
        user = UserService.get_one(chatID)
        userPickedDifficult = user.difficult if user else []
        userPickedDifficult = userPickedDifficult or []
        difficulties = DifficultModel.find_all()
        options = []
        for diff in difficulties:
            name = diff["diff_name"]
            id = str(diff["diff_id"])
            if id in userPickedDifficult:
                display_name = f"{name} ✅"
            else:
                display_name = name
            options.append({ 'text': display_name, 'callback_data': f"difficult_pick:{id}" })
        if messageID:
            self.telegram.send_message(chatID, self.view.pick_difficult(), options, messageID)
        else:
            self.telegram.send_message(chatID, self.view.pick_difficult(), options)
        
    def add_theme(self, chatID, themeID):
        return UserService.update_theme(chatID, themeID)
        
    def set_difficult(self, chatID, difficult):
        return UserService.update_difficult(chatID, difficult)