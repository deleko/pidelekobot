import logging
import telegram
from urllib.parse import urlsplit

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler

from amazon.referral import *
from gas_api.gas import *
from weather_api.weather import *
from lotto_api.lotto import *
from user_info.user_crud import *

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


def get_lotto(update, context):
    name = update.effective_user['first_name']
    logger.info(f"{name} get lotto data")
    user_id = update.effective_user['id']
    check_lotto_prizes(user_id)
    lotto_data = get_lotto_data(user_id)
    if lotto_data == -1:
        msg = 'No me has envíado ningún número todavía.'
    else:
        msg = '<b>TUS NÚMEROS</b>\n\n'
        for lotto_number in lotto_data:
            msg += "🎟️ " + str(lotto_number[0]) + " 💰 " + str(round(lotto_number[1] / 20, 2)) + "€\n"
        msg += '\n<i>*premio por € jugado</i>'
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)


LOTTO_BUTTONS, LOTTO_NUMBER = range(2)


def lotto_conversation(update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("🍀 Añadir un número", callback_data='add_lotto'), ],
                [InlineKeyboardButton("💰 Consultar mis números", callback_data='check_lotto')], ]
    markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Elige una opción para la loteria de navidad de 2022 🧑‍🎄 ', reply_markup=markup)

    return LOTTO_BUTTONS


def lotto_actions(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer(f'button click {query.data} recieved')

    if query.data == 'add_lotto':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Dime el número', reply_markup=ForceReply())
        return LOTTO_NUMBER

    if query.data == 'check_lotto':
        get_lotto(update, context)
        return ConversationHandler.END

    return ConversationHandler.END


def put_lotto(update, context):
    name = update.effective_user['first_name']
    lotto_number = update.message.text
    logger.info(f"{name} put lotto data")
    user_id = update.effective_user['id']
    lotto_data = put_lotto_data(user_id, name, lotto_number)
    if lotto_data == 0:
        msg = '🎟️ ' + str(lotto_number) + ' añadido correctamente\n\n Mucha suerte 🍀'
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=msg)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Name Conversation cancelled by user. Bye. Send /set_name to start again')
    return ConversationHandler.END


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
dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler('loteria', lotto_conversation)],
    states={
        LOTTO_BUTTONS: [CallbackQueryHandler(lotto_actions)],
        LOTTO_NUMBER: [MessageHandler(Filters.text, put_lotto)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
))
dp.add_handler(MessageHandler(Filters.text, check_message))
dp.add_handler(MessageHandler(Filters.location, location))

updater.start_polling()
print("BOT CARGADO")
updater.idle()  # permite pararlo
