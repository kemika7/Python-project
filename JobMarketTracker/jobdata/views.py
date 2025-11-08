from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

from .models import JobPosting, SkillTrend
from .serializers import JobPostingSerializer, SkillTrendSerializer
from .analysis import analyze_skills, get_job_volume_trends, get_avg_salary_by_role


class JobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing job postings.
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'location', 'posted_date']
    search_fields = ['job_title', 'company', 'location', 'description']
    ordering_fields = ['posted_date', 'scraped_at', 'salary_min', 'salary_max']
    ordering = ['-posted_date']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent job postings (last 7 days).
        """
        days = int(request.query_params.get('days', 7))
        date_threshold = timezone.now() - timedelta(days=days)
        recent_jobs = self.queryset.filter(posted_date__gte=date_threshold.date())
        
        page = self.paginate_queryset(recent_jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recent_jobs, many=True)
        return Response(serializer.data)


class SkillTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing skill trends.
    """
    queryset = SkillTrend.objects.all()
    serializer_class = SkillTrendSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['role']
    ordering_fields = ['frequency', 'last_updated']
    ordering = ['-frequency']


class AnalyticsView(APIView):
    """
    API view for analytics endpoints.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Get analytics data based on query parameter.
        """
        analytics_type = request.query_params.get('type', 'skill-demand')
        
        if analytics_type == 'skill-demand':
            return self.get_skill_demand(request)
        elif analytics_type == 'role-volume':
            return self.get_role_volume(request)
        elif analytics_type == 'avg-salary':
            return self.get_avg_salary(request)
        else:
            return Response(
                {'error': 'Invalid analytics type. Use: skill-demand, role-volume, avg-salary'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get_skill_demand(self, request):
        """
        Get skill demand statistics.
        """
        role = request.query_params.get('role')
        top_n = int(request.query_params.get('top', 20))
        
        queryset = SkillTrend.objects.all()
        if role:
            queryset = queryset.filter(role=role)
        else:
            # Get overall skills (empty role)
            queryset = queryset.filter(role='')
        
        skills = queryset.order_by('-frequency')[:top_n]
        total_frequency = sum(skill.frequency for skill in skills) or 1
        
        skill_data = []
        for skill in skills:
            percentage = (skill.frequency / total_frequency) * 100
            skill_data.append({
                'skill_name': skill.skill_name,
                'frequency': skill.frequency,
                'percentage': round(percentage, 2),
                'role': skill.role or 'all',
            })
        
        return Response({
            'skills': skill_data,
            'total_skills': len(skill_data),
            'total_frequency': total_frequency
        })
    
    def get_role_volume(self, request):
        """
        Get job volume trends over time.
        """
        days = int(request.query_params.get('days', 30))
        role = request.query_params.get('role', '').strip()
        trends = get_job_volume_trends(days=days, role=role if role else None)
        return Response(trends)
    
    def get_avg_salary(self, request):
        """
        Get average salary by role.
        """
        role = request.query_params.get('role', '').strip()
        salary_data = get_avg_salary_by_role(role=role if role else None)
        return Response(salary_data)


# Additional API views for specific endpoints
class SkillDemandView(APIView):
    """
    Dedicated endpoint for skill demand analytics.
    """
    def get(self, request):
        role = request.query_params.get('role', '').strip()
        top_n = int(request.query_params.get('top', 20))
        
        if role:
            # If role is provided, analyze skills from jobs matching that role
            from jobdata.analysis import analyze_skills
            result = analyze_skills(role=role)
            skills_dict = result.get('skills', {})
            
            # Convert to list format
            skill_data = []
            total_frequency = sum(skills_dict.values()) or 1
            
            for skill_name, frequency in sorted(skills_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]:
                percentage = (frequency / total_frequency) * 100
                skill_data.append({
                    'skill_name': skill_name,
                    'frequency': frequency,
                    'percentage': round(percentage, 2),
                    'role': role,
                })
            
            return Response({
                'skills': skill_data,
                'total_skills': len(skill_data),
                'total_frequency': total_frequency
            })
        else:
            # No role filter - show overall skills
            queryset = SkillTrend.objects.filter(role='')
            skills = queryset.order_by('-frequency')[:top_n]
            total_frequency = sum(skill.frequency for skill in skills) or 1
            
            skill_data = []
            for skill in skills:
                percentage = (skill.frequency / total_frequency) * 100
                skill_data.append({
                    'skill_name': skill.skill_name,
                    'frequency': skill.frequency,
                    'percentage': round(percentage, 2),
                    'role': 'all',
                })
            
            return Response({
                'skills': skill_data,
                'total_skills': len(skill_data),
                'total_frequency': total_frequency
            })


class RoleVolumeView(APIView):
    """
    Dedicated endpoint for role volume trends.
    """
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        role = request.query_params.get('role', '').strip()
        trends = get_job_volume_trends(days=days, role=role if role else None)
        return Response(trends)


class AvgSalaryView(APIView):
    """
    Dedicated endpoint for average salary analytics.
    """
    def get(self, request):
        role = request.query_params.get('role', '').strip()
        salary_data = get_avg_salary_by_role(role=role if role else None)
        return Response(salary_data)

