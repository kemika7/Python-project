from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPostingViewSet,
    SkillTrendViewSet,
    SkillDemandView,
    RoleVolumeView,
    AvgSalaryView,
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
]

