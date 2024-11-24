from django.contrib import admin
from .models import Goal, GoalAttendance

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'user',
        'duration',
        'start_date',
        'status',
        'current_stage',
        'progress_percentage',
        'attendance_count',
        'created_at'
    )
    
    list_filter = (
        'duration',
        'status',
        'current_stage',
        'created_at'
    )
    
    search_fields = (
        'title',
        'description',
        'user__username'
    )
    
    readonly_fields = (
        'current_stage',
        'next_stage',
        'progress_percentage',
        'created_at',
        'updated_at'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'message')
        }),
        ('Duration Settings', {
            'fields': ('duration', 'start_date')
        }),
        ('Progress Information', {
            'fields': (
                'current_stage',
                'next_stage',
                'progress_percentage',
                'attendance_count'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(GoalAttendance)
class GoalAttendanceAdmin(admin.ModelAdmin):
    list_display = ('goal', 'user', 'date', 'created_at')
    list_filter = ('date', 'user')
    search_fields = ('goal__title', 'user__username')
    date_hierarchy = 'date'