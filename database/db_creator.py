from dataclasses import fields

def create_table_from_dataclass(cls, table_name):
    cols = []
    for f in fields(cls):
        sql_type = "TEXT"
        if f.name == "_id":
            cols.append("_id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            cols.append(f"{f.name} {sql_type}")
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(cols)})"
