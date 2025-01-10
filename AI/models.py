from django.db import models
from django.conf import settings
from accounts.models import User
# Create your models here.

class AI(models.Model):
    user_question = models.CharField("질문", max_length=200)
    bot_response = models.TextField("챗봇 응답", null=True, blank=True)  # 챗봇의 응답 필드 추가
    created_at = models.DateTimeField("질문한 시간", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')  # 작성자 필드
    #session_id = models.CharField(max_length=100)  # 대화 세션 ID (모든 질문이 동일)


    def __str__(self):
        return f"{self.author.username}: {self.user_question} ({self.created_at})"