from rest_framework import serializers
from .models import Goal, GoalAttendance
from django.utils import timezone

class GoalAttendanceSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GoalAttendance
        fields = ['id', 'goal', 'user', 'username', 'date', 'created_at']
        read_only_fields = ['created_at']

class GoalSerializer(serializers.ModelSerializer):
    current_stage_display = serializers.CharField(source='get_current_stage_display', read_only=True)
    next_stage_display = serializers.CharField(source='get_next_stage_display', read_only=True)
    today_attendance_status = serializers.CharField(source='get_today_attendance_status', read_only=True)
    today_attendees = serializers.SerializerMethodField()
    shared_with = serializers.SerializerMethodField()
    original_goal_id = serializers.SerializerMethodField()
    current_boat_image = serializers.SerializerMethodField()
    next_boat_image = serializers.SerializerMethodField()
    progress_to_next = serializers.IntegerField(source='progress_to_next_stage', read_only=True)
    end_date = serializers.SerializerMethodField()
    day_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            'id', 
            'user', 
            'title', 
            'description', 
            'message',
            'duration', 
            'start_date', 
            'end_date',
            'status',
            'current_stage', 
            'current_stage_display',
            'current_boat_image',
            'next_stage', 
            'next_stage_display',
            'next_boat_image',
            'progress_percentage',
            'progress_to_next',
            'attendance_count', 
            'today_attendance_status', 
            'today_attendees',
            'shared_with', 
            'original_goal_id',
            'created_at', 
            'updated_at',
            'day_count',
        ]
        read_only_fields = [
            'user', 
            'end_date', 
            'status', 
            'current_stage', 
            'next_stage',
            'progress_percentage', 
            'attendance_count',
            'created_at', 
            'updated_at'
        ]

    def get_current_boat_image(self, obj):
        return f'/static/images/boats/{obj.current_stage}.png'

    def get_next_boat_image(self, obj):
        return f'/static/images/boats/{obj.next_stage}.png'

    def get_today_attendees(self, obj):
        original_goal = obj.get_original_goal()
        today = timezone.now().date().isoformat()
        return original_goal.attendance_dates.get(today, [])

    def get_shared_with(self, obj):
        original_goal = obj.get_original_goal()
        sharing = original_goal.shares.filter(status='accepted').first()
        if sharing:
            return {
                'user_id': sharing.shared_to_user.id,
                'username': sharing.shared_to_user.username
            }
        return None

    def get_original_goal_id(self, obj):
        original_goal = obj.get_original_goal()
        return original_goal.id

    def get_end_date(self, obj):
        """Get the calculated end date"""
        return obj.get_end_date()

    def get_day_count(self, obj):
        return obj.get_day_count()