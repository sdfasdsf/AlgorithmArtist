from django.urls import path, include
from . import views

app_name = "AI"

urlpatterns = [
    path("tmovingbot/", views.TMOVINGBOT, name="TMOVINGBOT"),
]
