
import os
import re
import json
import sys
import sqlite3
import niquests

# from pathlib import Path
from flask import jsonify


def extract_ashdi_data(html: str) -> dict:
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

def get_text_key(text, keyword, end: str = "\n"):
    start = text.find(keyword)
    if start == -1:
        return None
    start = start + len(keyword)
    end = text.find(end, start)
    if end == -1:
        end = len(text)
    return text[start:end]

def extract_player_block(body):
    key = "var player = new Playerjs"
    return get_text_key(body, key, "});")


def parse_stream(html: str):
    """
    Extract m3u8 from JS player
    """
    item = {}
    src = extract_player_block(html)
    if not src:
        print(f"Player not found!")
        return

    file = get_text_key(src, '(', '') + "}"
    subtitle = get_text_key(src, 'subtitle:"', '"')
    j_file = json.loads(file)
    item["m3u_links"] = {
        "m3u_link": file,
        "subtitle": subtitle or "",
    }


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


def parse_player_and_get_m3u(url, headers) -> dict:
    # ТУТ викликаєш:
    # scrapy crawl player_spider -a url=...
    # або свою requests+regex логіку
    if "ashdi.vip" in url:
        resp = niquests.get(url)
    else:
        resp = niquests.get(url, headers=headers)
    resp.raise_for_status()
    html_text = resp.text
    # fallback: try to extract .m3u8 from inline player config
    ashdi = extract_ashdi_data(html_text)
    # ashdi = parse_stream(html_text)
    return ashdi if ashdi else None


def fetch_m3u(playlist_id, headers):
    db = get_db()

    playlist = db.execute("""
        SELECT m3u_url, ext_player
        FROM playlist p
        WHERE p.content_id =  ?
    """, (playlist_id,)).fetchone()

    if not playlist:
        return {"status": "error", "message": "Playlist not found"}
   
    m3u_link = playlist[0]
    url_player = playlist[1]

    if not url_player:
        return {"status": "error", "message": "No ext_player url"}
    
    if m3u_link is not None:
        return jsonify({"status": "exists", "message": "Exist link. Rewrite?"})

    # ТУТ ти викликаєш свого павука / парсер
    m3u_url = parse_player_and_get_m3u(url_player, headers)
    if m3u_url.get("m3u", False):
        db.execute(
            "UPDATE playlist SET m3u_url = ? WHERE _id = ?",
            (m3u_url["m3u"], playlist_id)
        )
        if m3u_url.get("subtitle", False):
            db.execute(
            "UPDATE playlist SET subtitle = ? WHERE _id = ?",
            (m3u_url["subtitle"], playlist_id)
            )
        db.commit()

        return {"status": "ok", "message": "m3u оновлено"}
    else:
        return {"status": "fail", "message": "get m3u fail"}