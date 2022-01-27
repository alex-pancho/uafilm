from pony.orm import *


db = Database()


class Items(db.Entity):
    id = PrimaryKey(int, auto=True)
    title_ua = Optional(str)
    title_or = Optional(str)
    type_src = Optional(str)
    year = Optional(str)
    director = Optional(str)
    description = Optional(LongStr)
    poster = Optional(str)
    json = Optional(Json)
    imdb = Optional(str)


class Sezone(db.Entity):
    id = Required(int, auto=True)
    items_id = Required(int)
    name = Optional(str)
    number = Optional(int)
    total = Optional(int)
    PrimaryKey(id, items_id)


class Links(db.Entity):
    id = PrimaryKey(int, auto=True)
    source_id = Required(int)
    quality = Optional(str)
    its_work = Required(bool)
    type_src = Optional(str)
    m3u_links = Required(str)
    subs = Optional(Json)

db_params = dict(provider='mysql',
        host="localhost",
        user="root",
        passwd="root",
        db='uakino')#, create_db=True

sqlite = dict(provider='sqlite',
              filename='uakino.db',
              create_db=True)
set_sql_debug(True)
db.bind(**db_params)
#db.bind(**sqlite)
db.generate_mapping(create_tables=True)

def add_to_db(item):
    if select(i.id for i in Items if i.title_ua == item["title_ua"]).get() is not None:
        return select(i.id for i in Items if i.title_ua == item["title_ua"]).get()
    m3u_links = item.pop('m3u_links', None)
    try:
        item['poster'] = m3u_links[-1].get('poster', "")
    except:
        pass
    with db_session:
        # insert new movie
        mov_ua = select(i.id for i in Items if i.title_ua == item["title_ua"]) if item["title_ua"] != "" else []
        mov_or = select(i.id for i in Items if i.title_or == item["title_or"]) if item["title_or"] != "" else []
        imdb = select(i.id for i in Items if i.imdb == item["imdb"]) if item["imdb"] != "" else []
        if len(mov_ua) == 0 and len(mov_or) == 0 and len(imdb) == 0:
            Items(**item)
    if select(i.id for i in Items if i.title_ua == item["title_ua"]).get() is not None:
        return select(i.id for i in Items if i.title_ua == item["title_ua"]).get()
    else:
        raise ValueError(f"Cant save: {item}")


def get_m3u(m3u, type_src, source_id):
    if "1080" in m3u["m3u_link"]:
        quality = "1080p"
    elif "720" in m3u["m3u_link"]:
        quality = "720p"
    else:
        quality = "?"
    link_in_base = Links.get(m3u_links=m3u["m3u_link"])
    if link_in_base is not None:
        return
    with db_session:
        Links(source_id=source_id,
              quality=quality,
              its_work=1,
              type_src=type_src,
              m3u_links=m3u["m3u_link"],
              subs=m3u["subtitle"])


def save(item):
    m3u_links = item.get('m3u_links', [{"m3u_link": 'none', "subtitle": ""}])
    type_src = item["type_src"]
    source_id = add_to_db(item)
    with db_session:
        # insert link to movie
        if source_id is None:
            print("ERROR UPDATE:", item)
        for m3u in m3u_links:
            if isinstance(m3u, dict):
                get_m3u(m3u, type_src, source_id)
            elif isinstance(m3u, list):
                for m in m3u:
                    get_m3u(m, type_src, source_id)






