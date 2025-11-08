from django.db import models
from django.utils import timezone


class JobPosting(models.Model):
    """Model to store job posting data scraped from various sources."""
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    posted_date = models.DateField()
    salary_min = models.FloatField(null=True, blank=True)
    salary_max = models.FloatField(null=True, blank=True)
    description = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    job_url = models.URLField(max_length=500, blank=True, null=True)
    
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

