import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('bot.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRAKTIKUM_API = 'https://praktikum.yandex.ru/api/'

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    if homework_name is None:
        return homework_name
    if status not in ('approved', 'rejected'):
        return None
    elif status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = URL_PRAKTIKUM_API + 'user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except Exception as error:
        logger.error(error, exc_info=True)
    if len(homework_statuses.json()["homeworks"]) != 0:
        return homework_statuses.json()["homeworks"][0]
    return homework_statuses.json()


def send_message(message):
    if message is not None:
        logger.info('Sending message')
        return bot.send_message(CHAT_ID, message)
    return None


def main():
    logger.debug('Starting bot')
    current_timestamp = int(time.time()) - 60 * 25

    while True:
        try:
            send_message(
                parse_homework_status(
                    get_homeworks(current_timestamp)))
            time.sleep(21 * 60)

        except Exception as e:
            logger.error(f'Ошибка: {e}')
            time.sleep(5)
            return bot.send_message(CHAT_ID, f'У нас проблемы: {e}')


if __name__ == '__main__':
    main()
