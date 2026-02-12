from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AnimalProteinSource, ProteinIntake
from .serializers import AnimalProteinSourceSerializer, ProteinIntakeSerializer
from .permissions import IsOwner

class ProteinIntakeViewset(viewsets.ModelViewSet):

    """CRUD operations for (Protein_Intake). User can only view and modify their own activities."""

    serializer_class = ProteinIntakeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Users can only see their own protein intake records
        return ProteinIntake.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer): # Owner is always set to logged-in user
        serializer.save(user=self.request.user)


class AnimalProteinSourceViewset(viewsets.ModelViewSet):
    
    """CRUD operations for catalog (Animal_Protein_Source). All users can view and modify the same list of protein sources."""

    queryset = AnimalProteinSource.objects.all()
    serializer_class = AnimalProteinSourceSerializer
    permission_classes = [IsAuthenticated]


