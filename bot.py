import json
import logging
import re
import requests
import telegram
import pyshorteners
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from keys import *


# Log config
logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)


def start(update, context):
    name = update.effective_user['first_name']
    user_id = update.effective_user['id']
    logger.info(f'{name} ha iniciado el bot')
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=f"Hola <b>{name}</b>, envíame un enlace de amazon y verás lo que puedo hacer."
                            )


def gasolineras(update, context):
    name = update.effective_user['first_name']

    idmunicipio: int = 7149
    urlfiltromunicipio = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/"
    filtromunicipio = requests.get(urlfiltromunicipio + str(idmunicipio))
    jfiltromunicipio = filtromunicipio.json()
    ideess = str(14816)
    output_dict = [x for x in jfiltromunicipio['ListaEESSPrecio'] if x['IDEESS'] == ideess]
    gasoleo = "Gasoleo A: " + output_dict[0]['Precio Gasoleo A'] + " €"
    gasolina = "Gasolina 95: " + output_dict[0]['Precio Gasolina 95 E5'] + " €"

    user_id = update.effective_user['id']
    logger.info(f'{name} ha consultado gasolina')
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="HTML",
                            text=f"<b>⛽ VCC PATERNA</b> \n {gasoleo} \n {gasolina}"
                            )


def scrap_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",  # <-- add "Accept-Language" to try to prevent captcha
    }
    url = "https://" + url
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find(id="productTitle").get_text()

    # priceblock_saleprice = soup.find(id="priceblock_saleprice")
    # priceblock_dealprice = soup.find(id="priceblock_dealprice")
    # priceblock_ourprice = soup.find(id="priceblock_ourprice")
    # price = priceblock_saleprice or priceblock_dealprice or priceblock_ourprice
    # price = price.get_text()

    img_div = soup.find(id="imgTagWrapperId")
    imgs_str = img_div.img.get('data-a-dynamic-image')
    imgs_dict = json.loads(imgs_str)
    num_element = 0
    image = list(imgs_dict.keys())[num_element]

    # return title, image, price
    return title, image


def clear_url(url, domain):
    regex = re.compile("(/[dg]p/[^/?]+)")
    r = regex.findall(url)
    url = domain + r[0]
    return url


def set_referral_url(url):
    referral = "7760-21"
    extra = "%26language=es_ES&keywords="
    url = "https://" + url + "?tag=" + referral + extra
    return url


def short_url(url):
    s = pyshorteners.Shortener(api_key=BITLY_KEY)
    shorturl = s.bitly.short(url)
    return shorturl


def respuesta_amazon(update, context, text, domain):
    user_id = update.effective_user['id']
    url = clear_url(text, domain)
    url_ref = set_referral_url(url)
    url_short = short_url(url_ref)
    scrap = scrap_amazon(url)
    title = scrap[0].strip()
    image = scrap[1]
    # price = scrap[2]
    context.bot.sendMessage(chat_id=user_id,
                            parse_mode="Markdown",
                            # text=f"[🔹]({image})*{title}* \n\n💰 {price} \n\n🔗 {url_short}\n"
                            text=f"[🔹]({image})*{title}* \n\n🔗 {url_short}\n"
                            )


def check_message(update, context):
    name = update.effective_user['first_name']
    text = update.message.text
    logger.info(f"{name} ha enviado un mensaje: {text}")
    text = text.strip()
    domain = "{0.netloc}".format(urlsplit(text))
    if domain.find("amazon.") != -1:
        print(domain.find("amazon."))
        respuesta_amazon(update, context, text, domain)


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
dp.add_handler(CommandHandler("gasolineras", gasolineras))
dp.add_handler(MessageHandler(Filters.text, check_message))

updater.start_polling()
print("BOT CARGADO")
updater.idle()  # permite pararlo
