import time
import sqlite3
import os

BASE_DIR = 'films'
conn = sqlite3.connect(os.path.join(BASE_DIR, "films.sqlite"))
cursor = conn.cursor()

QL = ["L", "M", "H"]
par = ["easy", "ext", "max", ]  # n
ORDER = ['order by "name_ua1"', 'order by "years"']  # 'order by "name_orig"'


def file_write(result, write_file, p=par[0], order="name_ua"):
    if p == "easy":
        write_file.write("#EXTM3U\n")
        write_file.write("\n")
        for r in result:
            group = r[3]
            poster = r[5]
            nameua = r[2].replace(",", ";")
            nameor = r[4].replace(",", ";")
            year = r[7]
            director = r[8]
            # url = r[10]
            write_file.write(f"""{nameua} ({nameor}) [{year}]:{director} \n""")
            # write_file.write(url+"\n")
    if p == "ext":
        write_file.write("#EXTM3U\n")
        write_file.write("\n")
        for r in result:
            nameua = r[2].replace(",", ";")
            year = r[7]
            nameor = r[4].replace(",", ";")
            if order == "name_ua":
                group = nameua[0]
            elif order == "years":
                if year >= 2010:
                    group = year
                elif 2010 > year > 1990:
                    group = (year // 5) * 5
                else:
                    group = (year // 10) * 10
            poster = r[5]
            director = r[8]
            url = r[10]
            write_file.write(
                f"""#EXTINF:-1 tvg-logo="{poster}" group-title="{group}", {nameua} ({nameor}) [{year}]:{director} \n""")
            write_file.write(url + "\n")
    if p == "max":
        write_file.write("#EXTM3U\n")
        write_file.write("\n")
        for r in result:
            nameua = r[2].replace(",", ";")
            nameor = r[4].replace(",", ";")
            poster = r[5]
            desc = r[6]
            year = r[7]
            director = r[8]
            url = r[10]
            if order == "name_ua":
                group = nameua[0]
            elif order == "years":
                if year >= 2010:
                    group = year
                elif 2010 > year > 1990:
                    group = (year // 5) * 5
                else:
                    group = (year // 10) * 10
            write_file.write(
                f"""#EXTINF:-1 tvg-logo="{poster}" group-title="{group}", {nameua} ({nameor}) //{desc}// [{year}]:{director} \n""")
            write_file.write(url + "\n")


def save(Q, p=par[0], order=None):
    if order == 'order by "name_ua1"': ordr = "name_ua"
    if order == 'order by "name_orig"': ordr = "name_orig"
    if order == 'order by "years"': ordr = "years"
    if p == "easy":
        sql = f"""select * from "cinema" {order};"""
    elif Q == "L":
        sql = f"""select * from "cinema"
        join "cinema_link" on "id"="kinoid"
        where "quality" in ('360p','480p') and "cinema_link"."notWork" = 0
        {order}; """
    elif Q == "M":
        sql = f"""select * from "cinema" join "cinema_link" on "id"="kinoid"
        where "quality" in ('720p') and "cinema_link"."notWork" = 0
        {order}; """
    elif Q == "H":
        sql = f"""select * from "cinema" join "cinema_link" on "id"="kinoid"
        where "quality" in ('1080p') and "cinema_link"."notWork" = 0
        {order}; """
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        print(sql)
        input('..c')
    result = cursor.fetchall()

    if len(result) > 0:
        if Q == "L":
            fn = f"{p}_{ordr}_360-480_{time.strftime('%Y-%m-%d')}.m3u"
        if Q == "M":
            fn = f"{p}_{ordr}_720_{time.strftime('%Y-%m-%d')}.m3u"
        if Q == "H":
            fn = f"{p}_{ordr}_1080_{time.strftime('%Y-%m-%d')}.m3u"
        # encoding='utf-8-sig'
        try:
            write_file = open(os.path.join("m3u", p, fn), "a", encoding='utf-8')
        except:
            write_file = open(os.path.join("m3u", p, fn), "w", encoding='utf-8')
        file_write(result, write_file, p, ordr)
    print(Q, p, 'done')


for OR in ORDER:
    for Q in QL:
        for p in par[1:]:
            save(Q, p, OR)
save(QL[0], par[0], ORDER[0])
