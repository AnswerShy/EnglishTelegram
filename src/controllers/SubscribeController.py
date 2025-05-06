from models import DifficultModel, ThemeModel
from service import UserService
from views.TelegramView import TelegramView

class SubscribeController:
    def __init__(self, telegramService):
        self.telegram = telegramService
        self.view = TelegramView()

    def subscribeUser(self, chatID, username=None):
        user = UserService.getOne(chatID)
        if not user or not user.get("picked_themes"):
            UserService.subscribe_user(chatID, username)
            self.pickThemesMessage(chatID)
            self.pickDifficult(chatID)
        else:
            UserService.subscribe_user(chatID, username)
            self.telegram.send_message(chatID, self.view.subscribe_message())

    def unsubscribeUser(self, chadID):
        UserService.unsubscribe_user(chadID)
        self.telegram.send_message(chadID, self.view.unsubscribe_message())

    def pickThemesMessage(self, chatID, messageID=None):
        userPickedThemes = UserService.getSubscribedThemes(chatID)
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
            self.telegram.send_message(chatID, self.view.pickThemes(), options, messageID)
        else:
            self.telegram.send_message(chatID, self.view.pickThemes(), options)

    def pickDifficult(self, chatID, messageID=None):
        user = UserService.getOne(chatID)
        userPickedDifficult = user.to_dict().get("difficult") if user else []
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
            self.telegram.send_message(chatID, self.view.pickDifficult(), options, messageID)
        else:
            self.telegram.send_message(chatID, self.view.pickDifficult(), options)
        
    def addTheme(self, chatID, themeID):
        return UserService.updateTheme(chatID, themeID)
        
    def setDifficult(self, chatID, difficult):
        return UserService.updateDifficult(chatID, difficult)