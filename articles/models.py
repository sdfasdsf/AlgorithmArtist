# articles/models.py

from django.db import models
from accounts.models import User
from django.conf import settings

class Article(models.Model):
    """게시글 모델"""
    ACTION = 'AC'
    DRAMA = 'DR'
    COMEDY = 'CO'
    ADVENTURE = "AD"
    ANIMATION = "AM"
    CRIME = "CM"
    DOCUMENTARY= "DM"
    FANTASY = "FT"
    HORROR = "HO"
    MUSICAL = "MC"
    SF = "SF"
    ROMANCE = "RM"
    MYSTERY = "MS"
    SPORTS = "SP"
    HRILLER = "HR"
    WAR = "WAR"
    GENRE_CHOICES = [
        (ACTION, 'Action'),
        (DRAMA, 'Drama'),
        (COMEDY, 'Comedy'),
        (ADVENTURE, "Adventure"),
        (ANIMATION, "Animation"),
        (CRIME,"Crime"),
        (DOCUMENTARY,"Documentary"),
        (FANTASY , "Fantasy"),
        (HORROR, "Horror"),
        (MUSICAL, "Musical"),
        (SF, "SF"),
        (ROMANCE, "Romance"),
        (MYSTERY, "Mystery"),
        (SPORTS, "Sports"),
        (HRILLER, "Hriller"),
        (WAR, "War"),
    ]

    # 게시글 작성자 (User 모델과 연결, 작성자가 삭제되면 게시글도 삭제)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )
    Article_title = models.CharField("게시글 제목", max_length=200)  # 게시글 제목
    movie_title = models.CharField("영화 제목", max_length=200)  # 영화 제목
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default=ACTION)  # 영화 장르
    content = models.TextField("내용")  # 게시글 내용
    image = models.ImageField("영화 이미지", upload_to="images/", blank=True, null=True) # 영화 이미지 (선택적)
    created_at = models.DateTimeField("작성일", auto_now_add=True)  # 게시글 작성 날짜
    updated_at = models.DateTimeField("수정일", auto_now=True)  # 게시글 수정 날짜
    rating = models.IntegerField("평점", choices=[(i, str(i)) for i in range(1, 6)]) # 평점 (1~5 사이의 값)
    views = models.IntegerField("조회수", default=0) # 게시글 조회수
    article_like = models.ManyToManyField('accounts.User', related_name='liked_articles' ,blank=True) # 좋아요를 누른 사용자 목록
    total_likes_count = models.IntegerField("좋아요 수", default=0) # 총 좋아요 수
    

    def __str__(self):
        return self.Article_title


class Comment(models.Model):
    """댓글 모델"""

    # 댓글이 작성된 게시글 (Article 모델과 연결)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    # 댓글 작성자 (User 모델과 연결, 작성자가 삭제되면 댓글도 삭제)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("내용")  # 댓글 내용
    created_at = models.DateTimeField("작성일", auto_now_add=True)  # 댓글 작성 날짜
    updated_at = models.DateTimeField("수정일", auto_now=True)  # 댓글 수정 날짜

    comment_like = models.ManyToManyField('accounts.User', related_name='liked_comments' ,blank=True) # 좋아요를 누른 사용자 목록
    total_commentlikes_count = models.IntegerField("좋아요 수", default=0) # 총 좋아요 수

    def __str__(self):
        return f"{self.author} - {self.content}" # 객체 문자열 표현: 작성자와 댓글 내용
