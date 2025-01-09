from django.urls import path, include
from . import views
from .views import TMOVINGBOT_response

app_name = "AI"

urlpatterns = [
    path("TMOVINGBOT/", views.TMOVINGBOT_response, name="TMOVINGBOT_response"),
]
