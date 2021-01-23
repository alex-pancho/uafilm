import time
import sys
import csv
import locale
import requests
from lxml import html as HT
import json
import sqlite3
import mainspider

SCRIPT_VER = "kinoparser v 15.01.2020"
item_list = ""
BASE_URL = ''

conn = sqlite3.connect("films.sqlite")
cursor = conn.cursor()

START = 4


def check_src(URL):
    s = requests.session()
    try:
        req = s.get(URL, stream=True, timeout=3)
    except (requests.exceptions.ReadTimeout):
        return False
    if req.status_code == 200:
        return True
    else:
        return False


def addmovlink(filmid, m3u):
    # print(result)
    link_add = False
    if m3u.find('360p') != -1:
        li = [0, 0, 0]
        li[0] = filmid
        links = m3u.split(",")
        for l in links:
            if l.find('360p') != -1:
                li[1] = l.replace("[360p]", "")
                li[2] = '360p'
                # print(li)
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('480p') != -1:
                li[1] = l.replace("[480p]", "")
                li[2] = '480p'
                # print(li)
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('720p') != -1:
                li[1] = l.replace("[720p]", "")
                li[2] = '720p'
                # print(li)
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('1080p') != -1:
                li[1] = l.replace("[1080p]", "")
                li[2] = '1080p'
                # print(li)
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
    if not link_add:
        addlink_one2many(filmid,m3u)


def addlink_one2many(id, URL):

    if URL.find('http') != -1:
        s = requests.session()
        try:
            req = s.get(URL)
        except:
            return None
        # print ('one2many:',req.content)
        req_s = str(req.content)
    else:
        req_s = URL
    link_add = False
    if req_s.find("m3u")!=-1:
        li = [0, 0, 0]
        li[0] = id
        links = req_s.split("\\n")
        for l in links:
            if l.find('/360/') != -1:
                li[1] = URL.replace("index.m3u8", l.replace('./', ""))
                li[2] = '360p'
                # print(li)
                # input('...c')
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('/480/') != -1:
                li[1] = URL.replace("index.m3u8", l.replace('./', ""))
                li[2] = '480p'
                # print(li)
                # input('...c')
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('/720/') != -1:
                li[1] = URL.replace("index.m3u8", l.replace('./', ""))
                li[2] = '720p'
                # print(li)
                # input('...c')
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
            if l.find('/1080/') != -1:
                li[1] = URL.replace("index.m3u8", l.replace('./', ""))
                li[2] = '1080p'
                # print(li)
                # input('...c')
                if check_src(li[1]):
                    mainspider.insert_link(li)
                    link_add = True
    if not link_add:
        li = [id, URL, '1080p']
        mainspider.insert_link(li)


def get_html(URL, heads="", s=None):
    if s is None:
        s = requests.session()
    try:
        req = s.get(URL, headers=heads)  # proxies=p
    except Exception as e:
        print(e)
        return 'Null', heads

    if req.status_code != 200:
        print("ERR Satus:", req.status_code)
        return str(req.status_code), heads

    cont = req.text
    return cont, heads


def robo_slover(URL, heads, s):
    try:
        req = s.get(URL)#
    except:
        print ('too bad...')
        return None
    return req


max_page = 1


def last_pg(html):
    tree = HT.fromstring(html)
    page_count = tree.xpath('//span[@class="navigation"]/a')
    # print(page_count[-1].attrib)
    # print(page_count[-1].tag)
    # print(page_count[-1].text)
    global max_page
    max_page = int(page_count[-1].text)


def parse(html, heads, s=None):

    print('page:', max_page)
    start = START
    for i in range(start, max_page + 1):
        print("#")
        sub_url = f"/page/{i}/"
        print(sub_url)
        cont, heads = get_html(BASE_URL + sub_url, heads)
        item_list = parse_sub(cont, heads, s)
        x = save_to_file(item_list)
        print(x)


