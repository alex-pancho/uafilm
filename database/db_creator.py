from dataclasses import fields
import sqlite3
from pathlib import Path


def create_table_from_dataclass(cls, table_name):
    cols = []
    for f in fields(cls):
        sql_type = "TEXT"
        if f.name == "_id":
            cols.append("_id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            cols.append(f"{f.name} {sql_type}")
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(cols)})"


def get_max_id(table_name, id_column="_id", db_file=None):
    """Повертає максимальний id з таблиці.

    Параметри:
    - table_name: назва таблиці в БД
    - id_column: назва стовпця ідентифікатора (за замовчуванням "_id")
    - db_file: шлях до файлу sqlite; якщо None, використовується database/films.sqlite поруч з цим файлом

    Повертає 0, якщо таблиця пуста або файл БД не існує.
    """
    db_path = Path(db_file) if db_file else Path(__file__).parent / "films.sqlite"
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX({id_column}) FROM {table_name}")
        row = cur.fetchone()
        max_id = row[0] if row and row[0] is not None else 1
        return int(max_id)
    finally:
        conn.close()
