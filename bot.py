import logging
import telegram
from urllib.parse import urlsplit

from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from amazon.referral import *
from gas_api.gas import *
from weather_api.weather import *
from user_info.user_crud import *

import requests
import urlextract
from urlextract import URLExtract
import validators
from validators import ValidationFailure

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
    logger.info(f'{name} sent /start')
    msg = f"Hola <b>{name}</b>, con /help verás todo lo que puedes hacer."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)


def help(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    logger.info(f'{name} sent /help')
    msg = "🌦 Consultar el /tiempo en tu zona.\n\n " \
          "⛽ Buscar /gasolineras cerca y ver el precio.\n\n" \
          "☕ Link de amazon <i>(y compra con mi link)</i> para invitarme a un café."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)

def is_string_an_url(url_string: str) -> bool:
    result = validators.url(url_string)
    if isinstance(result, ValidationFailure):
        return False

    return result

def check_message(update, context):
    name = update.effective_user['first_name']
    text = update.message.text
    logger.info(f"{name} sent a msg: {text}")

    ht = "https://"

    #extrae la primera url del mensaje (si es que hay)
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    if len(urls) > 0:
        text = urls[0]

    text_s = text.strip()
    domain = "{0.netloc}".format(urlsplit(text_s))
    if domain.find("amazon.") != -1:
        amazon_referral(update, context, text_s, domain)
    else:
        if is_string_an_url(text):
            #request al enlace por si tiene redirecciones quedarnos con la url final
            r = requests.get(text)
            text_2 = r.url
            text_2s = text_2.strip()
            domain_2 = "{0.netloc}".format(urlsplit(text_2s))
            if domain_2.find("amazon.") != -1:
                amazon_referral(update, context, text_2s, domain_2)
        elif is_string_an_url(ht+text):
            r = requests.get(ht+text)
            text_3 = r.url
            text_3s = text_3.strip()
            domain_3 = "{0.netloc}".format(urlsplit(text_3s))
            if domain_3.find("amazon.") != -1:
                amazon_referral(update, context, text_3s, domain_3)

def location(update, context):
    name = update.effective_user['first_name']
    username = update.effective_user['username']
    logger.info(f"{name} sent location")
    user_id = update.effective_user['id']
    user_lat = update.message.location.latitude
    user_lon = update.message.location.longitude
    update_user_location(user_id, username, user_lat, user_lon)
    msg = "Perfecto, intentaré acordarme de que estás ahí."
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)


def location_gas(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} check gas")
    user_id = update.effective_user['id']
    user_lat = get_user_location(user_id)[0]
    user_lon = get_user_location(user_id)[1]
    if user_lat == 404:
        msg = 'Envíame la ubicación para poder saber dónde estás.'
    else:
        gas_load()
        lista = gas_search(user_lat, user_lon)
        msg = ''.join(lista)
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=telegram.ReplyKeyboardRemove(),
                            text=msg)


def location_weather(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} check weather")
    user_id = update.effective_user['id']
    user_lat = get_user_location(user_id)[0]
    user_lon = get_user_location(user_id)[1]
    if user_lat == 404:
        msg = 'Envíame la ubicación para poder saber dónde estás.'
    else:
        weather_found = weather_api(user_lat, user_lon)
        status = weather_found[0]
        if status == 200:
            city = weather_found[1]
            country = weather_found[2]
            weather_description = weather_found[3]
            current_temperature = weather_found[4]
            current_feeling = weather_found[5]
            msg = (f"El tiempo en {city}, {country}:\n"
                   f"{current_temperature}ºC, {weather_description}\n"
                   f"Sensación de {current_feeling}ºC")
        else:
            msg = "¿Dónde demonios estás?"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=telegram.ReplyKeyboardRemove(),
                            text=msg)


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
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("gasolineras", location_gas))
dp.add_handler(CommandHandler("tiempo", location_weather))
dp.add_handler(MessageHandler(Filters.text, check_message))
dp.add_handler(MessageHandler(Filters.location, location))

updater.start_polling()
print("BOT CARGADO")
updater.idle()  # permite pararlo
