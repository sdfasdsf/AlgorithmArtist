# accounts/views.py
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import SignupSerializer, UserUpdateSerializer, UserProfileSerializer, passwordchangeSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, logout, get_user_model ,login as auth_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly



from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.throttling import AnonRateThrottle
import logging 
import traceback
#추가한 내용 _________________
User = get_user_model()
logger = logging.getLogger(__name__)

class signup(APIView):
    permission_classes = [AllowAny]  # 인증이 필요하지 않음
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/signup.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용
    def get(self, request):
        """회원가입 폼 표시"""
        return Response({'message': '회원가입 페이지입니다.'})
    def post(self, request):
        """
        회원가입 처리
        - 데이터 유효성 검사
        - 에러 처리
        - 회원가입 성공/실패 처리
        """
        try:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                # 수정된 코드 위치
                user = serializer.save()  # serializer.save()에서 user 객체가 반환되어야 합니다.
                if not user:
                    raise ValueError('사용자 생성에 실패했습니다.')  # 사용자 생성 실패 시 예외 처리
                # 성공 메시지 및 리다이렉션
                messages.success(request, '회원가입이 완료되었습니다.')
                response = redirect('Main')
                return response
            # 유효성 검사 실패 시 에러 메시지 표시
            return Response({
                'message': '회원가입 페이지입니다.',
                'errors': serializer.errors
            }, status=400)
        except Exception as e:
            # 예외 발생 시 로깅 및 에러 메시지
            error_message = traceback.format_exc()  # 예외의 스택 트레이스를 문자열로 가져옴
            logger.error(f"회원가입 중 오류 발생: {error_message}")  # 오류 메시지 로깅
            messages.error(request, '회원가입 처리 중 오류가 발생했습니다.')
            return Response({
                'message': '회원가입 페이지입니다.',
                'errors': {'server': ['서버 오류가 발생했습니다.']}
            }, status=500)


class signout(APIView):
    # 로그인 사용자에게는 삭제 권한까지 부여
    permission_classes = [IsAuthenticatedOrReadOnly]
    def delete(self, request):
        user = request.user

        # 사용자 삭제
        user.delete()

        return Response({
            "message": "회원탈퇴가 되었습니다."
    }, status=status.HTTP_204_NO_CONTENT)


class login(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/login.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self, request):
        """로그인 페이지 표시"""
        return Response({'message': '로그인 페이지입니다.'})

    def post(self,request):
        """
        로그인 처리
        - 인증
        - 에러 처리
        - 로그인 성공/실패 처리
        """
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 이메일 값 확인
        if not email:
            return JsonResponse({"error": "이메일을 입력해 주세요."}, status=400)
        
        # 비밀번호 값 확인
        if not password:
            return JsonResponse({"error": "비밀번호를 입력해 주세요."}, status=400)

        # 사용자 인증
        user = authenticate(request, email=email, password=password)

        # 인증 성공 시
        if user is not None:
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # 쿠키에 토큰 저장
            response = redirect('Main')  # 'main'은 리다이렉트할 URL 패턴 이름
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True)

            return response
        
        else:
            return JsonResponse(
                {"error": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=400
            )

class logout(APIView):
    # 로그인 사용자만 로그아웃 가능
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self,request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃 성공"})
        except Exception:
            return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)

class profile(APIView):
    # 로그인 사용자만 정보 조회 및 수정 가능
    permission_classes = [IsAuthenticated]
    def get(self, request):

        user = request.user  # JWT 인증을 통해 얻은 현재 사용자

        serializer = UserProfileSerializer(user, context={"request": request})
            
        return Response(serializer.data, status=200)

    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(
            instance=user, data=request.data, partial=True
        )  # partial=True로 일부 업데이트 허용

        if serializer.is_valid():
            serializer.save()  # 수정 내용 저장
            return Response(
                {
                    "message": "회원정보가 성공적으로 수정되었습니다.",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class passwordchange(APIView):
    def put(self,request):
        user = request.user  # JWT 인증을 통해 얻은 현재 사용자

        serializer = passwordchangeSerializer(
                instance=user, data=request.data, partial=True
            )  # partial=True로 일부 업데이트 허용
        if serializer.is_valid():
                serializer.save()  # 수정 내용 저장
                return Response(
                    {
                        "message": "비밀번호가 성공적으로 수정되었습니다.",
                        "user": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class follow(APIView):
    def post(self,request, user_pk):
        profile_user = get_object_or_404(User, pk=user_pk)
        me = request.user

        if me == profile_user:
            return Response(
                {"error": "자기 자신을 팔로우할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if me.followings.filter(pk=profile_user.pk).exists():
            me.followings.remove(profile_user)
            is_followed = False
            message = f"{profile_user.email}님 팔로우를 취소했습니다."
        else:
            me.followings.add(profile_user)
            is_followed = True
            message = f"{profile_user.email}님을 팔로우했습니다."

        return Response(
            {
                "is_followed": is_followed,
                "message": message,
            },
            status=status.HTTP_200_OK,
        )