# articles/urls.py
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    # 게시글
    path("",views.ArticleList.as_view(),name="article_list"),
    path("api/", views.ArticleListAPI.as_view(), name="article_list_API"), # 게시글 목록 조회 API
    path("ArticleCreate/",views.ArticleCreate.as_view(), name="article_create"), # 게시글 생성
    path("<int:article_pk>/", views.ArticleDetail.as_view(), name="article_detail"), # 게시글 상세 조회, 좋아요 기능
    path("<int:article_pk>/articleedit/", views.ArticleDetail.as_view(), name="article_edit"), # 게시글 수정
    path("<int:article_pk>/delete/", views.ArticleDelete.as_view(), name="article_delete"),  # 게시글 삭제

    #댓글
    path("<int:article_pk>/comments/", views.CommentCreate.as_view(), name="comments"), # 댓글 생성
    path("<int:article_pk>/comments/<int:comment_pk>/edit/", views.CommentEdit.as_view(), name="comments"), # 댓글 수정
    path("<int:article_pk>/comments/<int:comment_pk>/delete/", views.CommentDelete.as_view(), name="comment_delete"),  # 댓글 삭제
    path("<int:article_pk>/comments/<int:comment_pk>/commentlike/", views.CommentLike.as_view(), name="commentslike"), # 댓글 좋아요 기능
]