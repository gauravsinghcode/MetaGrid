import sqlite3
from .base import BaseAdapter

class SQLiteAdapter(BaseAdapter):

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()


    def inspect_schema(self):

        schema = {}

        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )

        tables = self.cursor.fetchall()

        for table in tables:

            table_name = table[0]

            schema[table_name] = {
                "columns": self.get_columns(table_name)
            }

        return schema


    def get_columns(self, table_name):

        self.cursor.execute(f"PRAGMA table_info({table_name})")

        rows = self.cursor.fetchall()

        columns = []

        for row in rows:

            columns.append({
                "name": row[1],
                "data_type": row[2],
                "is_nullable": not bool(row[3]),
                "default_value": row[4],
                "is_primary_key": bool(row[5])
            })

        return columns


    def execute(self, query, params=None):

        if params is None:
            params = []

        cursor = self.conn.cursor()

        cursor.execute(query, params)

        return cursor