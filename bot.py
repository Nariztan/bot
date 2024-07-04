import telebot
import time
import snscrape.modules.telegram as tg
import sqlite3
from datetime import datetime
import requests
from config import BOT_TOKEN


response = requests.get(url='https://www.cbr-xml-daily.ru/daily_json.js').json()
print(f'Скрипт был успешно запущен в {datetime.now()}')
bot = telebot.TeleBot(BOT_TOKEN)


def write_to_sqlite(url):
    con = sqlite3.connect("checks.db")
    cur = con.cursor()
    x = cur.execute(f"SELECT * FROM checks WHERE url = '{url}'").fetchone()
    if x is None:
        cur.execute(f'INSERT INTO checks(url) VALUES("{url}")')
        con.commit()
        return True
    return False


def upload_posts():
    scraper = tg.TelegramChannelScraper('topchekroc')
    for i, t in enumerate(scraper.get_items()):
        if i == 1:
            break
        if "паролем" not in str(t.content):
            for url in t.outlinks:
                if 'mci' in url:
                    c = t.content
                    price = c[c.find('по'):c.find('с реферальной')]
                    if '(' in c:
                        if write_to_sqlite(url):
                            return url, float(price[price.find('(') + 1: price.find(')') - 1])
                        else:
                            return False, 0
                    else:
                        return url, 0
        else:
            return False, 0


@bot.message_handler(commands=['start'])
def send_welcome(message):
    con = sqlite3.connect("checks.db")
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY, url TEXT);''')
    bot.reply_to(message, "Бот готов к работе!")
    send()


# ЛЕГЧЕ ХУЙ ЗАБИТЬ, ЧТОБЫ ВСЕ БЫЛО НОРМ ВЕРНИ ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ WRITE_TO_SQLITE И ПЕРЕДЕЛАЙ НЕМНОГО UPLOAD_POSTS
def send():
    count = 0
    sum_checks = 0
    while True:
        post, price = upload_posts()
        if post is not False:
            count += 1
            sum_checks += price
            print(
                f"Использовано ссылок: {count}\nПриблизительная сумма: {sum_checks}$ ≈ {round(sum_checks * response['Valute']['USD']['Value'], 2)}₽")
            bot.send_message('-4248655991', post)
            time.sleep(30)


try:
    bot.polling()
except Exception as e:
    print(f'Остановка бота в {datetime.now()} из-за ошибки {e}')
