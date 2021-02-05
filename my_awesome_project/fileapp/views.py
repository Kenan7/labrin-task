from typing import Any

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .models import FileModel

User = get_user_model()


@login_required
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

        return HttpResponse("Uploaded", status=201)
    else:
        return HttpResponse("Forbidden", status=403)


class FileDetailView(LoginRequiredMixin, DetailView):

    model = FileModel
    # pk_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        try:
            file_item = FileModel.objects.get(id=id_)

            if (self.request.user in file_item.viewers.all()) or (
                self.request.user == file_item.owner
            ):
                return render(
                    self.request,
                    "fileapp/filemodel_detail.html",
                    {"fileitem": file_item, "room_name": file_item.id},
                )
            else:
                return render(self.request, "403.html", {})

        except FileModel.DoesNotExist:
            return render(self.request, "404.html", {})


file_detail_view = FileDetailView.as_view()


class FileListView(LoginRequiredMixin, ListView):
    model = FileModel
    template_name = "pages/home.html"

    # def get_queryset(self):
    #     print(super().get_queryset())
    #     return super().get_queryset()


file_list_view = FileListView.as_view()


@login_required
def refresh_file_list_view(request):
    return render(
        request,
        "pages/filelist_swap.html",
        {FileModel.objects.filter(owner=request.user)},
    )
