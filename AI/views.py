from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from .models import AI
from .serializers import AIService 
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
import json

def TMOVINGBOT(request):
    user_message = request.GET.get('message', '').lower()

class AI_service_view(APIView):
    """AI 서비스 호출"""
    def post(self, request):
        serializer = AIService(data=request.data)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author=request.user_question)
            ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