def parse_sub(html, heads, s):
    item_list = []
    tree = HT.fromstring(html)
    item_count = tree.xpath('//div[@class="movie-item short-item"]/a')
    print('item count:', len(item_count))
    x = len(item_count)
    for i in range(x):
        #print (i+1)
        sub_url = item_count[i].attrib['href']
        #print (sub_url)
        cont, heads = get_html(sub_url, heads)
        x = parse_sub_01(cont, heads, sub_url)
        item_list.append(x)
    return item_list


def parse_sub_01(html, heads, url):

    tree = HT.fromstring(html)
    try:
        title_ua = tree.xpath('//h1/span/text()')[0].strip(" ").replace("'", "")
    except IndexError:
        title_ua = ""

    type_src = "КіноФільм"
    if url.find('film') != -1:
        type_src = "КіноФільм"
    if url.find('cartoon') != -1:
        type_src = "Анімація"
    if url.find('seriesss') != -1:
        type_src = "Серіал"
    try:
        title_or = tree.xpath('//h1/../span/i/text()')[0].strip(" ").replace("'", "")
    except IndexError:
        title_or = ""
    try:
        poster = tree.xpath('//div[@class="film-poster"]/img')[0].attrib['src']
        if poster.find('https://') == -1: poster = 'https://uakino.club' + poster
    except (IndexError, KeyError):
        poster = ""
    try:
        text = tree.xpath('//div[@itemprop="description"]/text()')
        text2 = tree.xpath('//div[@itemprop="description"]/p//text()')
        if text[0] == '\n\t\t\t': text = text2
        desc = '\n'.join(text).strip('\n\t\t').replace("'", "")
    except IndexError:
        desc = ""
    try:
        year = tree.xpath('//div[@class="film-info"]/div[2]/div[@class="fi-desc"]/a/text()')[0]
    except (IndexError, ValueError):
        year = "?"
    try:
        director = tree.xpath('//div[@class="film-info"]/div[5]/div[@class="fi-desc"]/a/text()')[0].replace("'", "")
    except IndexError:
        director = ""

    film = dict(title_ua=title_ua, type=type_src, title_or=title_or,
                poster=poster, desc=desc, year=year, director=director)
    lenfilm, filmid = mainspider.add_mov(film)
    try:
        src = tree.xpath('//*[@id="pre"]')[0].attrib['src']
    except (IndexError, KeyError):
        src = ''
    all_links = {}

    def get_src(cont):
        if cont.find('https://') != -1:
            start = cont.find('file:"')
            end = cont.find('",', start)
            m3u = cont[start+6:end]
        else:
            m3u = src
        if m3u.find('https://www.youtube.com/embed/')!=-1:
            m3u = ''
        return m3u
    if src != '':
        cont, heads = get_html(src, heads)
        m3u = get_src(cont)
    else:
        m3u = ""

    if m3u == '':
        return None
    else:
        if m3u.find('new Playerjs') != -1 :
            src = m3u.split('"file":"')
            m3u = ",".join(src[1].split(',')[:-3])
            # print (m3u)
            addmovlink(filmid, m3u)
        else:
            addmovlink(filmid, m3u)
        print(title_ua + '\n' + m3u)
        return title_ua + '\n' + m3u


def save_to_file(il):
    fn = str(time.strftime("%Y-%m-%d_")) + str(BASE_URL.split("/")[-1]) + ".m3u"
    # encoding='utf-8-sig'
    try:
        with open(fn, "a", encoding='utf-8') as write_file:
            write_file.writelines("%s\n" % place for place in il)
    except:
        with open(fn, "w", encoding='utf-8') as write_file:
            write_file.writelines("%s\n" % place for place in il)
    global item_list
    il = []
    item_list = il
    return 'save'


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
    cont, head = get_html(URL, h, s)
    last_pg(cont)
    parse(cont, head, s)
    print("Job done")


def link_pars():
    links = ['https://uakino.club/filmi',
             'https://uakino.club/cartoon'
             ]
    for i in range(len(links)):
        global BASE_URL
        BASE_URL = links[i]
        main(BASE_URL)


if __name__ == '__main__':
    link_pars()
