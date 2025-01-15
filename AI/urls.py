from django.urls import path
from . import views

app_name = "AI"

urlpatterns = [
    path("TMOVINGBOT/", views.TMOVINGBOT, name="TMOVINGBOT"),
]