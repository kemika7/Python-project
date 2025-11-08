from rest_framework import serializers
from .models import JobPosting, SkillTrend


class JobPostingSerializer(serializers.ModelSerializer):
    """Serializer for JobPosting model."""
    
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ('scraped_at',)


class SkillTrendSerializer(serializers.ModelSerializer):
    """Serializer for SkillTrend model."""
    
    class Meta:
        model = SkillTrend
        fields = '__all__'
        read_only_fields = ('last_updated',)

