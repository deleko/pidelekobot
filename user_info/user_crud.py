import sqlite3
from datetime import datetime


def update_user_location(user_id, username, user_lat, user_lon):
    now = datetime.now()
    sysdate = now.strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect('pidelekobot.db')
    cur = con.cursor()

    search_user = """SELECT COUNT(*) FROM USER_INFO WHERE user_id = ?"""
    cur.execute(search_user, (user_id,))
    userexists = cur.fetchone()[0] > 0
    if userexists:
        update_user_info = """UPDATE USER_INFO SET last_msg = ?, user_lat = ?, user_lon = ? WHERE user_id = ?"""
        cur.execute(update_user_info, (sysdate, user_lat, user_lon, user_id))
    else:
        insert_user_info = """INSERT INTO USER_INFO (user_id, user_alias, first_msg, last_msg, user_lat, user_lon) VALUES (?, ?, ?, ?, ?, ?)"""
        cur.execute(insert_user_info, (user_id, username, sysdate, sysdate, user_lat, user_lon))
    con.commit()
    con.close()


def get_user_location(user_id):
    con = sqlite3.connect('pidelekobot.db')
    cur = con.cursor()
    query = """SELECT user_lat, user_lon FROM USER_INFO WHERE user_id = ?"""
    data = cur.execute(query, (user_id,)).fetchall()
    con.commit()
    con.close()
    try:
        return data[0]
    except:
        return 404, 404
