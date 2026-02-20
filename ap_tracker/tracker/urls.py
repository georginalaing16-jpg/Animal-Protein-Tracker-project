"""
URL configuration for ap_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import MeView
from rest_framework.routers import DefaultRouter
from  .views import ProteinIntakeViewSet, AnimalProteinSourceViewSet, DailyProteinTargetViewSet, IntakeSummaryViewSet


urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
]

router = DefaultRouter()
router.register(r"intakes", ProteinIntakeViewSet, basename="intakes")
router.register(r"sources", AnimalProteinSourceViewSet, basename="sources")
router.register(r"targets", DailyProteinTargetViewSet, basename="targets")
router.register(r"summaries", IntakeSummaryViewSet, basename="summaries")

urlpatterns = router.urls



