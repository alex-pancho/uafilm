from pony.orm import *
from pony.orm.core import sql_logger
from .settings import USE_DB
from .settings import DEBUG
"""
Create database structures
"""
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


class Seasons(db.Entity):
    id = PrimaryKey(int, auto=True)
    source_id = Required(int)
    name = Optional(str)
    season = Optional(str)
    title = Optional(str)


class Links(db.Entity):
    id = PrimaryKey(int, auto=True)
    source_id = Required(int)
    series_id = Optional(int)
    quality = Optional(str)
    its_work = Required(bool)
    type_src = Optional(str)
    m3u_links = Required(str)
    subs = Optional(Json)

mysql = dict(provider='mysql',
             host="localhost",
             user="root",
             passwd="root",
             db='uakino')

sqlite = dict(provider='sqlite',
              filename='uakino.db',
              create_db=True)

set_sql_debug(DEBUG)

if USE_DB == 'mysql':
    db.bind(**mysql)
elif USE_DB == 'sqlite':
    db.bind(**sqlite)
else:
    raise ConnectionError("Wrong or not supported DB in setting")
db.generate_mapping(create_tables=True)


@db_session
def check_in_base(checks, err_counter=0):
    try:
        param = Items.get(**checks)
        param = param.id
    except MultipleObjectsFoundError:
        err_counter += 1
        param = None
    except AttributeError:
        pass
    return param, err_counter


def add_to_db(item):
    """
    Add item to database
    :param item: scraped data in dict
    :return: item_id - id for record
    """
    item_id = None
    item.pop('m3u_links', None)
    err_counter = 0
    # Items.get(lambda p: p.title_ua.startswith('Всесвітня природна'))  # LIKE X%
    mov_ua, err_counter = check_in_base(dict(title_ua=item["title_ua"]), err_counter)
    mov_or, err_counter = check_in_base(dict(title_or=item["title_or"]), err_counter)
    imdb, err_counter = check_in_base(dict(imdb=item["imdb"]), err_counter)

    in_base = [_id for _id in [mov_ua, mov_or, imdb] if _id is not None]
    if err_counter == 3 or (len(in_base) > 1 and mov_ua != mov_or and mov_or != imdb and imdb != mov_ua):
        raise TooManyObjectsFoundError("No unique field found, data cannot be added or saved")

    if in_base == []:
        # then insert new movie
        with db_session:
            item_in_db = Items(**item)
            flush()
            item_id = item_in_db.id
    else:
        item_id = in_base[-1]
    if item_id is not None:
        return item_id
    else:
        raise TransactionError(f"Cant save: {item}")


def add_m3u(m3u, type_src):
    """
    Add episode or movie link to database
    :param m3u: streaming data for item
    :param type_src: one of [movie, cartoon, series]
    :param source_id: item id
    :param series: info about tv series episode
    """
    source_id = m3u.get("source_id")
    series = m3u.get("series")
    if "1080" in m3u["m3u_link"]:
        quality = "1080p"
    elif "720" in m3u["m3u_link"]:
        quality = "720p"
    else:
        quality = "?"
    with db_session:
        link_in_base = Links.get(m3u_links=m3u["m3u_link"])
    if link_in_base is not None:
        sql_logger.debug("current link in DB, append doesnt need")
        return
    series_id = 0
    if type_src == 'series':
        with db_session:
            if Seasons.get(**series) is None:
                series = Seasons(**series)
                flush()
                series_id = series.id
            else:
                sql_logger.debug("current series in DB, append doesnt need")
                return
    with db_session:
        Links(source_id=source_id,
              series_id=series_id,
              quality=quality,
              its_work=1,
              type_src=type_src,
              m3u_links=m3u["m3u_link"],
              subs=m3u.get("subtitle", ""))


def save(item):
    """
    Save item data into db
    :param item: scraped data in dict
    """
    m3u = item.get('m3u_links', [{"m3u_link": 'none', "subtitle": ""}])
    type_src = item["type_src"]
    # insert movie to db and get id (source_id)
    if "_id" not in item:
        source_id = add_to_db(item)
        item["_id"] = source_id
    else:
        source_id = item["_id"]

    series = item.get("json").get("series")
    # insert link to movie
    if source_id is None:
        raise TransactionError(f"Cant find id for: {item}")
    m3u["source_id"] = source_id
    if series:
        series["name"] = item["json"]["name"]
        series["source_id"] = source_id
        m3u["series"] = series
    add_m3u(m3u, type_src)
