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
    path("login/", views.login.as_view(), name="login"),
    path("logout/", views.logout.as_view(), name="logout"),
    path("profile/", views.profile.as_view(), name="profile"),  # 회원정보 조회 및 수정
    path("profile/passwordchange/", views.passwordchange.as_view(), name="passwordchange"),  # 비밀번호 변경
    path("<int:user_pk>/follow/", views.follow.as_view(), name="follow"),  # 팔로우/언팔로우 토글
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]
