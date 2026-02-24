from django.db.models import Sum
from .models import ProteinIntake, DailyProteinTarget, IntakeSummary

def upsert_intake_summary_for_user_date(*, user, day):
    """
    Recalculate and upsert the IntakeSummary for (user, day).
    Returns (summary_obj or None, created_bool or None).

    If no DailyProteinTarget exists for that day, returns (None, None).
    """
    total = (
        ProteinIntake.objects
        .filter(user=user, intake_date=day)
        .aggregate(total=Sum("protein_quantity_g"))
        .get("total")
    ) or 0

    try:
        target = DailyProteinTarget.objects.get(user=user, target_date=day)
    except DailyProteinTarget.DoesNotExist:
        return None, None

    summary_obj, created = IntakeSummary.objects.update_or_create(
        user=user,
        summary_date=day,
        defaults={
            "total_protein_grams": total,
            "target_protein_grams": target.target_grams,
        },
    )
    return summary_obj, created