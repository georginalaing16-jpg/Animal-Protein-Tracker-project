from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from .models import AnimalProteinSource, ProteinIntake, DailyProteinTarget, IntakeSummary
from .serializers import AnimalProteinSourceSerializer, ProteinIntakeSerializer, DailyProteinTargetSerializer, IntakeSummarySerializer
from .permissions import IsOwner
from decimal import Decimal
from rest_framework.exceptions import ValidationError

from datetime import date as date_class
from django.utils.dateparse import parse_date
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ProteinIntakeViewSet(viewsets.ModelViewSet):

    """CRUD operations for (Protein_Intake). User can only view and modify their own activities."""

    serializer_class = ProteinIntakeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Users can only see their own protein intake records
        return ProteinIntake.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer): # Owner is always set to logged-in user
        serializer.save(user=self.request.user)

    def get_queryset(self):
        qs = ProteinIntake.objects.filter(user=self.request.user)

        date_str = self.request.query_params.get("date")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")

        if date_str:
            d = parse_date(date_str)
            if not d:
                raise ValidationError({"date": "Invalid format. Use YYYY-MM-DD."})
            qs = qs.filter(intake_date=d)

        if start and end:
            s = parse_date(start)
            e = parse_date(end)
            if not s or not e:
                raise ValidationError({"range": "Invalid date format. Use YYYY-MM-DD."})
            if s > e:
                raise ValidationError({"range": "start must be <= end."})
            qs = qs.filter(intake_date__range=(s, e))

        return qs


class AnimalProteinSourceViewSet(viewsets.ModelViewSet):
    queryset = AnimalProteinSource.objects.all()
    serializer_class = AnimalProteinSourceSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class DailyProteinTargetViewSet(viewsets.ModelViewSet):
    serializer_class = DailyProteinTargetSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return DailyProteinTarget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        # Ensure user has weight
        if user.weight_kg is None:
            raise ValidationError({"weight_kg": "Set your weight first (PATCH /api/me/) to calculate target."})

        # Formula: weight * 0.8
        target = Decimal(str(user.weight_kg)) * Decimal("0.8")

        serializer.save(
            user=user,
            target_grams=target,
            calculation_method="weight * 0.8"
        )


class IntakeSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = IntakeSummarySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return IntakeSummary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """
        POST /api/summaries/generate/?date=YYYY-MM-DD

        Creates or updates a daily intake summary for the authenticated user.
        """
        raw_date = request.query_params.get("date")
        if not raw_date:
            return Response(
                {"detail": "Missing required query parameter: date (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        summary_date = parse_date(raw_date)
        if not summary_date:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Sum protein intake for the day
        total = (
            ProteinIntake.objects
            .filter(user=request.user, intake_date=summary_date)
            .aggregate(total=Sum("protein_quantity_grams"))
            .get("total")
        ) or 0

        # 2) Fetch daily target for the day
        try:
            target = DailyProteinTarget.objects.get(user=request.user, target_date=summary_date)
        except DailyProteinTarget.DoesNotExist:
            return Response(
                {"detail": "No daily protein target found for this date."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3) Upsert summary row (idempotent)
        summary_obj, _created = IntakeSummary.objects.update_or_create(
            user=request.user,
            summary_date=summary_date,
            defaults={
                "total_protein_grams": total,
                "target_protein_grams": target.target_grams,
            }
        )

        serializer = self.get_serializer(summary_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import MeSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    