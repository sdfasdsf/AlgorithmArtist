from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie

def TMOVINGBOT(request):
    user_message = request.GET.get('message', '').lower()

    # 영화 추천 로직
    if "최신" or "인기" or "추천" in user_message:
        movie = Movie.objects.order_by('?').first() # 랜덤 영화
        return JsonResponse({
            "response": f"제가 추천하는 영화는 '{movie.title}'입니다. 장르는 {movie.genre}이고, {movie.description}"
        })
    elif "감독" in user_message:
        director = user_message.split()[-1]
        movies = Movie.objects.filter(director__icontains=director)
        response = ", ".join([movie.title for movie in movies]) or "해당 감독의 영화를 찾을 수 없습니다."
        return JsonResponse({"response": response})
    else:
        return JsonResponse({"response": "도움을 원하시면 '추천' 또는 '감독'이라고 입력해보세요."})