# path to file with token
TOKEN_PATH = 'personal/telegram_bot_info.txt'

# path to google credentials file
CREDENTIALS_PATH = 'personal/kfu-poll-telegram-bot-demo-02695a72148e.json'


def get_token():
    with open(TOKEN_PATH) as file:
        return file.readline().split('\n')[0]


TOKEN = get_token()

