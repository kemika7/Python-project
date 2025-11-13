from rest_framework import serializers
from .models import JobPosting, SkillTrend, UserSearchHistory


class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'


class SkillTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillTrend
        fields = '__all__'


class UserSearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSearchHistory
        fields = ['id', 'role', 'date_range', 'timestamp']
        read_only_fields = ['timestamp']
