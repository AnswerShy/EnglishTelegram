class UserService:
    def __init__(self, chat_id, questions):
        self.chat_id = chat_id
        self.questions = questions
        self.current_question_index = 0
        self.message_id = None

    def get_current_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        else:
            return None

    def move_to_next_question(self):
        self.current_question_index += 1
