from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie, AI
from django.views.decorators.csrf import csrf_exempt
import json

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

# @csrf_exempt  # CSRF 비활성화 (테스트용, 실제 운영에서는 주의 필요)
def chat_view(request):
    if request.method == 'POST':
        try:
            # 요청 데이터 파싱
            body = json.loads(request.body)
            user_input = body.get('user_input', '')

            # 챗봇 응답 생성
            bot_response = bot_response(user_input)

            # 데이터 저장
            chat_log = AI.objects.create(user_input=user_input, bot_response=bot_response)

            # 응답 반환
            return JsonResponse({
                'status': 'success',
                'user_input': user_input,
                'bot_response': bot_response,
                'log_id': chat_log.id
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
