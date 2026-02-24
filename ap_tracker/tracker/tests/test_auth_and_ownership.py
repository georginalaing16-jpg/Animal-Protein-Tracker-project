from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from tracker.models import AnimalProteinSource, ProteinIntake

User = get_user_model()

class AuthOwnershipTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", email="u1@example.com", password="StrongPass123!", weight_kg=70)
        self.u2 = User.objects.create_user(username="u2", email="u2@example.com", password="StrongPass123!", weight_kg=80)
        self.source = AnimalProteinSource.objects.create(source_name="Chicken", protein_per_100g="31.00", category="meat")

    def test_unauthenticated_denied(self):
        resp = self.client.get("/api/intakes/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_others_intake(self):
        intake = ProteinIntake.objects.create(
            user=self.u2, protein_source=self.source, protein_quantity_g="20.00", intake_date="2026-02-20"
        )
        self.client.login(username="u1", password="StrongPass123!")
        resp = self.client.get(f"/api/intakes/{intake.id}/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)