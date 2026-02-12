from django.contrib.auth.models import AbstractUser
from django.db import models

# Create custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


from django.conf import settings

class AnimalProteinSource(models.Model):
    source_name = models.CharField(max_length=255, unique=True)
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source_name
    
class ProteinIntake(models.Model):
    # Activity belongs to a user(one-to-many relationship)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="protein_intake")
    protein_source = models.ForeignKey(AnimalProteinSource, on_delete=models.CASCADE, related_name="protein_intake")
    protein_quantity_g = models.DecimalField(max_digits=5, decimal_places=2)
    intake_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


