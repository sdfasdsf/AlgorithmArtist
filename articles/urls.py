from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListCreate.as_view(), name="article_list_create"),
    path("<int:article_pk>/", views.ArticleDetail.as_view(), name="article_detail"),
    path(
        "<int:article_pk>/comments/", views.CommentListCreate.as_view(), name="comments"
    ),
]
