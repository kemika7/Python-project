from django.contrib import admin
from .models import JobPosting, SkillTrend


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'location', 'posted_date', 'salary_min', 'salary_max', 'scraped_at')
    list_filter = ('posted_date', 'location', 'scraped_at')
    search_fields = ('job_title', 'company', 'location', 'description')
    readonly_fields = ('scraped_at',)
    date_hierarchy = 'posted_date'


@admin.register(SkillTrend)
class SkillTrendAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'role', 'frequency', 'last_updated')
    list_filter = ('role', 'last_updated')
    search_fields = ('skill_name', 'role')
    readonly_fields = ('last_updated',)
    ordering = ('-frequency',)

