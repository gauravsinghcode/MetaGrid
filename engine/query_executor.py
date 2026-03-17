from core.db_connections import get_adapter


class QueryExecutor:

    def __init__(self, db_path):
        self.adapter = get_adapter(db_path)

    def execute(self, query, params=None):

        if params is None:
            params = []

        cursor = self.adapter.execute(query, params)

        if cursor.description is None:
            self.adapter.conn.commit()
            return None

        columns = [col[0] for col in cursor.description]

        rows = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return rows