from django.urls import path
from . import views
from .views import Main, movie

urlpatterns = [
    path('', Main, name="Main"),
    path('movie/', movie, name="movie"),
]