import sqlite3
import json
from pathlib import Path
from database.db_creator import create_table_from_dataclass
from database.models import UkinoModel

db_file_path = Path(__file__).parent.parent.parent / "database" / "films.sqlite"

class SQLitePipeline:

    def open_spider(self, spider):
        self.conn = sqlite3.connect(db_file_path)
        sql = create_table_from_dataclass(UkinoModel, "content")
        self.cur = self.conn.cursor()
        self.cur.execute(sql)
        self.conn.commit()

    def process_item(self, item, spider):
        
        item = dict(item)
        item.pop("_id", None)
        keys = ", ".join(item.keys())

        placeholders = ", ".join(["?"] * len(item))
        values = list(item.values())

        sql = f"INSERT INTO content ({keys}) VALUES ({placeholders})"
        self.cur.execute(sql, values)
        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()
