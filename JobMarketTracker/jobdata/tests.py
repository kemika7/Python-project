"""
Tests for jobdata app.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import JobPosting, SkillTrend
from .utils import parse_salary, parse_date, normalize_job_title
from .analysis import extract_skills_from_text, analyze_skills


class JobPostingModelTest(TestCase):
    """Test JobPosting model."""
    
    def setUp(self):
        self.job = JobPosting.objects.create(
            job_title='Python Developer',
            company='Test Corp',
            location='San Francisco, CA',
            posted_date=timezone.now().date(),
            salary_min=80000.0,
            salary_max=120000.0,
            description='Python Developer with Django experience'
        )
    
    def test_job_creation(self):
        self.assertEqual(self.job.job_title, 'Python Developer')
        self.assertEqual(self.job.company, 'Test Corp')
    
    def test_job_str(self):
        self.assertIn('Python Developer', str(self.job))
        self.assertIn('Test Corp', str(self.job))


class UtilsTest(TestCase):
    """Test utility functions."""
    
    def test_parse_salary_range(self):
        min_sal, max_sal = parse_salary('80000 - 120000')
        self.assertEqual(min_sal, 80000.0)
        self.assertEqual(max_sal, 120000.0)
    
    def test_parse_salary_k_format(self):
        min_sal, max_sal = parse_salary('80k - 120k')
        self.assertEqual(min_sal, 80000.0)
        self.assertEqual(max_sal, 120000.0)
    
    def test_normalize_job_title(self):
        normalized = normalize_job_title('Python Dev')
        self.assertIn('developer', normalized)
    
    def test_extract_skills(self):
        text = 'We need a Python Developer with Django and PostgreSQL experience'
        skills = extract_skills_from_text(text)
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertIn('postgresql', skills)


class AnalysisTest(TestCase):
    """Test analysis functions."""
    
    def setUp(self):
        # Create test job postings
        JobPosting.objects.create(
            job_title='Python Developer',
            company='TechCorp',
            location='SF',
            posted_date=timezone.now().date(),
            description='Python, Django, PostgreSQL, AWS'
        )
        JobPosting.objects.create(
            job_title='JavaScript Developer',
            company='WebCorp',
            location='NY',
            posted_date=timezone.now().date(),
            description='JavaScript, React, Node.js, MongoDB'
        )
    
    def test_analyze_skills(self):
        result = analyze_skills()
        self.assertIn('total_jobs', result)
        self.assertGreater(result['total_jobs'], 0)
    
    def test_extract_skills_from_text(self):
        text = 'Python Developer with Django and PostgreSQL'
        skills = extract_skills_from_text(text)
        self.assertGreater(len(skills), 0)

