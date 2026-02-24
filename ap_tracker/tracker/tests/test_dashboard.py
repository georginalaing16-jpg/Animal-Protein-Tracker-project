from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from tracker.models import AnimalProteinSource, ProteinIntake, DailyProteinTarget

User = get_user_model()

class DashboardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="StrongPass123!", weight_kg=70)
        self.client.login(username="u1", password="StrongPass123!")
        self.source = AnimalProteinSource.objects.create(source_name="Eggs", protein_per_100g="13.00", category="dairy")

        # Create target (auto calc 56)
        self.client.post("/api/targets/", {"target_date": "2026-02-20"}, format="json")
        ProteinIntake.objects.create(user=self.user, protein_source=self.source, protein_quantity_g="10.00", intake_date="2026-02-20")

    def test_dashboard_returns_totals(self):
        resp = self.client.get("/api/dashboard/?date=2026-02-20")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["target_grams"], "56.00")
        self.assertEqual(resp.data["total_protein_grams"], "10.00")