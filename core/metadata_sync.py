from .models import TableMetadata, ColumnMetadata
from django.db import transaction
from django.utils import timezone

def initial_table_sync(metadata: dict):

    for table in metadata.keys():
        TableMetadata.objects.create(name=table, is_active=True, is_synced=True)


def add_new_table(new_tables: set):

    for table in new_tables:
        TableMetadata.objects.create(name=table, is_active=True, is_synced=True)


def inactivate_table(inactive_tables: set):

    for table in inactive_tables:
        TableMetadata.objects.filter(name=table).update(is_active=False)


def sync_table_metadata(metadata: dict):

    md_tables = set(metadata.keys())
    db_tables = set(TableMetadata.objects.values_list('name', flat=True))
    new_tables = md_tables.difference(db_tables)
    inactive_tables = db_tables.difference(md_tables)

    if not TableMetadata.objects.exists():
        initial_table_sync(metadata=metadata)

    else:
        add_new_table(new_tables=new_tables)
        inactivate_table(inactive_tables=inactive_tables)


def normalize_database(data_type: str):

    d_type = data_type.upper()

    if d_type in ["VARCHAR", "CHAR", "TEXT"]:
        return "STRING"
    
    if d_type in ["INT", "INTEGER", "TINYINT"]:
        return "INTEGER"
    
    if d_type in ["FLOAT", "DECIMAL", "REAL"]:
        return "FLOAT"
    
    if d_type in ["BOOL", "BOOLEAN"]:
        return "BOOLEAN"
    
    else:
        return "UNKNOWN"
    

def typecast_data(data, canonical_type):

    if canonical_type == "INTEGER":

        if isinstance(data, int):
            return True, data
        
        else:
            try:
                return True, int(data)
            except ValueError:
                return False, None
        
    if canonical_type == "BOOLEAN":

        if isinstance(data, bool):
            return True, data
        
        else:
            if data in ["False", "false", "FALSE", False]:
                data = False
                return True, data

            if data in ["True", "true", "TRUE", True]:
                data = True
                return True, data
            
            else:
                return False, None
        
    if canonical_type == "STRING":

        if isinstance(data, str):
            return True, data
        
        else:
            if not isinstance(data, str):
                return True, str(data)
            
            else:
                return False, None


@transaction.atomic
def sync_columns_for_table(table_meta, db_columns):

    now = timezone.now()

    db_column_map = {col["name"]: col for col in db_columns}

    metadata_qs = ColumnMetadata.objects.filter(table=table_meta)
    metadata_map = {col.name: col for col in metadata_qs}

    for column_name, db_col in db_column_map.items():

        normalized_type = normalize_database(db_col.get("data_type"))

        if column_name not in metadata_map:
            ColumnMetadata.objects.create(
                table=table_meta,
                name=column_name,
                data_type=normalized_type,
                is_nullable=db_col.get("is_nullable"),
                default_value=db_col.get("default_value"),
                is_primary_key=db_col.get("is_primary_key"),
                is_active=True,
            )

        else:
            meta_col = metadata_map[column_name]
            changed = False

            if meta_col.data_type != normalized_type:
                meta_col.data_type = normalized_type
                changed = True

            if meta_col.is_nullable != db_col.get("is_nullable"):
                meta_col.is_nullable = db_col.get("is_nullable")
                changed = True

            if meta_col.default_value != db_col.get("default_value"):
                meta_col.default_value = db_col.get("default_value")
                changed = True

            if meta_col.is_primary_key != db_col.get("is_primary_key"):
                meta_col.is_primary_key = db_col.get("is_primary_key")
                changed = True

            if not meta_col.is_active:
                meta_col.is_active = True
                changed = True

            meta_col.last_seen_at = now
            changed = True

            if changed:
                meta_col.save()

    for column_name, meta_col in metadata_map.items():
        if column_name not in db_column_map and meta_col.is_active:
            meta_col.is_active = False
            meta_col.save(update_fields=["is_active"])


def sync_metadata(metadata: dict):

    sync_table_metadata(metadata=metadata)

    tables = TableMetadata.objects.all()

    for table in tables:
        columns = metadata.get(table.name, {}).get("columns", [])
        sync_columns_for_table(table, columns)


def metadata_resolver(table_name):

    is_table_exists = TableMetadata.objects.filter(name=table_name).exists()

    if (is_table_exists):

        tableObj = TableMetadata.objects.get(name=table_name)

        if (tableObj.is_active and tableObj.is_synced):

            ColumnObj = ColumnMetadata.objects.filter(table=tableObj).filter(is_active=True)

            return tableObj, ColumnObj
        
    return None


def payload_validator(payload: dict, columns):

    payload_cols = payload.keys()
    required_cols = list(columns.filter(is_nullable=False).values_list("name", flat=True))
    cols_map = {}
    cleaned_data = {}

    for col in columns:
        cols_map[col.name] = col

    for col in required_cols:
        if col not in payload_cols and not cols_map[col].is_primary_key:
            return f"InvlaidValueError: {col} is a required field but no valid value is provided!"

    for col in payload_cols:
        if col not in cols_map:
            return f"ColumnNotExistsError: {col} does not exists!"
        
        if cols_map[col].is_primary_key:
            return f"PrimaryKeyError: {col} is the primary key. Cannot be altered!"
        
        if payload[col] == None and cols_map[col].is_nullable:
            cleaned_data[col] = payload[col]

        else:
            canonical_type = cols_map[col].data_type
            typecast_possible, casted_value = typecast_data(payload[col], canonical_type=canonical_type)

            if typecast_possible:
                cleaned_data[col] = casted_value
            else:
                return f"DataTypeError: Invalid data types are given!"
            
    return cleaned_data