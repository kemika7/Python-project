"""
Scrapy items for job scraping.
"""
import scrapy
from scrapy_djangoitem import DjangoItem
from jobdata.models import JobPosting


class JobPostingItem(DjangoItem):
    """
    Scrapy item for job postings.
    Maps directly to Django JobPosting model.
    """
    django_model = JobPosting

