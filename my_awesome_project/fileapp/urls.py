from django.urls import path

from .views import file_detail_view, file_upload_view

urlpatterns = [
    path(
        "upload/",
        file_upload_view,
        name="file_upload_view",
    ),
    path("<int:id>/", file_detail_view, name="file_detail_view_url"),
    # path(
    #     "refresh/",
    # ),
]
