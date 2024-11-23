from django.contrib import admin
from .models import GoalSharing

@admin.register(GoalSharing)
class GoalSharingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'goal_title',
        'shared_by_username', 
        'shared_to_username',
        'status',
        'invitation_code',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'goal__title',
        'shared_by_user__username',
        'shared_to_user__username',
        'invitation_code'
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def goal_title(self, obj):
        return obj.goal.title
    goal_title.short_description = 'Goal'

    def shared_by_username(self, obj):
        return obj.shared_by_user.username
    shared_by_username.short_description = 'Shared By'

    def shared_to_username(self, obj):
        if obj.shared_to_user:
            return obj.shared_to_user.username
        return 'Pending'  # or 'Not claimed yet' or '-'
    shared_to_username.short_description = 'Shared To'

    fieldsets = (
        ('Goal Information', {
            'fields': ('goal',)
        }),
        ('Users', {
            'fields': ('shared_by_user', 'shared_to_user')
        }),
        ('Invitation Details', {
            'fields': ('invitation_code', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
