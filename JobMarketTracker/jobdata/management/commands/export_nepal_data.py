"""
Django management command to export Nepal job market data to CSV.
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from jobdata.models import JobPosting
from jobdata.analysis import extract_skills_from_text


class Command(BaseCommand):
    help = 'Export Nepal job market data to CSV format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='nepal_job_market_data.csv',
            help='Output CSV file path',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        self.stdout.write(self.style.SUCCESS(f'Exporting job market data to {output_file}...'))
        
        jobs = JobPosting.objects.all().order_by('-posted_date')
        
        if not jobs.exists():
            self.stdout.write(self.style.WARNING('No job postings found. Load data first:'))
            self.stdout.write(self.style.WARNING('python manage.py loaddata nepal_job_market_data.json'))
            return
        
        # Prepare CSV data
        csv_data = []
        for job in jobs:
            # Extract skills from description
            skills = extract_skills_from_text(job.description)
            skills_list = ', '.join(sorted(skills))
            
            # Determine experience level
            desc_lower = job.description.lower()
            experience_level = 'Not Specified'
            if any(kw in desc_lower for kw in ['5+', 'senior', '4-5', '5-7']):
                experience_level = 'Senior (4+ years)'
            elif any(kw in desc_lower for kw in ['2-3', '3-4', '2-4', 'mid']):
                experience_level = 'Mid (2-4 years)'
            elif any(kw in desc_lower for kw in ['0-1', '1-2', '0-2', 'junior', 'entry']):
                experience_level = 'Entry (0-2 years)'
            
            # Calculate average salary
            avg_salary = None
            if job.salary_min and job.salary_max:
                avg_salary = (job.salary_min + job.salary_max) / 2
            
            # Suggest additional skills based on role
            suggested_skills = self.get_suggested_skills(job.job_title, skills)
            suggested_skills_list = ', '.join(sorted(suggested_skills))
            
            csv_data.append({
                'Job Title': job.job_title,
                'Company': job.company,
                'Location': job.location,
                'Required Skills': skills_list,
                'Suggested Additional Skills': suggested_skills_list,
                'Experience Level': experience_level,
                'Salary Min (NPR)': job.salary_min or '',
                'Salary Max (NPR)': job.salary_max or '',
                'Average Salary (NPR)': f"{avg_salary:,.0f}" if avg_salary else '',
                'Posted Date': job.posted_date.strftime('%Y-%m-%d'),
                'Job URL': job.job_url or '',
                'Description': job.description[:200] + '...' if len(job.description) > 200 else job.description
            })
        
        # Write to CSV
        if csv_data:
            fieldnames = [
                'Job Title', 'Company', 'Location', 'Required Skills',
                'Suggested Additional Skills', 'Experience Level',
                'Salary Min (NPR)', 'Salary Max (NPR)', 'Average Salary (NPR)',
                'Posted Date', 'Job URL', 'Description'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully exported {len(csv_data)} job postings to {output_file}'
            ))
        else:
            self.stdout.write(self.style.WARNING('No data to export'))
    
    def get_suggested_skills(self, job_title, existing_skills):
        """Suggest additional skills based on role."""
        suggestions = {
            'python developer': [
                'FastAPI', 'Celery', 'Kubernetes', 'GraphQL', 'Microservices',
                'CI/CD', 'Redis', 'Machine Learning Basics', 'Azure', 'GCP'
            ],
            'data scientist': [
                'PyTorch', 'Deep Learning', 'NLP', 'Apache Spark', 'MLflow',
                'MLOps', 'Data Visualization', 'Statistical Analysis', 'A/B Testing',
                'Business Intelligence', 'Tableau', 'Power BI'
            ],
            'web developer': [
                'TypeScript', 'Vue.js', 'Next.js', 'GraphQL', 'Microservices',
                'Kubernetes', 'MongoDB', 'Redis', 'Tailwind CSS', 'CI/CD'
            ],
            'mobile': [
                'Flutter', 'Swift', 'Kotlin', 'Native Modules', 'App Performance',
                'Biometric Authentication', 'Payment Gateway Integration',
                'State Management', 'Firebase', 'App Store Optimization'
            ],
            'ai': [
                'MLOps', 'Model Deployment', 'LLMs', 'Transformers', 'Generative AI',
                'Computer Vision', 'Reinforcement Learning', 'Model Optimization',
                'Real-time ML Inference', 'MLflow', 'Kubernetes for ML'
            ]
        }
        
        job_lower = job_title.lower()
        suggested = set()
        
        for key, skills in suggestions.items():
            if key in job_lower:
                for skill in skills:
                    if skill.lower() not in [s.lower() for s in existing_skills]:
                        suggested.add(skill)
        
        return list(suggested)

