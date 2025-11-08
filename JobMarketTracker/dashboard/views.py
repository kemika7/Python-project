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
    context = {
        'total_jobs': JobPosting.objects.count(),
        'recent_jobs': JobPosting.objects.filter(
            posted_date__gte=(timezone.now() - timedelta(days=7)).date()
        ).count(),
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

