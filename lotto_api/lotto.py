import json
import urllib.request
import sqlite3


# https://servicios.elpais.com/sorteos/loteria-navidad/api/

def put_lotto_data(user_id, username, lotto_number):
    con = sqlite3.connect('lotto.db')
    cur = con.cursor()

    search_user_number = """SELECT COUNT(*) FROM USER_LOTTO WHERE user_id = ? AND LOTTO_NUMBER = ?"""
    cur.execute(search_user_number, (user_id, lotto_number,))
    usernumberexists = cur.fetchone()[0] > 0
    if usernumberexists:
        # lotto data already stored
        return 1
    else:
        if str(lotto_number).isnumeric():
            insert_user_number = """INSERT INTO USER_LOTTO (user_id, user_alias, lotto_number, lotto_prize) VALUES (?, ?, ?, 0)"""
            cur.execute(insert_user_number, (user_id, username, lotto_number))
            con.commit()
        else:
            # lotto data is not a number
            return 2
    con.close()
    return 0


def get_lotto_data(user_id):
    con = sqlite3.connect('lotto.db')
    cur = con.cursor()
    query = """SELECT lotto_number, lotto_prize FROM USER_LOTTO WHERE user_id = ?"""
    data = cur.execute(query, (user_id,)).fetchall()

    search_user = """SELECT COUNT(*) FROM USER_LOTTO WHERE user_id = ?"""
    cur.execute(search_user, (user_id,))
    userexists = cur.fetchone()[0] > 0
    con.close()

    if userexists:
        return data
    else:
        return -1


def check_lotto_prizes(user_id):
    status_url = "https://api.elpais.com/ws/LoteriaNavidadPremiados?s=1"
    response = urllib.request.urlopen(status_url)
    data = response.read()
    response_json = json.loads(data.decode("utf8").replace("info=", ""))
    lotto_status = response_json["status"]
    status_decode = {
        0: "El sorteo no ha empezado",
        1: "El sorteo ha empezado",
        2: "El sorteo ha terminado",
        3: "El sorteo ha terminado, se están validando los datos",
        4: "El sorteo ha terminado, los datos son oficiales"
    }
    status_decode = status_decode.get(lotto_status)

    # while the lotto is on
    if lotto_status > 0:
        url = "http://api.elpais.com/ws/LoteriaNavidadPremiados?n="
        lotto_numbers = get_lotto_data(user_id)
        lotto_data_exists = lotto_numbers != -1

        if lotto_data_exists:
            for number in lotto_numbers:
                # if prize stored is zero
                if number[1] == 0:
                    response = urllib.request.urlopen(url + str(number[0]))
                    data = response.read()
                    response_json = json.loads(data.decode("utf8").replace("busqueda=", ""))
                    prize = response_json["premio"]
                    patch_lotto_prize(number[0], prize)


def patch_lotto_prize(number, prize):
    con = sqlite3.connect('lotto.db')
    cur = con.cursor()
    sql = """UPDATE USER_LOTTO SET lotto_prize = ? WHERE lotto_number = ?"""
    cur.execute(sql, (prize, number,))
    con.commit()
    con.close()
