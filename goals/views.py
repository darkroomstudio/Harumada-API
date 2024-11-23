from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from .models import Goal
from .serializers import GoalSerializer
from goal_sharing.models import GoalSharing

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        invitation_code = request.data.get('invitation_code')
        invitation_response = request.data.get('response')  # 'accept' or 'reject'
        
        if invitation_code:
            try:
                # First, check if the code exists at all
                sharing = GoalSharing.objects.filter(
                    invitation_code=invitation_code
                ).first()

                if not sharing:
                    return Response({
                        'error': 'Invalid invitation code'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Check if this is user's own invitation code
                if sharing.shared_by_user == request.user:
                    return Response({
                        'error': 'You cannot use your own invitation code'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Check if the code has already been used
                if sharing.status != 'pending':
                    return Response({
                        'error': 'This invitation code has already been used'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # If no response provided, return goal details for preview
                if not invitation_response:
                    original_goal = sharing.goal
                    return Response({
                        'message': 'Please accept or reject this goal invitation',
                        'goal_preview': {
                            'title': original_goal.title,
                            'description': original_goal.description,
                            'message': original_goal.message,
                            'start_date': original_goal.start_date,
                            'end_date': original_goal.end_date,
                            'duration': original_goal.duration,
                            'shared_by': sharing.shared_by_user.username
                        }
                    })

                # Handle rejection
                if invitation_response == 'reject':
                    sharing.shared_to_user = request.user
                    sharing.status = 'rejected'
                    sharing.save()
                    return Response({
                        'message': 'Goal invitation rejected successfully'
                    })

                # Handle acceptance
                if invitation_response == 'accept':
                    original_goal = sharing.goal
                    
                    # Create new goal with original goal's data
                    serializer = self.get_serializer(data={
                        'title': original_goal.title,
                        'description': original_goal.description,
                        'message': original_goal.message,
                        'start_date': original_goal.start_date,
                        'end_date': original_goal.end_date,
                        'duration': original_goal.duration,
                        'status': 'pending'
                    })
                    
                    if serializer.is_valid():
                        # Save the new goal
                        goal = serializer.save(user=request.user)
                        
                        # Update sharing with accepting user and status
                        sharing.shared_to_user = request.user
                        sharing.status = 'accepted'
                        sharing.save()
                        
                        # Update num_goal_partner for both users
                        sharing.shared_by_user.num_goal_partner += 1
                        request.user.num_goal_partner += 1
                        sharing.shared_by_user.save()
                        request.user.save()
                        
                        return Response({
                            'message': 'Goal invitation accepted and created successfully',
                            'goal': serializer.data
                        }, status=status.HTTP_201_CREATED)
                    
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    'error': 'Invalid response. Must be "accept" or "reject"'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'error': f'Error processing invitation code: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            # Regular goal creation
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Goal successfully deleted"},
            status=status.HTTP_200_OK
        )