import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    if len(homework["homeworks"]) != 0:
        homework_name = homework["homeworks"][0]["homework_name"]
        status = homework["homeworks"][0]["status"]
        if status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    if message is not None:
        logging.info('Отправляю сообщение')
    return bot.send_message(CHAT_ID, message)


def main():
    logging.debug('Запуск')
    current_timestamp = int(time.time() - 60 * 60 * 24 * 7)

    while True:
        try:
            send_message(
                parse_homework_status(
                    get_homeworks(current_timestamp)))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.debug(f'Ошибка: {send_message(e)}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
