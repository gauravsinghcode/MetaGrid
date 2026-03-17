from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # MetaGrid UI
    path("", include("ui.urls")),
]