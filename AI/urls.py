from django.urls import path, include
from . import views

app_name = "AI"

urlpatterns = [
    path("TMOVINGBOT/", views.TMOVINGBOT, name="TMOVINGBOT"),
]
