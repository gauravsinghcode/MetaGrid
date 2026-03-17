from core.metadata_sync import metadata_resolver, payload_validator
from engine.query_builder import (
    sql_insert_builder,
    sql_update_builder,
    sql_select_query,
    sql_delete_query
)
from engine.query_executor import QueryExecutor
from core.models import TableMetadata, ColumnMetadata


class OperationEngine:  

    def __init__(self, db_path):
        self.executor = QueryExecutor(db_path)


    def insert(self, table_name, payload):

        resolved = metadata_resolver(table_name)

        if not resolved:
            raise ValueError(f"Table '{table_name}' not found or inactive")

        table_meta, columns = resolved

        cleaned_data = payload_validator(payload, columns)

        query, params = sql_insert_builder(
            table_meta,
            {col.name: col for col in columns},
            cleaned_data
        )

        return self.executor.execute(query, params)


    def select(self, table_name, filters=None, **kwargs):

        resolved = metadata_resolver(table_name)

        if not resolved:
            raise ValueError(f"Table '{table_name}' not found or inactive")

        table_meta, columns = resolved

        query, params = sql_select_query(
            table_meta,
            {col.name: col for col in columns},
            filters=filters,
            **kwargs
        )

        return self.executor.execute(query, params)


    def update(self, table_name, payload, pk_value):

        table_meta = TableMetadata.objects.get(name=table_name)

        columns_meta = ColumnMetadata.objects.filter(
            table=table_meta,
            is_active=True
        )

        columns_meta_dict = {c.name: c for c in columns_meta}

        query, params = sql_update_builder(
            table_meta,
            columns_meta_dict,
            payload,
            pk_value
        )

        return self.executor.execute(query, params)


    def delete(self, table_name, filters=None):

        resolved = metadata_resolver(table_name)

        if not resolved:
            raise ValueError(f"Table '{table_name}' not found or inactive")

        table_meta, columns = resolved
            
        query, params = sql_delete_query(
            table_meta,
            {col.name: col for col in columns},
            filters
        )

        if not query:
            raise ValueError("Unsafe delete operation prevented")

        return self.executor.execute(query, params)