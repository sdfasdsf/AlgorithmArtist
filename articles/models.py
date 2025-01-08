# articles/models.py

from django.db import models
from accounts.models import User
from django.conf import settings

class Article(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )
    title = models.CharField("제목", max_length=200)
    content = models.TextField("내용")
    image = models.ImageField("영화 이미지", upload_to="images/", blank=True, null=True)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
    rating = models.IntegerField("평점", choices=[(i, str(i)) for i in range(1, 6)])
    writer = models.ForeignKey(
        User,  # 커스텀 User 모델 사용
        on_delete=models.CASCADE,    # User가 삭제될 때 게시글도 삭제
        null=True
    )
    article_like = models.ManyToManyField('accounts.User', related_name='liked_articles' ,blank=True) # 게시글 좋아요 필드 추가

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    writer = models.ForeignKey(
        User,  # 커스텀 User 모델 사용
        on_delete=models.CASCADE,    # User가 삭제될 때 게시글도 삭제
        null=True
    )
    comment_like = models.ManyToManyField('accounts.User', related_name='liked_comments' ,blank=True) # 댓글 좋아요 필드 추가

    def __str__(self):
        return f"{self.author} - {self.content}"
