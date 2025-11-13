from django.db import models
from django.utils import timezone


class JobPosting(models.Model):
    """Model to store job posting data scraped from various sources."""
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead/Principal'),
    ]
    
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    posted_date = models.DateField()
    salary_min = models.FloatField(null=True, blank=True)
    salary_max = models.FloatField(null=True, blank=True)
    description = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    job_url = models.URLField(max_length=500, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid', blank=True)
    
    class Meta:
        ordering = ['-posted_date', '-scraped_at']
        indexes = [
            models.Index(fields=['-posted_date']),
            models.Index(fields=['job_title', 'company']),
        ]
        unique_together = [['job_title', 'company', 'posted_date']]
    
    def __str__(self):
        return f"{self.job_title} at {self.company}"


class SkillTrend(models.Model):
    """Model to store skill frequency and trend data from job analysis."""
    skill_name = models.CharField(max_length=100, db_index=True)
    frequency = models.IntegerField(default=0)
    role = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-frequency', 'skill_name']
        unique_together = [['skill_name', 'role']]
        indexes = [
            models.Index(fields=['-frequency']),
            models.Index(fields=['skill_name', 'role']),
        ]
    
    def __str__(self):
        return f"{self.skill_name} ({self.frequency})"


class UserSearchHistory(models.Model):
    """Model to store user search history (last 10 searches)."""
    role = models.CharField(max_length=200)
    date_range = models.IntegerField(default=30, help_text="Number of days")
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, help_text="Session identifier for anonymous users")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'session_id']),
        ]
    
    def __str__(self):
        return f"{self.role} ({self.date_range} days) - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def save_search(cls, role, date_range, session_id=''):
        """Save a search and maintain only the last 10 searches per session."""
        # Create new search
        cls.objects.create(role=role, date_range=date_range, session_id=session_id)
        
        # Get all searches for this session, ordered by timestamp
        searches = cls.objects.filter(session_id=session_id).order_by('-timestamp')
        
        # Keep only the last 10
        if searches.count() > 10:
            # Get IDs of searches beyond the 10th
            ids_to_delete = list(searches.values_list('id', flat=True)[10:])
            # Delete the oldest searches beyond 10
            if ids_to_delete:
                cls.objects.filter(id__in=ids_to_delete).delete()

