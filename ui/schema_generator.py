def map_db_type(data_type):

    mapping = {
        "INTEGER": "number",
        "TEXT": "text",
        "REAL": "number",
        "BOOLEAN": "checkbox",
        "DATE": "date"
    }

    return mapping.get(data_type.upper(), "text")


def generate_table_schema(table_meta, columns):

    schema = {
        "type": "table",
        "table": table_meta.name,
        "columns": [],
    }

    for col in columns:

        schema["columns"].append({
            "name": col.name,
            "type": col.data_type,
            "nullable": col.nullable,
            "primary_key": col.primary_key
        })

    return schema


def generate_form_schema(table_meta, columns):

    schema = {
        "type": "form",
        "table": table_meta.name,
        "fields": []
    }

    for col in columns:

        if col.primary_key:
            continue

        schema["fields"].append({
            "name": col.name,
            "type": map_db_type(col.data_type),
            "required": not col.nullable
        })

    return schema


def generate_filter_schema(columns):

    filters = []

    for col in columns:

        filters.append({
            "name": col.name,
            "type": map_db_type(col.data_type),
            "operators": ["=", ">", "<", ">=", "<=", "LIKE"]
        })

    return filters