from django.shortcuts import render
from django.http import JsonResponse
from jobdata.models import JobPosting, SkillTrend
from jobdata.analysis import get_job_volume_trends, get_avg_salary_by_role
from datetime import timedelta
from django.utils import timezone


def index(request):
    """
    Render the main dashboard page.
    """
    # Get all jobs count
    total_jobs = JobPosting.objects.count()
    
    # Get recent jobs (last 7 days) - extend to 365 days if no recent jobs
    date_threshold = timezone.now() - timedelta(days=7)
    recent_jobs = JobPosting.objects.filter(
        posted_date__gte=date_threshold.date()
    ).count()
    
    # If no recent jobs, count all jobs in last 365 days
    if recent_jobs == 0:
        date_threshold = timezone.now() - timedelta(days=365)
        recent_jobs = JobPosting.objects.filter(
            posted_date__gte=date_threshold.date()
        ).count()
    
    context = {
        'total_jobs': total_jobs,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'dashboard/index.html', context)


def api_data(request):
    """
    API endpoint to fetch dashboard data.
    """
    data = {
        'job_volume': get_job_volume_trends(days=30),
        'top_skills': list(
            SkillTrend.objects.filter(role='')
            .order_by('-frequency')[:10]
            .values('skill_name', 'frequency')
        ),
        'avg_salary': get_avg_salary_by_role(),
    }
    return JsonResponse(data)

