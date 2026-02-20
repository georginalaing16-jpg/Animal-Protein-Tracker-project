# Validate input and block malicious data
from rest_framework import serializers
from .models import AnimalProteinSource, ProteinIntake
from django.contrib.auth import get_user_model
from .models import DailyProteinTarget, IntakeSummary

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
        read_only_fields = ["user", "created_at"]

        def validate_protein_quantity_grams(self, value):
            if value <= 0:
                raise serializers.ValidationError("protein_quantity_grams must be greater than 0.")
            return value

class DailyProteinTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyProteinTarget
        fields = "__all__"
        read_only_fields = ["user", "target_grams", "created_at", "calculation_method"]

class IntakeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = IntakeSummary
        fields = "__all__"
        read_only_fields = ["user"]


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "weight_kg", "created_at"]
        read_only_fields = ["id", "username", "email", "created_at"]

        def validate_weight_kg(self, value):
            if value is not None and value <= 0:
                raise serializers.ValidationError("weight_kg must be greater than 0.")
            return value