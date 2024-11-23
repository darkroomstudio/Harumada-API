from rest_framework import serializers
from .models import GoalSharing
from goals.serializers import GoalSerializer

class GoalSharingSerializer(serializers.ModelSerializer):
    goal_details = GoalSerializer(source='goal', read_only=True)
    shared_by_username = serializers.CharField(source='shared_by_user.username', read_only=True)
    shared_to_username = serializers.CharField(source='shared_to_user.username', read_only=True)

    class Meta:
        model = GoalSharing
        fields = [
            'id', 'goal', 'goal_details', 'shared_by_user', 'shared_by_username', 'shared_to_user', 'shared_to_username', 'invitation_code', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shared_by_user', 'invitation_code', 'created_at', 'updated_at']
        extra_kwargs = {
            'shared_to_user': {'required': False}
        }