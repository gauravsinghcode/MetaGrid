from core.db_connections import get_adapter
from core.metadata_sync import sync_metadata


def inspect_schema(db_path):

    adapter = get_adapter(db_path)

    schema = adapter.inspect_schema()

    sync_metadata(schema)