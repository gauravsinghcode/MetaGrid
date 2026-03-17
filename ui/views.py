from django.shortcuts import render, redirect
from core.schema_inspector import inspect_schema
from core.models import TableMetadata
from engine.operation_engine import OperationEngine
from core.metadata_sync import metadata_resolver
from django.http import JsonResponse

def home(request):

    return render(request, "home.html")


def connect_database(request):

    if request.method == "POST":

        db_path = request.POST.get("db_path")

        if db_path:
            inspect_schema(db_path)

        return redirect("table_explorer")

    return render(request, "connect.html")


def table_explorer(request):

    tables = TableMetadata.objects.filter(is_active=True)

    return render(request, "pages/tables.html", {
        "tables": tables
    })


def table_view(request, table_name):

    engine = OperationEngine("temp.db")

    page = int(request.GET.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    search = request.GET.get("search")
    order_by = request.GET.get("order_by")
    sort = request.GET.get("sort", "ASC")

    filter_column = request.GET.get("filter_column")
    filter_operator = request.GET.get("filter_operator")
    filter_value = request.GET.get("filter_value")

    filters = None

    if search:

        table_meta, columns_meta = metadata_resolver(table_name)

        search_columns = [col.name for col in columns_meta if col.data_type in ["TEXT", "VARCHAR"]]

        filters = {
            "__search__": {
                "value": search,
                "columns": search_columns
            }
        }

    elif filter_column and filter_operator and filter_value:

        filters = {
            filter_column: {
                filter_operator: filter_value
            }
        }

    rows = engine.select(
    table_name,
    filters=filters,
    limit=limit,
    offset=offset,
    order_by=order_by,
    sort_order=sort
    )

    print("FILTERS:", filters)

    table_meta, columns_meta = metadata_resolver(table_name)

    columns = [col.name for col in columns_meta]

    return render(
        request,
        "pages/table_view.html",
        {
            "table_name": table_name,
            "rows": rows,
            "columns": columns,
            "page": page,
            "search": search,
            "order_by": order_by,
            "sort": sort
        }
    )


def add_row(request, table_name):

    table_meta, columns = metadata_resolver(table_name)

    form_fields = [col for col in columns if not col.is_primary_key]

    if request.method == "POST":

        payload = {}

        for col in form_fields:
            payload[col.name] = request.POST.get(col.name)

        engine = OperationEngine("temp.db")

        engine.insert(table_name, payload)

        return redirect("table_view", table_name=table_name)

    return render(
        request,
        "pages/add_row.html",
        {
            "table_name": table_name,
            "fields": form_fields,
        },
    )


def edit_row(request, table_name, pk):

    engine = OperationEngine("temp.db")

    table_meta, columns_meta = metadata_resolver(table_name)

    columns = [col.name for col in columns_meta]

    rows = engine.select(table_name, filters={"id": pk})
    row = rows[0] if rows else None

    if request.method == "POST":

        payload = {}

        for col in columns:
            if col != "id":
                payload[col] = request.POST.get(col)

        engine.update(
            table_name,
            payload,
            pk
        )

        return redirect("table_view", table_name=table_name)

    return render(
        request,
        "pages/edit_row.html",
        {
            "table_name": table_name,
            "row": row,
            "columns": columns
        }
    )


def delete_row(request, table_name, pk):

    engine = OperationEngine("temp.db")

    filters = {"id": pk}

    engine.delete(table_name, filters)

    return redirect("table_view", table_name=table_name)


def update_cell(request, table_name, pk):

    if request.method == "POST":

        column = request.POST.get("column")
        value = request.POST.get("value")

        engine = OperationEngine("temp.db")

        payload = {column: value}
        print(payload)

        engine.update(
            table_name,
            payload,
            pk
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"})