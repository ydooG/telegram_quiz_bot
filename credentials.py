# path to file with token
token_path = 'personal/telegram_bot_info.txt'

# path to google credentials file
credentials_path = 'personal/kfu-poll-telegram-bot-demo-02695a72148e.json'


def get_token():
    with open(token_path) as file:
        return file.readline().split('\n')[0]


TOKEN = get_token()
CREDENTIALS = open(credentials_path)

