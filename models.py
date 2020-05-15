class Question:
    def __init__(self, text=None, variants=None, answer_index=None):
        self.text = text
        self.variants = variants
        self.answer_index = answer_index

    def __str__(self):
        return str(self.text) + "\n" + str(self.variants) + '\n' + str(self.answer_index)


class User:
    def __init__(self, name=None, surname=None, group=None):
        self.name = name
        self.surname = surname
        self.group = group
