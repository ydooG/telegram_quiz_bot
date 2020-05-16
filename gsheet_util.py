import gspread
from credentials import CREDENTIALS_PATH
from models import User

gc = gspread.service_account(CREDENTIALS_PATH)
spreadsheet = gc.open('poll-bot-data')
worksheet = spreadsheet.worksheets()[0]


def _next_available_row(ws):
    str_list = list(filter(None, ws.col_values(1)))
    return len(str_list)+1


def write_user(user: User):
    n = _next_available_row(worksheet)
    name = 'Неизвестно' if user.name is None else user.name
    surname = 'Неизвестно' if user.surname is None else user.surname
    group = 'Неизвестно' if user.group is None else user.group
    worksheet.update_cell(n, 1, name)
    worksheet.update_cell(n, 2, surname)
    worksheet.update_cell(n, 3, group)
    worksheet.update_cell(n, 4, user.points)
    for i in range(len(user.answers)):
        worksheet.update_cell(n, i+5, user.answers[i])
