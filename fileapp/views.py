from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, RedirectView, UpdateView

from my_awesome_project.users.models import User

from .models import FileModel

User = get_user_model()


def file_upload_view(request):
    if request.method == "POST":
        current_user = request.user

        my_file = request.FILES.get("file")

        file_obj = FileModel.objects.create(
            name=my_file.name,
            description="def",
            file_itself=my_file,
            owner=current_user,
        )

        file_obj.viewers.set(
            [
                current_user,
            ]
        )
        file_obj.commenters.set(
            [
                current_user,
            ]
        )


class FileDetailView(LoginRequiredMixin, DetailView):

    model = User
    # pk_url_kwarg = "pk"
    # slug_field = "username"
    # slug_url_kwarg = "username"

    def get_object(self):
        id_ = self.kwargs.get("id")
        try:
            file_item = FileModel.objects.get(id=id_)

            if (self.request.user in file_item.viewers.all()) or (
                self.request.user == file_item.owner
            ):
                return render(
                    self.request, "file_detail.html", {"file_item": file_item}
                )
            else:
                return render(self.request, "403.html", {})

        except FileModel.DoesNotExist:
            return render(self.request, "404.html", {})


file_detail_view = FileDetailView.as_view()
