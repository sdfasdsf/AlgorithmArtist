# articles/urls.py
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListCreate.as_view(), name="article_list_create"), # 게시글 목록 조회 및 게시글 생성
    path("<int:article_pk>/", views.ArticleDetail.as_view(), name="article_detail"), # 게시글 수정/삭제 및 상세 조회, 좋아요 기능
    path("<int:article_pk>/comments/", views.CommentListCreate.as_view(), name="comments"), # 댓글 목록 조회 및 댓글 생성
    path("<int:article_pk>/comments/<int:comment_pk>/", views.CommentListDelete.as_view(), name="comments"), # 댓글 수정/삭제
    path("<int:article_pk>/comments/<int:comment_pk>/commentlike/", views.CommentLike.as_view(), name="commentslike"), # 댓글 좋아요 기능
]