# articles/serializers.py
from rest_framework import serializers
from .models import Article
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회 및 생성 및 수정 Serializer"""

    author = serializers.ReadOnlyField(source="author.email")
    

    class Meta:
        model = Comment
        fields = (
            "id",
            "article",
            "author",
            "content",
            "created_at",
            "updated_at",
            
        )
        read_only_fields = ("article", "like_users")

class ArticleListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회 Serializer"""
    class Meta:
        model = Article
        fields = (
            "id",
            "author",
            "Article_title",
            "movie_title",
            "created_at",
            "image",
            "rating"
        )
        read_only_fields = ("author",)


class ArticleDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 조회 및 수정 및 생성 Serializer"""
    comments = CommentSerializer(many=True, read_only=True)

    author = serializers.ReadOnlyField(
        source="author.email"
    )  # author 필드에 작성자의 이메일만 출력
    image = serializers.ImageField()

    class Meta:
        model = Article
        fields = (
            "id",
            "author",
            "Article_title",
            "movie_title",
            "content",
            "image",
            "created_at",
            "updated_at",
            "rating",
            "comments",
            "views",
        )

    def get_image(self, obj):
        request = self.context.get("request")  # Serializer context에서 request 가져오기
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    



