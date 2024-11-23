from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalSharingViewSet

router = DefaultRouter()
router.register(r'', GoalSharingViewSet, basename='goal-sharing')

urlpatterns = [
    path('', include(router.urls)),
]