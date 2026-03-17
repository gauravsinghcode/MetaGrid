from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("connect/", views.connect_database, name="connect_database"),
    path("tables/", views.table_explorer, name="table_explorer"),
    path("table/<str:table_name>/", views.table_view, name="table_view"),
    path("table/<str:table_name>/add/", views.add_row, name="add_row"),
    path("table/<str:table_name>/delete/<int:pk>/", views.delete_row, name="delete_row"),
    path("table/<str:table_name>/edit/<int:pk>/", views.edit_row, name="edit_row"),
    path("table/<str:table_name>/update/<int:pk>/", views.update_cell,name="update_cell",)
]