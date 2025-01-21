# articles/serializers.py
from rest_framework import serializers
from .models import Article
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회 및 생성 및 수정 Serializer"""

    # 댓글 작성자의 이메일을 출력하기 위한 필드 (읽기 전용)
    author = serializers.ReadOnlyField(source="author.email")
    

    class Meta:
        model = Comment
        fields = (
            "id",  # 댓글 ID
            "article",  # 댓글이 작성된 게시글 ID
            "author",  # 댓글 작성자 이메일
            "content",  # 댓글 내용
            "created_at",  # 댓글 작성 날짜
            "updated_at",  # 댓글 수정 날짜
            "total_commentlikes_count",  # 댓글 좋아요 수
        )
        read_only_fields = ("article", "like_users") # 읽기 전용 필드 지정

class ArticleListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회 Serializer"""
    class Meta:
        model = Article
        fields = (
            "id",  # 게시글 ID
            "author",  # 게시글 작성자 ID
            "Article_title",  # 게시글 제목
            "movie_title",  # 영화 제목
            "created_at",  # 게시글 작성 날짜
            "image",  # 게시글에 첨부된 영화 이미지
            "rating",  # 영화 평점
        )
        read_only_fields = ("author",) # 게시글 작성자는 읽기 전용


class ArticleDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 조회 및 수정 및 생성 Serializer"""

    # 댓글 목록을 포함하기 위한 필드
    comments = CommentSerializer(many=True, read_only=True)
    
    # 게시글 작성자의 이메일 출력 (읽기 전용)
    author = serializers.ReadOnlyField(
        source="author.email"
    )  # author 필드에 작성자의 이메일만 출력
    image = serializers.ImageField() # 이미지 필드

    class Meta:
        model = Article
        fields = (
            "id",  # 게시글 ID
            "author",  # 게시글 작성자 이메일
            "Article_title",  # 게시글 제목
            "movie_title",  # 영화 제목
            "content",  # 게시글 내용
            "image",  # 게시글 이미지
            "created_at",  # 게시글 작성 날짜
            "updated_at",  # 게시글 수정 날짜
            "rating",  # 영화 평점
            "comments",  # 게시글에 달린 댓글 목록
            "views",  # 게시글 조회수
            "total_likes_count",  # 게시글 총 좋아요 수
            "genre" # 영화 장르
        )

    def get_image(self, obj):
        """이미지의 절대 경로를 생성해 반환"""
        request = self.context.get("request")  # Serializer context에서 request 가져오기
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    



