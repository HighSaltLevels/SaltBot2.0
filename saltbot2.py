import os
import traceback

from lib.controller import CLIENT
from lib.email import send_email

BOT_TOKEN = os.environ['BOT_TOKEN']

if __name__ == '__main__':
    try:
        CLIENT.run(BOT_TOKEN)
    except Exception as error:
        error_msg = traceback.format_exc()
        print(error_msg)
        send_email(error_msg)
        os.system('reboot')
