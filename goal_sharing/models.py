from django.db import models
from django.contrib.auth import get_user_model
from goals.models import Goal

User = get_user_model()

class GoalSharing(models.Model):
    SHARING_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_goals'
    )
    shared_to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_shared_goals',
        null=True,
        blank=True
    )
    invitation_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=10,
        choices=SHARING_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['goal', 'shared_to_user']

    def save(self, *args, **kwargs):
        if not self.invitation_code:
            self.invitation_code = self.generate_invitation_code()
        super().save(*args, **kwargs)

    def generate_invitation_code(self):
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not GoalSharing.objects.filter(invitation_code=code).exists():
                return code

    def __str__(self):
        return f"Goal {self.goal.title} shared by {self.shared_by_user.username}"