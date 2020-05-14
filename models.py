class Question:
    def __init__(self, text=None, variants=None, answer=None):
        self.text = text
        self.variants = variants
        self.answer = answer

    def __str__(self):
        return str(self.text) + str(self.answer)


class User:
    def __init__(self, name=None, surname=None, group=None):
        self.name = name
        self.surname = surname
        self.group = group
