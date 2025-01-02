from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField("이메일", unique=True)
    username = models.CharField("닉네임", max_length=150, unique=True)
    profile_image = models.ImageField(
        "프로필 이미지", upload_to="profile_images/", blank=True, null=True
    )
    name = models.CharField("이름", max_length=30)  # 이름 필드 추가
    birthdate = models.DateField("생일", blank=True, null=True)  # 생일 필드 추가
    gender = models.CharField(
        "성별",
        max_length=10,
        choices=[("male", "남성"), ("female", "여성"), ("other", "기타")],
        blank=True,
    )  # 성별 필드 추가
    introduction = models.TextField("자기소개", blank=True)

    # ManyToManyField로 팔로우 기능 구현
    followings = models.ManyToManyField(
        "self",  # 자기 자신과의 관계
        symmetrical=False,  # 대칭 관계가 아님 (단방향)
        related_name="followers",  # 역참조 이름
        through="Follow",  # 중간 테이블
    )

    USERNAME_FIELD = "email"  # 로그인 시 이메일 사용
    REQUIRED_FIELDS = ["username", "name"]  # email은 자동으로 필수

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# 중간 테이블을 명시적으로 정의
class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="followed_users", on_delete=models.CASCADE
    )  # 팔로우를 하는 사용자
    following = models.ForeignKey(
        User, related_name="following_users", on_delete=models.CASCADE
    )  # 팔로우받는 사용자
    created_at = models.DateTimeField(auto_now_add=True)  # 팔로우한 시간

    class Meta:
        unique_together = ("follower", "following")  # 중복 팔로우 방지

    def __str__(self):
        return f"{self.follower} follows {self.following}"