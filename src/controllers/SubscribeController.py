from models import ThemeModel
from service import UserService
from views.TelegramView import TelegramView

class SubscribeController:
    def __init__(self, telegramService):
        self.telegram = telegramService
        self.view = TelegramView()

    def subscribeUser(self, chatID, username=None):
        user = UserService.getOne(chatID).to_dict()
        if not user or not user.get("picked_themes"):
            self.pickThemesMessage(chatID)
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
            self.telegram.send_message(chatID, "Pick theme or themes to learn", options, messageID)
        else:
            self.telegram.send_message(chatID, "Pick theme or themes to learn", options)
        
    def addTheme(self, chatID, themeID):
        return UserService.updateTheme(chatID, themeID)