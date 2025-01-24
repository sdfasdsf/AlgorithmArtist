# articles/urls.py
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    # 게시글
    path("",views.ArticleList.as_view(),name="article_list"),# 게시글 목록
    path("api/", views.ArticleListAPI.as_view(), name="article_list_API"), # 게시글 목록 조회 API

    path("ArticleCreate/",views.ArticleCreate.as_view(), name="article_create"), # 게시글 생성
    path("ArticleCreate/api/",views.ArticleCreateAPI.as_view(), name="article_creat_API"), # 게시글 생성 API

    path("<int:article_pk>/",views.ArticleDetail.as_view(), name="article_detail"), # 게시판 상세 조회
    path("<int:article_pk>/api/", views.ArticleDetailAPI.as_view(), name="article_detail_API"), # 게시글 상세 조회, 좋아요 기능 API

    path("<int:article_pk>/articleedit/", views.ArticleEdit.as_view(), name="article_edit"), # 게시글 수정
    path("<int:article_pk>/articleedit/api/",views.ArticleEditAPI.as_view(), name="article_edit_API"), # 게시판 수정 API

    path("<int:article_pk>/delete/", views.ArticleDeleteAPI.as_view(), name="article_delete"),  # 게시글 삭제
    #--------------------------------------------------------------------------------------------------------------------------
    #댓글
    path("<int:article_pk>/comments/", views.CommentForm.as_view(), name="comments"), # 댓글 생성 폼
    path("<int:article_pk>/comments/api/", views.CommentCreate.as_view(), name="commentscreate"), # 댓글 생성 API
    path("<int:article_pk>/comments/<int:comment_pk>/edit/", views.CommentEdit.as_view(), name="commentsedit"), # 댓글 수정
    path("<int:article_pk>/comments/<int:comment_pk>/edit/api/", views.CommentEditAPI.as_view(), name="commentsedit_api"), # 댓글 수정 API
    path("<int:article_pk>/comments/<int:comment_pk>/delete/", views.CommentDelete.as_view(), name="comment_delete"),  # 댓글 삭제
    path("<int:article_pk>/comments/<int:comment_pk>/commentlike/", views.CommentLike.as_view(), name="commentslike"), # 댓글 좋아요 기능
]
