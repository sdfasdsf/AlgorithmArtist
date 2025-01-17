from django.urls import path
from . import views
from views import Main, movie, movieboard, reviewboard

urlpatterns = [
    path('', views.Main, name="Main"),
    path('movie/', views.movie, name="movie"),
    path('movieboard/', views.movieboard, name="movieboard"),
    path('reviewboard/', views.reviewboard, name="reviewboard"),
]