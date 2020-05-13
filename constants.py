# path to file with token and proxy
token_proxy_path = 'personal/telegram_bot_info.txt'

# path to google credentials file
credentials_path = 'personal/kfu-poll-telegram-bot-demo-02695a72148e.json'


def get_token():
    with open(token_proxy_path) as file:
        return file.readline().split('\n')[0]


def get_proxy():
    with open(token_proxy_path) as file:
        file.readline()
        return file.readline().split('\n')[0]


TOKEN = get_token()
PROXY = get_proxy()
CREDENTIALS = open(credentials_path)
