"""
Script to generate comprehensive analysis from Nepal job market data.
"""
import json
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobMarketTracker.settings')
django.setup()

from jobdata.models import JobPosting, SkillTrend
from collections import Counter
from datetime import datetime, timedelta
from django.utils import timezone


def analyze_nepal_job_market():
    """Generate comprehensive analysis of Nepal job market."""
    
    # Get all job postings
    jobs = JobPosting.objects.all()
    
    if not jobs.exists():
        print("No job postings found. Please load the data first:")
        print("python manage.py loaddata nepal_job_market_data.json")
        return
    
    print("=" * 80)
    print("NEPAL JOB MARKET ANALYSIS")
    print("=" * 80)
    print()
    
    # 1. Role Distribution
    print("1. ROLE DISTRIBUTION")
    print("-" * 80)
    role_counts = Counter()
    for job in jobs:
        role_counts[job.job_title] += 1
    
    for role, count in role_counts.most_common():
        percentage = (count / jobs.count()) * 100
        print(f"  {role}: {count} postings ({percentage:.1f}%)")
    print()
    
    # 2. Location Distribution
    print("2. LOCATION DISTRIBUTION")
    print("-" * 80)
    location_counts = Counter()
    for job in jobs:
        location_counts[job.location] += 1
    
    for location, count in location_counts.most_common():
        percentage = (count / jobs.count()) * 100
        print(f"  {location}: {count} postings ({percentage:.1f}%)")
    print()
    
    # 3. Company Distribution
    print("3. TOP COMPANIES HIRING")
    print("-" * 80)
    company_counts = Counter()
    for job in jobs:
        company_counts[job.company] += 1
    
    for company, count in company_counts.most_common(10):
        print(f"  {company}: {count} postings")
    print()
    
    # 4. Salary Analysis by Role
    print("4. SALARY ANALYSIS BY ROLE")
    print("-" * 80)
    role_salaries = {}
    for job in jobs:
        if job.salary_min and job.salary_max:
            role = job.job_title
            if role not in role_salaries:
                role_salaries[role] = {'min': [], 'max': [], 'avg': []}
            role_salaries[role]['min'].append(job.salary_min)
            role_salaries[role]['max'].append(job.salary_max)
            role_salaries[role]['avg'].append((job.salary_min + job.salary_max) / 2)
    
    for role, salaries in sorted(role_salaries.items()):
        avg_min = sum(salaries['min']) / len(salaries['min'])
        avg_max = sum(salaries['max']) / len(salaries['max'])
        avg_avg = sum(salaries['avg']) / len(salaries['avg'])
        print(f"  {role}:")
        print(f"    Min: NPR {avg_min:,.0f}")
        print(f"    Max: NPR {avg_max:,.0f}")
        print(f"    Avg: NPR {avg_avg:,.0f}")
    print()
    
    # 5. Skills Analysis
    print("5. SKILLS ANALYSIS")
    print("-" * 80)
    skill_trends = SkillTrend.objects.all().order_by('-frequency')
    
    if skill_trends.exists():
        print("  Top 20 Most Demanded Skills:")
        for i, skill in enumerate(skill_trends[:20], 1):
            print(f"    {i}. {skill.skill_name}: {skill.frequency} occurrences")
    else:
        print("  No skills analyzed yet. Run: python manage.py analyze_skills")
    print()
    
    # 6. Experience Level Analysis
    print("6. EXPERIENCE LEVEL ANALYSIS")
    print("-" * 80)
    experience_keywords = {
        'entry': ['0-1', '1-2', 'junior', 'entry', '0-2'],
        'mid': ['2-3', '3-4', '2-4', 'mid'],
        'senior': ['4+', '5+', 'senior', '4-5', '5-7']
    }
    
    exp_counts = {'entry': 0, 'mid': 0, 'senior': 0}
    for job in jobs:
        desc_lower = job.description.lower()
        if any(kw in desc_lower for kw in experience_keywords['senior']):
            exp_counts['senior'] += 1
        elif any(kw in desc_lower for kw in experience_keywords['mid']):
            exp_counts['mid'] += 1
        elif any(kw in desc_lower for kw in experience_keywords['entry']):
            exp_counts['entry'] += 1
    
    total_with_exp = sum(exp_counts.values())
    if total_with_exp > 0:
        for level, count in exp_counts.items():
            percentage = (count / total_with_exp) * 100
            print(f"  {level.capitalize()} Level: {count} postings ({percentage:.1f}%)")
    print()
    
    # 7. Trends Summary
    print("7. MARKET TRENDS SUMMARY")
    print("-" * 80)
    print(f"  Total Job Postings: {jobs.count()}")
    print(f"  Companies: {company_counts.__len__()}")
    print(f"  Locations: {location_counts.__len__()}")
    print(f"  Unique Roles: {role_counts.__len__()}")
    
    jobs_with_salary = jobs.filter(salary_min__isnull=False, salary_max__isnull=False).count()
    if jobs_with_salary > 0:
        avg_salary_min = sum(j.salary_min for j in jobs.filter(salary_min__isnull=False)) / jobs.filter(salary_min__isnull=False).count()
        avg_salary_max = sum(j.salary_max for j in jobs.filter(salary_max__isnull=False)) / jobs.filter(salary_max__isnull=False).count()
        print(f"  Jobs with Salary Info: {jobs_with_salary}")
        print(f"  Average Salary Range: NPR {avg_salary_min:,.0f} - {avg_salary_max:,.0f}")
    print()
    
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)


if __name__ == '__main__':
    analyze_nepal_job_market()

