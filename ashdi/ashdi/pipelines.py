import sqlite3

class SQLitePipeline:

    def open_spider(self, spider):
        self.conn = sqlite3.connect("films.db")
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, 
            title TEXT, 
            ukr_name TEXT, 
            eng_name TEXT,
            year TEXT, 
            vip_link TEXT, 
            image_link TEXT,
            club_link TEXT, 
            original_id INTEGER UNIQUE
        )
        """)

    def process_item(self, item, spider):
        self.conn.execute("""
        INSERT OR IGNORE INTO content
        (type,title,ukr_name,eng_name,year,vip_link,image_link,club_link,original_id)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            item["type"], item["title"], item["ukr_name"],
            item["eng_name"], item["year"], item["vip_link"],
            item["image_link"], item["club_link"], item["original_id"]
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()
