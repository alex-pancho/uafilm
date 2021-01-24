import os
import sys
import json
import sqlite3

BASE_DIR = os.path.abspath(os.path.join('..', 'films'))
conn = sqlite3.connect(os.path.join(BASE_DIR, "films.sqlite"))
cursor = conn.cursor()
# controller = Controller.from_port(address=local_url, port=9051)


def _printResponse(res, name=''):
    print('D-res : ', name)
    for child in res.iter('*'):
        print('\t', child.tag, child.attrib, child.text)
    print('\n')


def _printList(res, name=''):
    print('L-res : ', name)
    for i in range(len(res)):
        if isinstance(res[i], list):
            _printList(res[i], str(i) + 'sub')
        else:
            print(i, '\t', res[i].encode('utf-8'))
    print('\n')


def chek_mov(films):
    name_ua = films.get('title_ua', "")
    name_orig = films.get('title_or', "")
    year = films.get('year', "")

    if name_ua == "" and name_orig == "" and year == "":
        print('wrong parametrs')
        print(films)
        return [0]
    if name_ua is not None and name_orig is not None:
        string = f"""("name_ua1" LIKE '%{name_ua}%'  or "name_orig" LIKE '%{name_orig}%') """
    elif name_ua is not None:
        string = f""" "name_ua1" LIKE '%{name_ua}%' """
    elif name_orig is not None:
        string = f""" "name_orig" LIKE '%{name_orig}%' """
    else:
        print('wrong parametrs')
        print(films)
        return [0]
    if year != "":
        yearstr = f""" and "years" = {year} """
    else:
        yearstr = ''
    sql = f'SELECT * FROM "cinema" WHERE {string} {yearstr}'
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        print(sql)
        input('..c')
    result = cursor.fetchall()
    lr = len(result)
    if lr > 0:
        id = result[0][0]
    else:
        id = 0
    return [lr, id]


def add_mov(films):
    name_ua = films.get('title_ua', "")
    name_orig = films.get('title_or', "")
    year = films.get('year', "")

    if name_ua == "" and name_orig == "" and year == "":
        print('wrong parametrs')
        return [0]

    type_src = films.get('type_src', "Кіно")
    poster = films.get('poster', "")
    desc = films.get('desc', "")
    director = films.get('director', "")
    all_pars = [name_ua, type_src, name_orig, poster, desc, year, director]
    for a in range(len(all_pars)):
        if all_pars[a] is None:
            all_pars[a] = "''"
    params = "'" + "', '".join(all_pars) + "'"
    sql = f"""INSERT INTO "main"."cinema"
    ("name_ua1", "type_src", "name_orig", "poster", "descript", "years", "director")
    VALUES ( {params} );"""
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError as e:
        print(e)
        print(sql)
        input('..c')
        return None
    conn.commit()
    return chek_mov(films)


def insert_link(li):
    sql = f"""SELECT * FROM "cinema_link" WHERE "kinoid"={li[0]} and "quality"='{li[2]}'  """
    # print (sql)
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError as e:
        print(e)
        print(sql)
        input('..c')
    result = cursor.fetchall()
    if len(result) > 0:
        print("link in base")
        return None

    sql = f"""INSERT INTO "cinema_link" ("kinoid","link","quality") VALUES {li[0],li[1],li[2]};"""
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError as e:
        print(e)
        print(sql)
        #input('..c')
    conn.commit()
    print("new link add")
    return None


def save_item_dict(item):
    for i in item:
        if isinstance(item[i], dict) or item[i] is None:
            continue
        item[i] = item[i].replace("'", '’').replace(",", ';').replace('"', '’')

    cnt = chek_mov(item)
    if cnt[0] == 0:
        cnt = add_mov(item)
        if cnt[0] != 0:
            print(f"{cnt[1]} new MOVIE add")
    else:
        try:
            x = f"{cnt[1]}\t{item.get('title_ua', '')}"
        except IndexError:
            x = item.get('title_ua', "")
        print(x, "movie in base")
    if cnt[0] != 0:
        kinoid = cnt[1]
        links = item.get("all_links", [])
        for li, val in links.items():
            # print("ADD:", kinoid, val, li)
            # input('..c')
            if val is not None:
                insert_link([kinoid, val, li])