import os
from django.shortcuts import render
from rest_framework.views import APIView
from .models import Movie
import requests
from django.http import JsonResponse
from dotenv import dotenv_values

MOVIEDATA_API_KEY = dotenv_values(".env")

def Main(request):
        latest_movies = Movie.objects.order_by('-release_date')[:5]  # 최신 영화 5개
        popular_movies = Movie.objects.filter(is_popular=True)[:5]  # 인기 영화 5개
        return render(request, 'Home.html', {})

def fetch_movies(request):
    # API 호출 로직
        url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
        headers = {
        "accept": "application/json",
        "Authorization": "https://api.themoviedb.org/3/trending/movie/day?language=ko-KR" 
        }
        response = requests.get(url)
        if response.status_code == 200:
        # JSON 응답을 파싱
            data = response.json()
        movies = data.get('results', [])  # 영화 목록 추출
        return render(request, "Home.html", {"movies": movies})
        # else:
        # return JsonResponse({"error": "Failed to fetch movies"}, status=response.status_code)

def home(request):
    """영화 데이터를 템플릿으로 전달"""
    latest_movies = fetch_movies('')  # 최근 영화 목록
    popular_movies = fetch_movies('')    # 인기 영화 목록

    context = {
        'latest_movies': latest_movies,
        'popular_movies': popular_movies,
    }
    return render(request, 'Home.html', context)


def movie(request):
    return render(request, 'movie.html')

def movieboard(request):
    return render(request, 'movieboard.html')

def reviewboard(request):
    return render(request, 'reviewboard.html')
