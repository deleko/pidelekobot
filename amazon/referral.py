import json
import re
import requests
import pyshorteners
from bs4 import BeautifulSoup
from docs.constants import *


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
