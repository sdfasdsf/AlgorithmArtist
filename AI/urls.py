from django.urls import path
from . import views

app_name = "AI"

urlpatterns = [
    path("TMOVINGBOT/", views.AIanswerbot.as_view(), name="TMOVINGBOT"), # 챗봇 페이지
    path("TMOVINGBOT/api/", views.AIanswer.as_view(), name="TMOVINGBOTresponse"), # 챗봇 응답
]
