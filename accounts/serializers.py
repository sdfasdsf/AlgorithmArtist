# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Follow
from articles.models import Article, Comment


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "username",
            "profile_image",
            "gender",
            "ssn",
            "phone_number",
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password2")  # password2 제거
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):

    class FollowSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "profile_image",)

    followers = FollowSerializer(many=True, read_only=True)
    followings = FollowSerializer(many=True, read_only=True)
    follower_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(
        source="followings.count", read_only=True
    )
    # 추가된 필드 ___________________________________________________________________
    class article_likeSerializer(serializers.ModelSerializer): # 좋아요 한 게시글 정보
        author_username = serializers.CharField(source='author.username', read_only=True)  # 작성자의 username을 가져옴
        class Meta:
            model = Article
            fields = ("Article_title", "movie_title","image", "rating", "author_username")
    
    Favorite_articles = article_likeSerializer(
        many=True, 
        read_only=True, 
        source="liked_articles"  # User 모델의 'liked_articles'를 참조
    )
    Favorite_articles_count = serializers.IntegerField(
        source="liked_articles.count", read_only=True  # 개수 필드도 source 수정
    )
    class comment_likeSerializer(serializers.ModelSerializer): # 좋아요 한 게시글 정보
        Article_title = serializers.CharField(source='article.Article_title', read_only=True)  # Article의 title을 가져옴
        author_username = serializers.CharField(source='author.username', read_only=True)  # 작성자의 username을 가져옴

        class Meta:
            model = Comment
            fields = ("content", "created_at", "Article_title","author_username")
    Favorite_comments = comment_likeSerializer(
        many=True, 
        read_only=True, 
        source="liked_comments"  # User 모델의 'liked_comments'를 참조
    )
    Favorite_comments_count = serializers.IntegerField(
        source="liked_comments.count", read_only=True  # 개수 필드도 source 수정
    )
    #_____________________________________________________________________
    profile_image = serializers.SerializerMethodField()  # 커스텀 필드로 처리

    # 추가된 필드 ___________________________________________________________________
    gender = serializers.CharField(source='get_gender_display', read_only=True)  # 성별 추가
    ssn = serializers.CharField(read_only=True)  # 주민등록번호 추가
    phone_number = serializers.CharField(read_only=True)  # 전화번호 추가
    #_____________________________________________________________________


    
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "profile_image",
            "followings",
            "followers",
            "follower_count",
            "following_count",
            "profile_image",
            "gender",        # 성별 필드 추가
            "ssn",           # 주민등록번호 필드 추가
            "phone_number",  # 전화번호 필드 추가
            "Favorite_articles", # 좋아요 한 게시글 정보
            "Favorite_articles_count", # 좋아요 한 게시글 수
            "Favorite_comments", # 좋아요한 댓글 정보
            "Favorite_comments_count" # 좋아요 한 댓글 수
        ]  # 반환할 필드

    def get_profile_image(self, obj):
        request = self.context.get("request")  # Serializer context에서 request 가져오기
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
    


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "profile_image")  # 수정 가능한 필드

class passwordchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["password"]  # 수정 가능한 필드
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])  # 비밀번호 해시화
        instance.save()
        return instance

