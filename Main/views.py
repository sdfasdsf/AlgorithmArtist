import os
from django.shortcuts import render
from .models import Movie

def Main(request):
    latest_movies = Movie.objects.order_by('-release_date')[:5]  # 최신 영화 5개
    popular_movies = Movie.objects.filter(is_popular=True)[:5]  # 인기 영화 5개
    return render(request, 'Home.html', {})
# def Main(request):
#     return render(request, 'Main.html', {})

def movie(request):
    return render(request, 'movie.html')

def movieboard(request):
    return render(request, 'movieboard.html')

def reviewboard(request):
    return render(request, 'reviewboard.html')