from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPostingViewSet,
    SkillTrendViewSet,
    SkillDemandView,
    RoleVolumeView,
    AvgSalaryView,
    CompanyDistributionView,
    LocationDistributionView,
    ExperienceLevelView,
    SalaryDistributionView,
    SkillCorrelationView,
)

router = DefaultRouter()
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'skills', SkillTrendViewSet, basename='skilltrend')

urlpatterns = [
    path('', include(router.urls)),
    path('jobs/recent/', JobPostingViewSet.as_view({'get': 'recent'}), name='jobs-recent'),
    path('analytics/skill-demand/', SkillDemandView.as_view(), name='skill-demand'),
    path('analytics/role-volume/', RoleVolumeView.as_view(), name='role-volume'),
    path('analytics/avg-salary/', AvgSalaryView.as_view(), name='avg-salary'),
    path('analytics/company-distribution/', CompanyDistributionView.as_view(), name='company-distribution'),
    path('analytics/location-distribution/', LocationDistributionView.as_view(), name='location-distribution'),
    path('analytics/experience-level/', ExperienceLevelView.as_view(), name='experience-level'),
    path('analytics/salary-distribution/', SalaryDistributionView.as_view(), name='salary-distribution'),
    path('analytics/skill-correlation/', SkillCorrelationView.as_view(), name='skill-correlation'),
]

