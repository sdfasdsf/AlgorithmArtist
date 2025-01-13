from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import AI
from .serializers import AIRequestSerializer
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
import json


class AIList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """AI 대화 목록 조회"""
        AIes = AI.objects.all()
        serializer = AIRequestSerializer(
            AI, many=True
        )  # 목록용 Serializer 사용
        return Response(serializer.data)

class AIDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, AI_pk):
        return get_object_or_404(AI, pk=AI_pk)

    def get(self, request, AI_pk):
        """목록 상세 조회"""
        AI_find = self.get_object(AI_pk)
        serializer = AIDetail(AI_find)  # 상세 Serializer 사용
        return Response(serializer.data)

def TMOVINGBOT(request):
    user_message = request.GET.get('message', '').lower()




# class AI_service_view(APIView):
#     """AI 서비스 호출"""
#     def post(self, request):
#         serializer = AIService(data=request.data)  # 상세 Serializer 사용
#         if serializer.is_valid():
#             serializer.save(author=request.user_question)
#             ai_instance = AI.objects.create(user_question=self.prompt)  # 질문을 저장
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # @csrf_exempt  # CSRF 비활성화 (테스트용, 실제 운영에서는 주의 필요)
# def chat_view(request):
#     if request.method == 'POST':
#         try:
#             # 요청 데이터 파싱
#             body = json.loads(request.body)
#             user_input = body.get('user_input', '')

#             # 챗봇 응답 생성
#             bot_response = bot_response(user_input)

#             # 데이터 저장
#             chat_log = AI.objects.create(user_input=user_input, bot_response=bot_response)

#             # 응답 반환
#             return JsonResponse({
#                 'status': 'success',
#                 'user_input': user_input,
#                 'bot_response': bot_response,
#                 'log_id': chat_log.id
#             })

#         except json.JSONDecodeError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

