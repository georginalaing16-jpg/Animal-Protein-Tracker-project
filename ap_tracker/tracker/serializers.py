# Validate input and block malicious data
from rest_framework import serializers
from .models import AnimalProteinSource, ProteinIntake
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "weight_kg", "created_at"]
        read_only_fields = ["id", "created_at"]

class AnimalProteinSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalProteinSource
        fields = "__all__"

class ProteinIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProteinIntake
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

