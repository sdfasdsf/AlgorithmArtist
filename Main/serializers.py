# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # 프로필 정보 포함

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']
