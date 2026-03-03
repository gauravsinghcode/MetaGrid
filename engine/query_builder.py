# CLAUSE BUILDERS

def where_clause_builder(columns_meta: dict, filters: dict | None=None):

    if filters:

        for col in filters.keys():
            if col not in columns_meta:
                return None, None, f"ColumnNotExists: {col} does not exists!"
        
        params = []
        filter_cols = []
        where_clause = []

        for col in filters.keys():
            filter_cols.append(f"{col}=?")

        filter_cols = " AND ".join(filter_cols)
        filter_values = filters.values()
        params.extend(filter_values)

        where_clause.append(f"WHERE {filter_cols}")

        return where_clause, params, None
    

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


# STATEMENTS BUILDERS

def sql_insert_builder(table_meta, columns_meta, cleaned_data: dict):

    table_name = table_meta.name

    columns = []
    params = []

    for key, value in cleaned_data.items():

        if columns_meta[key].primary_key:
            continue

        columns.append(key)
        params.append(value)

    if len(columns) != 0:

        cols_sql = ",".join(columns)
        params_sql = ",".join(["?"]*len(columns))

        insert_sql_query = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({params_sql})"

        return insert_sql_query, params
    
    return None, None
    

def sql_update_builder(table_meta, columns_meta: dict, cleaned_data: dict, pk_value):

    table_name = table_meta.name
    
    columns = []
    params = []
    pk_col = ""
    update_query = []

    for col in columns_meta.values():
        if col.primary_key:
            pk_col = col.name

    if pk_col == "" or pk_value is None:
        return None, None
    
    update_query.append(f"UPDATE {table_name} SET {cols_sql}")

    for key, value in cleaned_data.items():

        if key == pk_col:   
            continue

        columns.append(f"{key}=?")
        params.append(value)               

    if len(columns) != 0:

        filters = {pk_col: pk_value}

        where_clause, where_params, error = where_clause_builder(columns_meta=columns_meta, filters=filters)
        update_query.extend(where_clause)
        params.extend(where_params)

        if error:
            return None, None

    cols_sql = ",".join(columns)
    update_query = " ".join(update_query)

    return update_query, params


def sql_select_query(table_meta, columns_meta: dict,  filters:dict | None=None, select_cols: list | None=None, limit: int| None=None, offset: int | None=None, order_by: str | None=None, sort_order: str | None=None):

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

    select_query_builder.append(f"SELECT ({select_cols}) FROM {table_name}")

    where_clause, where_params = where_clause_builder(columns_meta=columns_meta, filters=filters)

    select_query_builder.extend(where_clause)
    params.extend(where_params)                 

    if limit is not None:
        params.append(limit)
        select_query_builder.append("LIMIT ?")
    
    if offset is not None:
        params.append(offset)
        select_query_builder.append("OFFSET ?")

    if order_by is not None:

        if order_by not in columns_meta:
            return None, None
    
        if sort_order is not None and sort_order in ["ASC", "DESC"] and order_by is not None:
            select_query_builder.append(f"ORDER BY {order_by} {sort_order}")
        select_query_builder.append(f"ORDER BY {order_by} ASC")   

    select_sql_query = " ".join(select_query_builder)

    return select_sql_query, params


def sql_delete_query(table_meta, columns_meta: dict, filters: dict | None=None, limit:int | None=None):

    table_name = table_meta.name
    # filter_cols = []
    params = []
    pk_col = None
    delete_query_builder = []
    delete_query_builder.append(f"DELETE FROM {table_name}")

    if filters is None:
        return None, None
    
    for col in columns_meta.values():
        if col.primary_key:
            pk_col = col.name

    if limit is None and pk_col not in filters:
        return None, None
    
    # for col in filters.keys():
    #     if col not in columns_meta:
    #         return None, None
        
    #     filter_cols.append(f"{col}=?")

    # filter_cols = " AND ".join(filter_cols)
    # filter_values = filters.values()
    # params.extend(filter_values)

    where_clause, where_params, error = where_clause_builder(columns_meta=columns_meta, filters=filters)
    params.extend(where_params)
    delete_query_builder.extend(where_clause)

    if error:
        return None, None

    if limit is not None:
        params.append(limit)
    else:
        params.append(1)
    
    delete_query_builder.append("LIMIT ?")
    delete_sql_query = " ".join(delete_query_builder)

    return delete_sql_query, params