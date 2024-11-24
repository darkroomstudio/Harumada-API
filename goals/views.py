from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from .models import Goal
from .serializers import GoalSerializer
from goal_sharing.models import GoalSharing
from rest_framework.decorators import action
from django.db.models import Q

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """Get goals that user owns or has shared access to"""
        user = self.request.user
        return Goal.objects.filter(
            Q(user=user) |
            Q(shares__shared_to_user=user, shares__status='accepted')
        ).distinct()

    def perform_create(self, serializer):
        """Automatically set the user when creating a goal"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to prevent duplicate shared goals"""
        # If this is a shared goal join request, redirect to join_shared_goal
        if 'invitation_code' in request.data:
            return self.join_shared_goal(request)
            
        # Normal goal creation
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Goal successfully deleted"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def increment_attendance(self, request, pk=None):
        """Increment attendance count for a goal"""
        goal = self.get_object()
        goal.attendance_count += 1
        goal.save()  # This will recalculate progress
        serializer = self.get_serializer(goal)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_all_statuses(self, request):
        """Force update status for all goals"""
        goals = self.get_queryset()
        updated = []
        
        for goal in goals:
            old_status = goal.status
            goal.update_status()
            if old_status != goal.status:
                goal.save()
                updated.append({
                    'id': goal.id,
                    'title': goal.title,
                    'old_status': old_status,
                    'new_status': goal.status
                })
        
        return Response({
            'message': f'Updated {len(updated)} goals',
            'updated_goals': updated
        })

    def retrieve(self, request, *args, **kwargs):
        """Get single goal with updated status"""
        instance = self.get_object()
        instance.update_status()
        if instance.is_dirty():  # Now this will work
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        """Mark attendance for today"""
        goal = self.get_object()
        original_goal = goal.get_original_goal()
        
        try:
            created, status = original_goal.mark_attendance(request.user)
            return Response({
                'message': 'Attendance marked successfully' if created else 'Already marked attendance for today',
                'attendance_status': status,
                'created': created,
                'original_goal_id': original_goal.id
            })
        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        """Get attendance history"""
        goal = self.get_object()
        original_goal = goal.get_original_goal()
        return Response({
            'original_goal_id': original_goal.id,
            'history': original_goal.get_attendance_history()
        })

    @action(detail=False, methods=['post'])
    def join_shared_goal(self, request):
        """Join a shared goal using invitation code"""
        invitation_code = request.data.get('invitation_code')
        
        try:
            # Find the sharing invitation
            sharing = GoalSharing.objects.get(
                invitation_code=invitation_code,
                status='pending'
            )
            
            # Get the original goal
            original_goal = sharing.goal
            
            # Check if user is already part of this goal
            if original_goal.user == request.user or \
               original_goal.shares.filter(shared_to_user=request.user).exists():
                return Response(
                    {'error': 'You are already part of this goal'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update sharing status to accepted
            sharing.status = 'accepted'
            sharing.shared_to_user = request.user
            sharing.save()
            
            # Return the original goal data
            serializer = self.get_serializer(original_goal)
            
            return Response({
                'message': 'Successfully joined the shared goal',
                'goal': serializer.data,
                'is_shared': True,
                'original_goal_id': original_goal.id
            })
            
        except GoalSharing.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired invitation code'},
                status=status.HTTP_400_BAD_REQUEST
            )