# main/urls.py
from django.urls import path, include
from .views import MainPageView

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),  # 메인 페이지
    path('accounts/', include('accounts.urls', namespace='user_accounts')),  # namespace 수정
]
