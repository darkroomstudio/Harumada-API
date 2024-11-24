from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, datetime

User = get_user_model()

class Goal(models.Model):
    DURATION_CHOICES = [
        ('week', '1 Week'),
        ('month', '1 Month'),
        ('3months', '3 Months'),
        ('6months', '6 Months'),
        ('12months', '12 Months'),
        ('unlimited', 'Unlimited'),
    ]

    BOAT_STAGES = [
        ('boat1', 'Boat1'),
        ('boat2', 'Boat2'),
        ('boat3', 'Boat3'),
        ('boat4', 'Boat4'),
        ('boat5', 'Boat5'),
        ('boat6', 'Boat6')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)
    start_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Progress fields
    current_stage = models.CharField(
        max_length=10,
        choices=BOAT_STAGES,
        default='boat1'
    )
    next_stage = models.CharField(
        max_length=10,
        choices=BOAT_STAGES,
        default='boat2'
    )
    progress_percentage = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    attendance_count = models.IntegerField(default=0)
    
    # Add attendance fields
    attendance_dates = models.JSONField(default=dict)  # Stores dates and users who attended
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original values to check for changes
        self._original_status = self.status if hasattr(self, 'status') else None

    def is_dirty(self):
        """Check if the model has unsaved changes"""
        return self.status != self._original_status

    def get_duration_days(self):
        """Convert duration choice to number of days"""
        duration_mapping = {
            'week': 7,
            'month': 30,
            '3months': 90,
            '6months': 180,
            '12months': 365,
            'unlimited': None
        }
        return duration_mapping.get(self.duration)

    def determine_stages(self, progress):
        """Determine current and next boat stages based on progress percentage"""
        if progress < 20:
            return 'boat1', 'boat2'
        elif progress < 40:
            return 'boat2', 'boat3'
        elif progress < 60:
            return 'boat3', 'boat4'
        elif progress < 80:
            return 'boat4', 'boat5'
        elif progress < 100:
            return 'boat5', 'boat6'
        else:
            return 'boat6', 'boat6'

    def get_end_date(self):
        """Calculate end date based on duration"""
        if self.duration == 'unlimited':
            return None
            
        duration_days = self.get_duration_days()
        if duration_days is None:
            return None
            
        return self.start_date + timedelta(days=duration_days)

    @property
    def end_date(self):
        """Property to access end_date easily"""
        return self.get_end_date()

    def update_status(self):
        """Update status based on dates"""
        today = timezone.now().date()
        
        # Convert start_date to date object if it isn't already
        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        
        # Debug prints
        print(f"Today: {today} (type: {type(today)})")
        print(f"Start date: {self.start_date} (type: {type(self.start_date)})")
        print(f"Duration: {self.duration}")
        print(f"Current status: {self.status}")
        
        # If goal hasn't started yet
        if today < self.start_date:
            print("Goal hasn't started yet")
            self.status = 'pending'
            return
            
        # If goal has unlimited duration
        if self.duration == 'unlimited':
            print("Unlimited duration goal")
            if today >= self.start_date:
                self.status = 'in_progress'
            return
            
        # Calculate end date
        end_date = self.get_end_date()
        print(f"End date: {end_date}")
        
        # Update status based on dates
        if today >= end_date:
            print("Goal is done")
            self.status = 'done'
        elif today >= self.start_date:
            print("Goal is in progress")
            self.status = 'in_progress'
        else:
            print("Goal is pending")
            self.status = 'pending'
        
        print(f"New status: {self.status}")

    def calculate_progress(self):
        """Calculate progress based on duration and elapsed time"""
        now = timezone.now().date()
        
        # If goal hasn't started yet
        if now < self.start_date:
            self.current_stage = 'boat1'
            self.next_stage = 'boat2'
            return 0

        # If goal is done
        if self.status == 'done':
            self.current_stage = 'boat6'
            self.next_stage = 'boat6'
            return 100

        # Handle unlimited duration
        if self.duration == 'unlimited':
            target_attendance = 30
            progress = min(100, (self.attendance_count / target_attendance) * 100)
            self.current_stage, self.next_stage = self.determine_stages(progress)
            return round(progress)

        # Calculate regular progress
        duration_days = self.get_duration_days()
        elapsed_days = (now - self.start_date).days
        progress = min(100, max(0, (elapsed_days / duration_days) * 100))
        progress = round(progress)
        self.current_stage, self.next_stage = self.determine_stages(progress)
        return progress

    def progress_to_next_stage(self):
        """Calculate how much progress is needed to reach next stage"""
        if self.current_stage == 'boat6':
            return 0
        stage_thresholds = {
            'boat1': 20,
            'boat2': 40,
            'boat3': 60,
            'boat4': 80,
            'boat5': 100,
            'boat6': 100
        }
        threshold = stage_thresholds.get(self.current_stage)
        return threshold - self.progress_percentage

    def get_original_goal(self):
        """Get the original goal if this is a shared goal"""
        # If this is the original goal, return self
        if not hasattr(self, 'shared_from'):
            return self
            
        # If this is a shared goal, return the original
        sharing = self.shared_from.first()  # Get the sharing record
        if sharing:
            return sharing.goal
        return self

    def mark_attendance(self, user):
        """Mark attendance for today"""
        today = timezone.now().date().isoformat()
        
        # Get original goal
        original_goal = self.get_original_goal()
        
        # Initialize attendance_dates if empty
        if not original_goal.attendance_dates:
            original_goal.attendance_dates = {}
        
        # Verify user has permission
        if user != original_goal.user:
            sharing = original_goal.shares.filter(
                shared_to_user=user,
                status='accepted'
            ).first()
            if not sharing:
                raise PermissionError("You don't have permission to mark attendance for this goal")

        # Check if user already marked attendance today
        today_attendees = original_goal.attendance_dates.get(today, [])
        if user.username in today_attendees:
            return False, original_goal.get_today_attendance_status()

        # Mark attendance
        today_attendees.append(user.username)
        original_goal.attendance_dates[today] = today_attendees
        original_goal.attendance_count += 1
        original_goal.save()

        return True, original_goal.get_today_attendance_status()

    def get_today_attendance_status(self):
        """Get attendance status for today"""
        original_goal = self.get_original_goal()
        today = timezone.now().date().isoformat()
        today_attendees = original_goal.attendance_dates.get(today, [])
        
        # Get goal sharing if exists
        sharing = original_goal.shares.filter(status='accepted').first()
        
        if sharing:
            # This is a shared goal
            user_a_attended = original_goal.user.username in today_attendees
            user_b_attended = sharing.shared_to_user.username in today_attendees
            
            if user_a_attended and user_b_attended:
                return "completed"
            elif user_a_attended or user_b_attended:
                return "one_person_done"
            return "zero_person_done"
        else:
            # Single user goal
            return "completed" if original_goal.user.username in today_attendees else "zero_person_done"

    def get_attendance_history(self):
        """Get formatted attendance history"""
        original_goal = self.get_original_goal()
        return original_goal.attendance_dates

    def save(self, *args, **kwargs):
        # Update status before saving
        self.update_status()
        
        # Update progress percentage and boat stages
        self.progress_percentage = self.calculate_progress()
        
        # Save the model
        super().save(*args, **kwargs)
        
        # Update original values after save
        self._original_status = self.status

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.progress_percentage}%"

class GoalAttendance(models.Model):
    goal = models.ForeignKey(
        Goal, 
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['goal', 'user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.goal.title} - {self.user.username} - {self.date}"