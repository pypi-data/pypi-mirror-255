from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from omni_pro_base.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "name",
            "first_name",
            "last_name",
            "url",
            "groups",
            "is_active",
            "last_login",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class UserLoginSerializer(serializers.Serializer):
    """User login Serializer.

    Handle the login request data.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        self.context["user"] = user
        return data

    def create(self, data):
        """Generate or retrieve"""
        token, created = Token.objects.get_or_create(user=self.context["user"])
        return self.context["user"], token.key


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")
