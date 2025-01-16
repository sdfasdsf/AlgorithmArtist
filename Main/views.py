from django.shortcuts import render
from .models import Movie

def Main(request):
    latest_movies = Movie.objects.order_by('-release_date')[:5]  # 최신 영화 5개
    popular_movies = Movie.objects.filter(is_popular=True)[:5]  # 인기 영화 5개
    return render(request, 'Main/Home.html', {
        'latest_movies': latest_movies,
        'popular_movies': popular_movies,
    })
# def Main(request):
#     return render(request, 'Main.html', {})
