# my_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSerializer

# 메인 페이지
class MainPageView(APIView):
    def get(self, request):
        if request.user.is_authenticated:  # 로그인된 상태
            # 로그인된 사용자의 정보를 포함한 메인 페이지 응답
            return Response({
                "message": f"Welcome to the main page, {request.user.username}!",
                "profile_info": {
                    "username": request.user.username,
                    "email": request.user.email,
                    "profile_image": request.user.profile_image.url if request.user.profile_image else None,
                },
                "profile_url": reverse('accounts:profile'),  # 프로필 URL
                "logout_url": reverse('accounts:logout'),  # 로그아웃 URL
            })
        else:  # 비로그인 상태
            return Response({
                "message": "Welcome to the main page, please log in to see more.",
                "login_url": reverse('accounts:login')  # 로그인 페이지 URL
            })

# 프로필 정보 API
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def get(self, request):
        user_data = UserSerializer(request.user).data  # 로그인된 사용자 정보 반환
        return Response(user_data)
