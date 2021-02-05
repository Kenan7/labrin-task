from django.urls import path

from fileapp.views import file_detail_view, file_upload_view

urlpatterns = [
    path(
        "upload/",
        file_upload_view,
    ),
    path(
        "<int:id>/",
        file_detail_view,
    ),
]
