import json
from typing import Any

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .forms import FileUploadForm
from .models import FileModel

User = get_user_model()


@login_required
def file_upload_view(request):
    if request.method == "POST":
        current_user = request.user

        my_file = request.FILES.get("file")
        description = request.POST.get(
            "file_description", "default description"
        )

        file_obj = FileModel.objects.create(
            name=my_file.name,
            description=description,
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


# @login_required
# def file_detail_view(request, id):
#     try:
#         file_item = FileModel.objects.get(id=id)
#         if (request.user in file_item.viewers.all()) or (
#             request.user == file_item.owner
#         ):
#             return render(
#                 request,
#                 "pages/filemodel_detail.html",
#                 {"fileitem": file_item, "room_name": file_item.id},
#             )
#         else:
#             return render(request, "403.html", {})

#     except FileModel.DoesNotExist:
#         return render(request, "404.html", {})


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
                    "pages/filemodel_detail.html",
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

    def get_queryset(self):
        current_user = User.objects.get(id=self.request.user.id)
        return (
            FileModel.objects.filter(owner=current_user)
            .select_related("owner")
            .prefetch_related("viewers", "commenters")
        )


file_list_view = FileListView.as_view()


@login_required
def refresh_file_list_view(request):
    return render(
        request,
        "pages/filelist_swap.html",
        {FileModel.objects.filter(owner=request.user)},
    )


@login_required
def remove_from_viewer(request, viewer_id, filemodel_id):
    if request.method == "POST":
        try:
            current_file = FileModel.objects.get(id=filemodel_id)
            if current_file:
                if request.user.id == current_file.owner.id:
                    user = User.objects.get(id=viewer_id)
                    current_file.viewers.remove(user)
                    return redirect(
                        reverse(
                            "file_detail_view_url", kwargs={"id": filemodel_id}
                        )
                    )
                else:
                    return render(request, "403.html", {})
        except:
            return render(request, "404.html", {})
    else:
        return render(request, "403.html", {})


@login_required
def remove_from_commenter(request, commenter_id, filemodel_id):
    if request.method == "POST":
        try:
            current_file = FileModel.objects.get(id=filemodel_id)
            if current_file:
                if request.user.id == current_file.owner.id:
                    user = User.objects.get(id=commenter_id)
                    current_file.commenters.remove(user)
                    return redirect(
                        reverse(
                            "file_detail_view_url", kwargs={"id": filemodel_id}
                        )
                    )
                else:
                    return render(request, "403.html", {})
        except:
            return render(request, "404.html", {})
    else:
        return render(request, "403.html", {})


@login_required
def add_viewer_commenter(request, filemodel_id):
    if request.method == "POST":
        current_file = FileModel.objects.get(id=filemodel_id)
        if current_file:
            if request.user.id == current_file.owner.id:
                try:
                    credentials = request.POST.get("credentials")
                    current_user = User.objects.filter(
                        Q(username=credentials) | Q(email=credentials)
                    ).first()
                    if request.POST.get("viewer_check", "off") == "on":
                        current_file.viewers.add(current_user)
                    if request.POST.get("commenter_check", "off") == "on":
                        current_file.commenters.add(current_user)

                    return redirect(
                        reverse(
                            "file_detail_view_url",
                            kwargs={"id": filemodel_id},
                        )
                    )
                except User.DoesNotExist:
                    return render(request, "404.html", {})

            else:
                return render(request, "403.html", {})
    else:
        return render(request, "403.html", {})


@login_required
def file_create_view(request):
    form = FileUploadForm(request.POST or None)

    queryset = None
    if request.method == "POST":
        print(form)
        if form.is_valid():
            form.save()

        return redirect(reverse("file_create_view"))

    elif request.method == "GET":
        current_user = User.objects.get(id=request.user.id)
        queryset = FileModel.objects.filter(owner=current_user)

    return render(
        request,
        "pages/create_filemodel.html",
        {"form": form, "filemodel_list": queryset},
    )
