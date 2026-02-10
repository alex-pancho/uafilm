
import os
import re
import sys
import sqlite3
# import niquests
# from pathlib import Path
from flask import jsonify


def extract_ashdi_data(html: str):
    data = {}

    m3u = re.search(r"file\s*:\s*['\"]([^'\"]+\.m3u8)['\"]", html)
    poster = re.search(r"poster\s*:\s*['\"]([^'\"]+)['\"]", html)
    sub = re.search(r"subtitle\s*:\s*['\"]([^'\"]*)['\"]", html)

    if m3u:
        data["m3u"] = m3u.group(1)
    if poster:
        data["poster"] = poster.group(1)
    if sub:
        data["subtitle"] = sub.group(1)

    return data


def base_path():
    # якщо exe
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # якщо звичайний запуск
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(base_path(), "database", "films.sqlite")


def get_db():

    db = sqlite3.connect(DB_PATH)
    return db


def parse_player_and_get_m3u(url, headers):
    # ТУТ викликаєш:
    # scrapy crawl player_spider -a url=...
    # або свою requests+regex логіку

    print("Парсю:", url)

    return "https://example.com/video.m3u8"


def fetch_m3u(playlist_id, headers):
    db = get_db()

    playlist = db.execute("""
        SELECT m3u_url, ext_player
        FROM playlist p
        WHERE p.content_id =  ?
    """, (playlist_id,)).fetchone()

    if not playlist:
        return {"status": "error", "message": "Playlist not found"}

    url_player = playlist["ext_player"]
    m3u_link = playlist["m3u_url"]

    if not url_player:
        return {"status": "error", "message": "No ext_player url"}
    
    if m3u_link is not None:
        return jsonify({"status": "exists", "message": "Exist link. Rewrite?"})

    # ТУТ ти викликаєш свого павука / парсер
    m3u_url = parse_player_and_get_m3u(url_player, headers)

    db.execute(
        "UPDATE playlist SET m3u_url = ? WHERE _id = ?",
        (m3u_url, playlist_id)
    )
    db.commit()

    return {"status": "ok", "message": "m3u оновлено"}
