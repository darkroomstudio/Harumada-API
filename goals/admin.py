from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'user', 'status', 'duration', 'start_date', 'end_date')
    list_filter = ('status', 'duration', 'created_at')
    search_fields = ('title', 'description', 'user_email', 'user_username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'message')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'duration')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )