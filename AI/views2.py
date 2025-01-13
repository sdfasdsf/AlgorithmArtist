from django.shortcuts import render
from django.http import JsonResponse
#
#From .serializers2 import AIService
from .models import Movie
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def TMOVINGBOT(request):
    user_message = request.GET.get('message', '').loweeo

    # AIService 클래스 인스턴스 생성
  # ai_service = AIService(user_question=user_message, api_key="your-openai-api-key")

    # 영화 정보 가져오기
    movie_info = ai_service.get_movie_info()

    if movie_info:
        return JsonResponse({
            "response": f"제가 추천하는 영화는 '{movie_info.get('title')}'입니다. 장르는 {movie_info.get('genre')}이고, {movie_info.get('description')}"
        })
    else:
        return JsonResponse({
            "response": "도움을 원하시면 '추천' 또는 '감독'이라고 입력해보세요."
        })

    
#views 보이는 거니까 serializer ai 서비스 질문 결과값 가져오는 걸로 하고 데이터 베이스 클라이언트  인증  account