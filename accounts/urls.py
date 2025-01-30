# accounts/urls.py

from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup.as_view(), name="signup"),
    path("signout/", views.signout.as_view(), name="signout"),
    path("login/", views.Login.as_view(), name="login"),
    path("checklogin/", views.CheckLoginStatus.as_view(), name="checklogin"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("profile/", views.profile.as_view(), name="profile"),  # 회원정보 조회 및 수정
    path("profileedit/", views.profileedit.as_view(), name="profileedit"),  # 프로필 수정 페이지
    path("profileedit/api/", views.ProfileEditAPI.as_view(), name="profileedit_api"),  # 프로필 수정 API
    path("profile/passwordchange/", views.passwordchange.as_view(), name="passwordchange"),  # 비밀번호 변경
    path("<int:user_pk>/follow/", views.follow.as_view(), name="follow"),  # 팔로우/언팔로우 토글
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]
