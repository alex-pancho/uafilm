
# 🧠 Ідея

Ти зберігаєш десь файл, наприклад:

```
https://site.com/data.json
```

або

```
https://site.com/update.sql
```

Ми зараз зробимо варіант з **JSON** (безпечніше).

---

# 1️⃣ Кнопка в шаблоні

`templates/index.html`

```html
<form action="/update" method="post">
    <button type="submit">🔄 Оновити базу</button>
</form>
```

---

# 2️⃣ Flask-роут

`miniapp/app.py`

```python
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    import updater
    result = updater.run()
    return redirect("/?msg=" + result)
```

---

# 3️⃣ updater.py (серце системи)

```python
import sqlite3
import requests
from pathlib import Path

DB_PATH = Path("database/films.sqlite")
DATA_URL = "https://example.com/data.json"  # <-- твій файл

def run():
    print("Downloading update...")

    r = requests.get(DATA_URL, timeout=30)
    r.raise_for_status()
    data = r.json()  # список фільмів

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for item in data:
        cur.execute("""
        INSERT OR REPLACE INTO content
        (_id, title_ua, title_or, type_src, year, director,
         description, poster, imdb, m3u_links, json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["_id"],
            item["title_ua"],
            item["title_or"],
            item["type_src"],
            item["year"],
            item["director"],
            item["description"],
            item["poster"],
            item["imdb"],
            item["m3u_links"],
            item["json"],
        ))

    conn.commit()
    conn.close()

    return "ok"
```

---

# 4️⃣ Формат data.json

```json
[
  {
    "_id": 1,
    "title_ua": "Тачки",
    "title_or": "Cars",
    "type_src": "cartoon",
    "year": "2006",
    "director": "John Lasseter",
    "description": "Мультфільм про авто",
    "poster": "https://...",
    "imdb": "7.1",
    "m3u_links": "https://...",
    "json": "{}"
  }
]
```

---

# 🛡 Захист від ламання

Можна додати:

```python
try:
    updater.run()
except Exception as e:
    return f"Помилка: {e}"
```


# ❗ Дуже важлива фішка (версії)

Додай таблицю:

```sql
CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT
);
```

і перевіряй версію перед оновленням.

# Безпека

## ✅ Варіант 1: просто Base64

### 🔒 Шифруємо (експортер)

```python
import base64

with open("data.json", "rb") as f:
    raw = f.read()

encoded = base64.b64encode(raw)

with open("data.b64", "wb") as f:
    f.write(encoded)

print("Saved as data.b64")
```

Ти публікуєш:

```
data.b64
```

---

### 🔓 Розшифровка у клієнта

```python
import base64
import json

with open("data.b64", "rb") as f:
    encoded = f.read()

decoded = base64.b64decode(encoded)

data = json.loads(decoded.decode("utf-8"))

print(data[0])
```

---

## ✅ Варіант 2: Base64 + “ключ” (XOR) 🔑

(вже краще, але все ще просто)

### 🔒 Шифруємо

```python
import base64

KEY = b"mysecret"

with open("data.json", "rb") as f:
    raw = f.read()

xored = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(raw))
encoded = base64.b64encode(xored)

with open("data.enc", "wb") as f:
    f.write(encoded)
```

---

### 🔓 Розшифровка

```python
import base64, json

KEY = b"mysecret"

with open("data.enc", "rb") as f:
    encoded = f.read()

xored = base64.b64decode(encoded)
raw = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(xored))

data = json.loads(raw.decode("utf-8"))
```

Без ключа → нічого не зрозуміло.

