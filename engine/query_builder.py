from engine.filter_engine import compile_filters

# RULES

OPERATION_RULES = {

    "SELECT": {
        "filters_required": False,
        "pk_required": False,
        "limit_default": None
    },
    "UPDATE": {
        "filters_required": True,
        "pk_required": True,
        "limit_default": None
    },
    "DELETE": {
        "filters_required": True,
        "pk_required": False,
        "limit_default": 1
    }
}

ALLOWED_OPERATORS = {
    "=", ">", "<", ">=", "<=", "LIKE"
}


# CLAUSE BUILDERS

def where_clause_builder(columns_meta, filters=None):

    if not filters:
        return [], [], None

    try:

        if "__search__" in filters:

            search_value = filters["__search__"]["value"]
            search_columns = filters["__search__"]["columns"]

            clauses = []
            params = []

            for col in search_columns:
                if col in columns_meta:
                    clauses.append(f"{col} LIKE ?")
                    params.append(f"%{search_value}%")

            if clauses:
                sql = " OR ".join(clauses)
                return [f"WHERE ({sql})"], params, None

            return [], [], None

        sql, params = compile_filters(filters, columns_meta)

        return [f"WHERE {sql}"], params, None

    except ValueError as e:
        return None, None, str(e)


# STATEMENTS BUILDERS

def sql_insert_builder(table_meta, columns_meta, cleaned_data: dict):

    table_name = table_meta.name

    columns = []
    params = []

    for key, value in cleaned_data.items():

        if columns_meta[key].is_primary_key:
            continue

        columns.append(key)
        params.append(value)

    if len(columns) != 0:

        cols_sql = ",".join(columns)
        params_sql = ",".join(["?"]*len(columns))

        insert_sql_query = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({params_sql})"

        return insert_sql_query, params
    
    return None, None
    

def sql_update_builder(table_meta, columns_meta, cleaned_data, pk_value):

    table_name = table_meta.name

    set_parts = []
    params = []

    for key, value in cleaned_data.items():

        if key not in columns_meta:
            raise ValueError(f"Invalid column: {key}")

        set_parts.append(f"{key} = ?")
        params.append(value)

    set_clause = ", ".join(set_parts)

    pk_column = None

    for col in columns_meta.values():
        if col.is_primary_key:
            pk_column = col.name
            break

    if not pk_column:
        raise ValueError("Primary key not found")

    params.append(pk_value)

    query = f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE {pk_column} = ?
    """

    return query, params


def sql_select_query(table_meta, columns_meta, filters=None, select_cols=None, limit=None, offset=None, order_by=None, sort_order="ASC"):
    
    params = []

    table_name = table_meta.name

    if select_cols is not None:
        for col in select_cols:
            if col not in columns_meta:
                return None, None
            
        select_cols = ",".join(select_cols)
    else:
        select_cols = "*"

    select_query_builder = []

    select_query_builder.append(f"SELECT {select_cols} FROM {table_name}")

    where_clause, where_params, error = where_clause_builder(columns_meta=columns_meta, filters=filters)

    if error:
         return None, None

    select_query_builder.extend(where_clause)
    params.extend(where_params)         

    if order_by:

        if order_by not in columns_meta:
            return None, None

        if sort_order in ["ASC", "DESC"]:
            select_query_builder.append(f"ORDER BY {order_by} {sort_order}")
        else:
            select_query_builder.append(f"ORDER BY {order_by} ASC")        

    if limit is not None:
        params.append(limit)
        select_query_builder.append("LIMIT ?")
    
    if offset is not None:
        params.append(offset)
        select_query_builder.append("OFFSET ?")

    select_sql_query = " ".join(select_query_builder)

    return select_sql_query, params


def sql_delete_query(table_meta, columns_meta: dict, filters: dict | None=None):

    table_name = table_meta.name
    params = []
    pk_col = None
    delete_query_builder = []
    delete_query_builder.append(f"DELETE FROM {table_name}")

    if filters is None:
        return None, None
    
    for col in columns_meta.values():
        if col.is_primary_key:
            pk_col = col.name

    if pk_col not in filters:
        return None, None
    
    where_clause, where_params, error = where_clause_builder(columns_meta, filters)

    if error:
        return None, None

    delete_query_builder.extend(where_clause)
    params.extend(where_params)
    
    delete_sql_query = " ".join(delete_query_builder)

    return delete_sql_query, params