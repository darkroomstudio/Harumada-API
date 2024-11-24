from django.core.management.base import BaseCommand
from django.utils import timezone
from goals.models import Goal

class Command(BaseCommand):
    help = 'Update goal statuses based on dates'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Update pending to in_progress
        pending_updated = Goal.objects.filter(
            start_date__lte=today,
            status='pending'
        ).update(status='in_progress')
        
        # Update in_progress to done
        done_updated = 0
        in_progress_goals = Goal.objects.filter(status='in_progress')
        
        for goal in in_progress_goals:
            if goal.duration != 'unlimited':
                end_date = goal.get_end_date()
                if today >= end_date:
                    goal.status = 'done'
                    goal.save()
                    done_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {pending_updated} goals to in_progress and '
                f'{done_updated} goals to done'
            )
        )