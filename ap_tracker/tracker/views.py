from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS, AllowAny
from .models import AnimalProteinSource, ProteinIntake, DailyProteinTarget, IntakeSummary
from .serializers import AnimalProteinSourceSerializer, ProteinIntakeSerializer, DailyProteinTargetSerializer, IntakeSummarySerializer
from .permissions import IsOwner
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from .services import upsert_intake_summary_for_user_date

from datetime import date as date_class
from django.utils.dateparse import parse_date
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from .serializers import MeSerializer, RegisterSerializer

class ProteinIntakeViewSet(viewsets.ModelViewSet):

    """CRUD operations for (Protein_Intake). User can only view and modify their own activities."""

    serializer_class = ProteinIntakeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Users can only see their own protein intake records
        return ProteinIntake.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer): # Owner is always set to logged-in user
        obj = serializer.save(user=self.request.user)
        # Automatically update or create the IntakeSummary for the intake_date
        upsert_intake_summary_for_user_date(user=self.request.user, day=obj.intake_date)
  
    def perform_update(self, serializer):
        old_obj = self.get_object()
        old_date = old_obj.intake_date
    
        obj = serializer.save()

        # If intake_date changed, update summaries for both old and new dates
        upsert_intake_summary_for_user_date(user=self.request.user, day=old_date)
        upsert_intake_summary_for_user_date(user=self.request.user, day=obj.intake_date)
 
    def perform_destroy(self, instance):
        day = instance.intake_date
        instance.delete()
        upsert_intake_summary_for_user_date(user=self.request.user, day=day)

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
            .aggregate(total=Sum("protein_quantity_g"))
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

    @action(detail=False, methods=["post"], url_path="generate-range")
    def generate_range(self, request):
        start_raw = request.query_params.get("start")
        end_raw = request.query_params.get("end")

        if not start_raw or not end_raw:
            return Response(
                {"detail": "Missing required query parameters: start and end (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start = parse_date(start_raw)
        end = parse_date(end_raw)
        if not start or not end:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if start > end:
            return Response(
                {"detail": "start must be <= end."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Loop day-by-day
        current = start
        updated = 0
        skipped_no_target = 0

        from datetime import timedelta
        while current <= end:
            summary_obj, _created = upsert_intake_summary_for_user_date(user=request.user, day=current)
            if summary_obj is None:
                skipped_no_target += 1
            else:
                updated += 1
            current += timedelta(days=1)

        return Response(
            {"updated": updated, "skipped_no_target": skipped_no_target},
            status=status.HTTP_200_OK
        )



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
    


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_raw = request.query_params.get("date")
        if date_raw:
            day = parse_date(date_raw)
            if not day:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            from datetime import date as date_class
            day = date_class.today()

        # Try to use summary if available (fast)
        summary = IntakeSummary.objects.filter(user=request.user, summary_date=day).first()

        # Target
        target_obj = DailyProteinTarget.objects.filter(user=request.user, target_date=day).first()
        target_grams = str(target_obj.target_grams) if target_obj else None

        # Total
        if summary:
            total = summary.total_protein_grams
        else:
            total = (
                ProteinIntake.objects.filter(user=request.user, intake_date=day)
                .aggregate(total=Sum("protein_quantity_g"))
                .get("total")
            ) or 0

        remaining = None
        if target_obj:
            remaining = target_obj.target_grams - total

        intakes = ProteinIntake.objects.filter(user=request.user, intake_date=day).order_by("-created_at")
        intakes_data = ProteinIntakeSerializer(intakes, many=True).data

        def fmt2(value):
            return format(Decimal(value), ".2f")
        return Response(
            {
                "date": str(day),
                "target_grams": target_grams,
                "total_protein_grams": fmt2(total),
                "remaining_grams": fmt2(remaining) if remaining is not None else None,
                "intakes": intakes_data,
            },
            status=status.HTTP_200_OK
        )
    

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "username": user.username, "email": user.email},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)