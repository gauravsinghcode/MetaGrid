import sqlite3
# from .metadata_sync import sync_metadata

conn = sqlite3.connect("temp.db")
cursor = conn.cursor()

def inspect_schema(cursor):

    database = {}

    cursor.execute("SELECT * FROM sqlite_master where type='table'")

    results = cursor.fetchall()

    for result in results:

        tables = { "columns": {}, "foreign_keys": []}
        columns = {}

        cursor.execute(f"PRAGMA table_info({result[2]}) ")
        cols = cursor.fetchall()

        for col in cols:

            column = {}
            is_primary_key = col[5] == 1
            is_not_null = col[3] == 1

            column["type"] = col[2]
            if is_primary_key:
                column["nullable"] = False
            else:
                column["nullable"] = not is_not_null
            column["primary_key"] = True if col[5] == 1 else False
            column["unique"] = True if col[5] == 1 else False
            column["default"] = col[4]

            columns[col[1]] = column

            tables["columns"] = columns

        database[result[2]] = tables

    return database

metadata = inspect_schema(cursor=cursor)
print(metadata.keys())
# sync_metadata(metadata=metadata, cursor=cursor)