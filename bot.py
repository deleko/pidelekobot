import logging
import telegram
from urllib.parse import urlsplit
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from amazon.referral import *
from gas_api.gas import *

# Log config
logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    filename='logs/bot.log',
    format='%(asctime)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)


def start(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    logger.info(f'{name} ha iniciado el bot')
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=f"Hola <b>{name}</b>, con /help verás todo lo que puedo hacer."
                            )


def check_message(update, context):
    name = update.effective_user['first_name']
    text = update.message.text
    logger.info(f"{name} sent a msg: {text}")
    text = text.strip()
    domain = "{0.netloc}".format(urlsplit(text))
    if domain.find("amazon.") != -1:
        respuesta_amazon(update, context, text, domain)


def location(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} sent location")
    user_id = update.effective_user['id']
    user_lat = update.message.location.latitude
    user_lon = update.message.location.longitude
    carga_gasolineras()
    lista = busca_gasolineras(user_lat, user_lon)
    msg = ''.join(lista)

    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                            text=f"{msg}"
                            )


if __name__ == "__main__":
    # Obtenemos la info del bot
    my_bot = telegram.Bot(token=TOKEN_TG)
    print(my_bot.getMe())

# Enlazamos updater con bot
updater = Updater(my_bot.token, use_context=True)

# Creamos despachador
dp = updater.dispatcher

# creamos manejador
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text, check_message))
dp.add_handler(MessageHandler(Filters.location, location))

updater.start_polling()
print("BOT CARGADO")
updater.idle()  # permite pararlo
