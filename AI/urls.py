from django.urls import path
from . import views

app_name = "AI"

urlpatterns = [
    path("TMOVINGBOT/", views.AIanswer.as_view(), name="TMOVINGBOT"),
]