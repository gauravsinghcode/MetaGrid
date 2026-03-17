ALLOWED_OPERATORS = {"=", ">", "<", ">=", "<=", "LIKE"}


def compile_filters(filters, columns_meta):

    params = []
    
    if "AND" in filters or "OR" in filters:

        operator = "AND" if "AND" in filters else "OR"
        expressions = filters[operator]

        compiled = []

        for expr in expressions:

            sql, sub_params = compile_filters(expr, columns_meta)

            compiled.append(f"({sql})")
            params.extend(sub_params)

        return f" {operator} ".join(compiled), params

    if "NOT" in filters:

        sql, sub_params = compile_filters(filters["NOT"], columns_meta)

        return f"NOT ({sql})", sub_params


    sql_parts = []

    for col, condition in filters.items():

        if col not in columns_meta:
            raise ValueError(f"ColumnNotExists: {col}")

        if isinstance(condition, dict):
            op = condition.get("op", "=")
            value = condition.get("value")
        else:
            op = "="
            value = condition

        if op not in ALLOWED_OPERATORS:
            raise ValueError(f"InvalidOperator: {op}")

        sql_parts.append(f"{col} {op} ?")
        params.append(value)

    return " AND ".join(sql_parts), params