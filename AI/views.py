from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import AI
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
import json
from .serializers import AIRequestSerializer
from .AIanswer import generate_response_with_setup

# class AIList(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def get(self, request):
#         """AI 대화 목록 조회"""
#         articles = AI.objects.all()
#         serializer = AIListSerializer(
#             AI, many=True
#         )  # 목록용 Serializer 사용
#         return Response(serializer.data)

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import AI
from .serializers import AIRequestSerializer
from .AIanswer import generate_response_with_setup  


class AIanswer(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(AI)

    def post(self, request):
        """응답 생성"""
        # 사용자 질문을 기반으로 챗봇 응답을 생성합니다.
        serializer = AIRequestSerializer(data=request.data)
        if serializer.is_valid():
            #질문 DB 저장
            ai_instance = serializer.save(author=request.user)  # 자동으로 처리되는 부분

            user_question = ai_instance.user_question
            # 답변 생성 (여기서는 함수 호출로 처리하는 부분)
            answer = generate_response_with_setup(user_question)

            ai_instance.bot_response = answer
            ai_instance.save()

            return Response(serializer.data)









