from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import AI
from .serializers import AIService
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

class AIanswer(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(AI)

    def post(self, request):
        """응답 생성"""
        serializer = AIRequestSerializer(data=request.data)
        if serializer.is_valid():
            # 질문 저장
            ai_instance = serializer.save()
            user_question = ai_instance.user_question
            answer = generate_response_with_setup(user_question)
            # 생성된 응답 저장
            ai_instance.response = answer
            ai_instance.save()
            
            return Response(serializer.data)
    








