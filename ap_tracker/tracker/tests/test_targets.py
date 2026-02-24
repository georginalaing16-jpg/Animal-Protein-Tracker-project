from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class TargetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="StrongPass123!", weight_kg=70)
        self.client.login(username="u1", password="StrongPass123!")

    def test_target_auto_calculates_weight_times_point8(self):
        resp = self.client.post("/api/targets/", {"target_date": "2026-02-20"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # 70 * 0.8 = 56
        self.assertEqual(resp.data["target_grams"], "56.00")