from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import User


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
class User(AbstractUser):
    email = models.EmailField('이메일', unique=True)
    username = models.CharField('닉네임', max_length=150)  # unique=True 제거
    profile_image = models.ImageField('프로필 이미지', upload_to='profile_images/', blank=True, null=True)
    
    # ManyToManyField로 팔로우 기능 구현
    followings = models.ManyToManyField(
        'self',  # 자기 자신과의 관계
        symmetrical=False,  # 대칭 관계가 아님 (단방향)
        related_name='followers',  # 역참조 이름
        through='Follow',  # 중간 테이블
        blank=True
    )

    # 새로운 필드 추가 부분_____________________________
    #_____________________________________________________________선이다
    gender = models.CharField(  # 성별 추가
        '성별',
        max_length=10,
        choices=[('male', '남성'), ('female', '여성'), ('other', '기타')],
        blank=True, null=True  # 선택 사항
    )
    
    ssn = models.CharField(  # 주민등록번호 추가
        '주민등록번호',
        max_length=13,  # 주민등록번호는 13자리
        unique=True,  # 주민등록번호는 고유해야 함
        blank=True, null=True  # 선택 사항
    )

    phone_number = models.CharField(  # 전화번호 추가
        '전화번호',
        max_length=15,  # 전화번호의 최대 길이
        unique=True,  # 전화번호는 고유해야 함
        blank=True, null=True  # 선택 사항
    )
#__________________________________________________________추가한부분 
    USERNAME_FIELD = 'email'    # 로그인 시 이메일 사용
    REQUIRED_FIELDS = []        # email은 자동으로 필수

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
    
    class Post(models.Model):
        title = models.CharField(max_length=40)
        contents = models.TextField()
        create_date = models.DateTimeField(auto_now_add=True)
        writer = models.ForeignKey(User, on_delete=models.CASCADE)
        like = models.ManyToManyField(User, related_name='likes', blank=True)

        def __str__(self):
            return 'id : {}, title : {}'.format(self.id, self.title, self.contents)