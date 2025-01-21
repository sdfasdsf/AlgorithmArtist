from django.urls import path
from . import views
from .views import Main, movie, movieboard, reviewboard

urlpatterns = [
    path('', Main, name="Main"),
    path('movie/', movie, name="movie"),
    path('movieboard/', movieboard, name="movieboard"),
    path('reviewboard/', reviewboard, name="reviewboard"),
]