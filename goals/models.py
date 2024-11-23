from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Goal(models.Model):
    DURATION_CHOICES = [
        ('week', 'Week'),
        ('month', 'Month'),
        ('3months', '3 Months'),
        ('6months', '6 Months'),
        ('12months', '12 Months'),
        ('unlimited', 'Unlimited'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title