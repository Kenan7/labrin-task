from django.urls import path

from .views import (
    add_viewer_commenter,
    file_detail_view,
    file_upload_view,
    remove_from_commenter,
    remove_from_viewer,
)

urlpatterns = [
    path(
        "upload/",
        file_upload_view,
        name="file_upload_view",
    ),
    path(
        "<int:id>/",
        file_detail_view,
        name="file_detail_view_url",
    ),
    path(
        "remove_viewer/<int:viewer_id>/<int:filemodel_id>/",
        remove_from_viewer,
        name="remove_viewer",
    ),
    path(
        "remove_commenter/<int:commenter_id>/<int:filemodel_id>/",
        remove_from_commenter,
        name="remove_commenter",
    ),
    path(
        "add_viewer_commenter/<int:filemodel_id>/",
        add_viewer_commenter,
        name="add_viewer_commenter_to_file",
    ),
    # path(
    #     "refresh/",
    # ),
]
