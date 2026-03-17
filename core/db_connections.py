from core.adapters.sqlite_adapter import SQLiteAdapter
    
def get_adapter(db_path: str):

    if not db_path:
        raise ValueError("Database path required")

    adapter = SQLiteAdapter(db_path)

    return adapter