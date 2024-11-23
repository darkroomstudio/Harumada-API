from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import GoalSharing
from .serializers import GoalSharingSerializer
from goals.models import Goal
import uuid

class GoalSharingViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSharingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return GoalSharing.objects.filter(
            Q(shared_by_user=self.request.user) | 
            Q(shared_to_user=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        goal_id = request.data.get('goal')
        
        # Validate goal ownership
        try:
            goal = Goal.objects.get(id=goal_id, user=request.user)
        except Goal.DoesNotExist:
            return Response({
                'error': 'Goal not found or does not belong to you'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Generate invitation code
        invitation_code = str(uuid.uuid4())[:8].upper()
        
        # Create the sharing directly
        sharing = GoalSharing.objects.create(
            goal=goal,
            shared_by_user=request.user,
            invitation_code=invitation_code,
            status='pending'
        )
        
        serializer = self.get_serializer(sharing)
        
        return Response({
            'message': 'Goal sharing invitation created',
            'invitation_code': invitation_code,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)