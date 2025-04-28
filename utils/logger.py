from datetime import datetime

class textColor:
    reset = '\x1b[0m'
    black = '\x1b[30m'
    red = '\x1b[31m'
    green = '\x1b[32m'
    yellow = '\x1b[33m'
    blue = '\x1b[34m'
    magenta = '\x1b[35m'
    cyan = '\x1b[36m'
    white = '\x1b[37m'
    gray = '\x1b[90m'

def logger(text):
    current_time = datetime.now().strftime('%H:%M:%S')
    colored_time = textColor.yellow + f'[{current_time}]' + textColor.reset + ' '
    text_message = text.split("\n")[0]

    print(colored_time + text_message)
