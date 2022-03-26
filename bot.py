import logging
import telegram
from urllib.parse import urlsplit

from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from amazon.referral import *
from gas_api.gas import *
from weather_api.weather import *

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
    msg = f"Hola <b>{name}</b>, con /help verás todo lo que puedes enviarme"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)


def help(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    logger.info(f'{name} sent /help')
    msg = f"- Ubicación para saber información de tu zona \n\n- Link de amazon <i>(y compra con mi link)</i> para invitarme a un café ☕"
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)


def check_message(update, context):
    name = update.effective_user['first_name']
    text = update.message.text
    logger.info(f"{name} sent a msg: {text}")
    text = text.strip()
    domain = "{0.netloc}".format(urlsplit(text))
    if domain.find("amazon.") != -1:
        amazon_referral(update, context, text, domain)


def location(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} sent location")
    user_id = update.effective_user['id']
    global user_lat
    global user_lon
    user_lat = update.message.location.latitude
    user_lon = update.message.location.longitude
    buttons = [[KeyboardButton("/gasolineras")], [KeyboardButton("/tiempo")]]
    keyboard = [[InlineKeyboardButton("🌦️ Tiempo", callback_data='/tiempo'),
                 InlineKeyboardButton("⛽ Gasolineras", callback_data='/gasolineras')]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Elige una de las opciones",
                             reply_markup=ReplyKeyboardMarkup(buttons))


def location_gas(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} check gas")
    user_id = update.effective_user['id']
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
