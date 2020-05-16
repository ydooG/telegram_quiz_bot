"""
for keyboard generation
"""
from models import Question


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


# for questions in
def get_questions(path):
    questions = []
    with open(path, 'r', encoding='utf8') as file:
        q = Question()
        q.variants = []
        i = 0
        for line in file:
            text = line.split("\n")[0][1:]
            if line.startswith('?'):
                q.text = text
            elif line.startswith('-'):
                q.variants.append(text)
                i += 1
            elif line.startswith('+'):
                q.answer_index = i
                q.variants.append(text)
            elif line.startswith('\n'):
                i = 0
                questions.append(q)
                q = Question()
                q.variants = []
    return questions


LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def get_letter_variants(n):
    return build_menu(LETTERS[:n], 2)


text = "asasd"
print(text.capitalize())