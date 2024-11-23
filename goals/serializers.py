from rest_framework import serializers
from .models import Goal

class GoalSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Goal
        fields = ['id', 'user', 'title', 'description', 'message', 'start_date', 'end_date', 'duration', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']