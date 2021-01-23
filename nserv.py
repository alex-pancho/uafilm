import requests
from lxml import html as ET
import json
from mainspider import save_item_dict

SCRIPT_VER = "kinoparser v 02.08.2020"
BASE_URL = ''
START = 1


def save_item(item, name):

    title_ua = None
    type_src = "Кіно"
    title_or = None
    poster = ""
    desc = ""
    year = ""
    director = ""
    all_links = {}
    # print(film)
    names = name.split(" / ")

    title_ua = names[0]
    if len(names) > 1:
        title_or = ";".join(names[-1])
    ch = item.get("channels", [])
    if len(ch) > 0:
        for i in ch:
            if i.get("title") == "Описание":
                desc = str(i.get("description", "[]"))
                tree = ET.fromstring(desc)
                poster = tree.xpath('//img[@src]')[0].attrib["src"]
                texts = tree.xpath('//div[3]/text()')
                # print(texts)
                year = texts[0].split(",")[-1].strip()
                director = texts[-1].strip()
                desc_sh = tree.xpath('//*[@id="footer"]/text()')[0]
                desc = desc_sh
            elif i.get("title") != "Описание" and i.get("title") != "Трейлер":
                qa = i.get("title", "?")
                link = i.get("stream_url")
                all_links.update({qa: link})
    # print(all_links)
    # input("...")
    item_dict = dict(
        title_ua=title_ua, type_src=type_src, title_or=title_or,
        poster=poster, desc=desc, year=year,
        director=director, all_links=all_links)
    # print(item_dict)
    save_item_dict(item_dict)


def parse(cont, heads, s=None):
    s = requests.session()
    if isinstance(cont, dict):
        items = cont.get("channels")
        for i in items:
            item_url = i.get("playlist_url", "http://nserv.host:5300/view")
            name = i.get("title", "")
            item, heads = get_body(item_url, heads, s)
            if isinstance(item, dict):
                save_item(item, name)
            else:
                print("ERR item:", item)
        # next page url
        next_page_url = cont.get("next_page_url")
        old_url = heads.get("url")
        print(next_page_url)
        if old_url != next_page_url:
            # print(old_url, next_page_url)
            cont, heads = get_body(next_page_url, heads, s)
            return parse(cont, heads, s)  # None
        else:
            print("Look, its all!")
            return
    else:
        print("ERR content type", type(cont), cont)
        return


def get_body(URL, heads, s):
    try:
        req = s.get(URL, headers=heads)  # proxies=p
    except Exception as e:
        print(e)
        return 'Null', heads

    if req.status_code != 200:
        print("ERR Satus:", req.status_code)
        return str(req.status_code), heads

    try:
        cont = req.json()
    except json.decoder.JSONDecodeError:
        cont = req.text
    return cont, heads


def main(URL):
    print(SCRIPT_VER)
    print(URL)
    h = {
        "User-Agent": "Mozilla/5.0 (SmartHub; SMART-TV; U; Linux/SmartTV+2013; Maple2012) \
            AppleWebKit/535.20+ (KHTML, like Gecko) SmartTV Safari/535.20+",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "url": URL
         }
    s = requests.session()
    cont, heads = get_body(URL, h, s)
    parse(cont, heads, s)
    print("Job done")


def link_pars():

    src_list = [  # 'http://nserv.host:5300/eneyida/list?cat=films',
                'http://nserv.host:5300/uakino/list?cat=filmi&page=28',
                # 'http://nserv.host:5300/kinoukr/list?cat=films'
                 ]
    for url in src_list:
        global BASE_URL
        BASE_URL = url
        main(BASE_URL)


if __name__ == '__main__':
    link_pars()
