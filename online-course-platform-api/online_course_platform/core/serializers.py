from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.db import transaction
from .models import User
from custom.models import Teacher, Student
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'role']

    @transaction.atomic()
    def create(self, validated_data):
        if validated_data['role'] == User.RoleChoices.TEACHER.value:
            user = super().create(validated_data)
            Teacher.objects.create(user_id=user.id)
        elif validated_data['role'] == User.RoleChoices.STUDENT.value:
            user = super().create(validated_data)
            Student.objects.create(user_id=user.id)
        else:
            raise serializers.ValidationError(
                {"role": f"role should be either '{User.RoleChoices.STUDENT.value}' for student or '{User.RoleChoices.TEACHER.value}' for teacher"}
            )
        return user

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

    role = serializers.CharField(read_only=True)