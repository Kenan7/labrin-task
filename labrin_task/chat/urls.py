from django.urls import path

from chat import views

urlpatterns = [
    path("chat/", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
]
