from datetime import datetime
import inspect

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
    
    frame = inspect.stack()[1]
    filename = frame.filename
    lineno = frame.lineno
    
    colored_time = textColor.yellow + f'[{current_time}]' + textColor.reset + ' '
    file_info = textColor.gray + f'[{filename}:{lineno}]' + textColor.reset + ' '
    text_message = ""
    if isinstance(text, str):
        text_message = text.split("\n")[0]
    elif isinstance(text, int):
        text_message = str(text)
    else:
        for i, a in enumerate(text):
            color = textColor.gray if i % 2 == 0 else textColor.white
            text_message += f"{color}{str(a)}{textColor.reset}\n"

    print(colored_time + file_info + text_message)
