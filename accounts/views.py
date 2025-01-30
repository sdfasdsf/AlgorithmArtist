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
from django.contrib.auth import authenticate, logout, get_user_model, login as auth_login, update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.template.response import TemplateResponse

from django.contrib.auth.hashers import check_password

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.throttling import AnonRateThrottle
import logging
import traceback
# 추가한 내용 _________________
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
                # serializer.save()에서 user 객체가 반환되어야 합니다.
                user = serializer.save()

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


class Login(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/login.html'
    throttle_classes = [AnonRateThrottle]  # Rate limiting 적용

    def get(self, request):
        """로그인 페이지 표시"""
        return Response({'message': '로그인 페이지입니다.'})

    def post(self, request):
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

            # 로그인 상태 유지
            login(request, user)

            # 쿠키에 토큰 저장
            response = TemplateResponse(
                request, 'Main/home.html', {'user': request.user})
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True)
            return response

        else:
            return JsonResponse(
                {"error": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=400
            )

class CheckLoginStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        로그인 여부 확인 API
        - 로그인된 사용자: 상태 200과 사용자 정보 반환
        - 로그인되지 않은 사용자: 상태 401 반환
        """
        if request.user.is_authenticated:
            return Response({"message": "로그인 상태입니다.", "user": request.user.username}, status=200)
        return Response({"error": "로그인이 필요합니다."}, status=401)

class Logout(APIView):
    # 로그인 사용자만 로그아웃 가능
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        try:
            # refresh token을 가져옵니다.
            refresh_token = request.COOKIES.get("refresh_token")

            # refresh token을 사용하여 토큰을 블랙리스트 처리
            token = RefreshToken(refresh_token)
            token.blacklist()  # 토큰을 블랙리스트에 추가하여 더 이상 사용할 수 없도록 처리

            logout(request)

            response = redirect('/')
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response

        except Exception as e:
            return Response({"error": "로그아웃 실패", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class profile(APIView):

    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/profile.html'

    def get(self, request):
        """프로필 폼 표시"""
        user = request.user  # 현재 로그인한 사용자
        serializer = UserProfileSerializer(user, context={'request': request})

        access_token = request.COOKIES.get('access_token', None)
        
        # 템플릿에 필요한 데이터 전달
        context = {
            'profile_data': serializer.data,  # 프로필 정보

            'access_token': access_token,   # 토큰도 템플릿에 전달
        }

        return Response(context)


class profileedit(APIView):
    # 로그인 사용자만 정보 조회 및 수정 가능
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/profileedit.html'  # 프로필 템플릿

    def get(self, request):
        """프로필 수정 페이지 렌더링"""
        return Response({'message': '프로필 수정 페이지입니다.'})
    

class ProfileEditAPI(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        """프로필 데이터 반환 (JSON 형식)"""
        user = request.user
        serializer = UserUpdateSerializer(user)
        return Response(serializer.data)  # ✅ JSON 데이터 반환

    def patch(self, request):
        """프로필 수정 처리"""
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)  # ✅ 수정된 데이터 JSON 반환

        return Response(serializer.errors, status=400)

class passwordchange(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'accounts/passwordchange.html'  # 프로필 템플릿

    def get(self, request):
        """비밀번호 변경 페이지 렌더링"""
        return Response()

    def post(self, request):
        """비밀번호 변경 처리"""
        current_password = request.data.get('current_password')
        new_password = request.data.get('password')
        new_password_confirm = request.data.get('password_confirm')

        # 현재 비밀번호 확인
        if not check_password(current_password, request.user.password):
            return JsonResponse({'error': '현재 비밀번호가 올바르지 않습니다.'}, status=400)

        # 새 비밀번호 확인
        if new_password != new_password_confirm:
            return JsonResponse({'error': '새 비밀번호가 일치하지 않습니다.'}, status=400)


        # 비밀번호 유효성 검사
        serializer = passwordchangeSerializer(instance=request.user, data={'password': new_password}) 
        if serializer.is_valid():
            # 비밀번호 변경
            serializer.save()

            # 세션 업데이트 (로그인 유지)
            update_session_auth_hash(request, request.user)  # 세션 업데이트
            
            return redirect('accounts:profile')  # 프로필 페이지로 리디렉션

        return Response({'error': '비밀번호 변경에 실패했습니다.'}, status=400)


class follow(APIView):
    def post(self, request, user_pk):
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
