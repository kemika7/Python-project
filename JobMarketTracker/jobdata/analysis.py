"""
Data analysis and NLP-based skill extraction from job postings.
"""
import re
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Set
import pandas as pd
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import JobPosting, SkillTrend

logger = logging.getLogger(__name__)

# Common tech skills keywords (expandable)
TECH_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', '.net',
    'go', 'golang', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala',
    'r', 'matlab', 'perl', 'bash', 'shell', 'powershell',
    
    # Web Frameworks
    'django', 'flask', 'fastapi', 'spring', 'react', 'vue', 'angular',
    'express', 'node.js', 'nodejs', 'next.js', 'nextjs', 'nuxt',
    'laravel', 'symfony', 'rails', 'ruby on rails',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
    'cassandra', 'elasticsearch', 'dynamodb', 'oracle', 'sqlite',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
    'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible',
    'ci/cd', 'cicd', 'devops',
    
    # Data Science & ML
    'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch',
    'keras', 'machine learning', 'deep learning', 'nlp', 'data science',
    'apache spark', 'spark', 'hadoop', 'kafka',
    
    # Frontend
    'html', 'css', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
    'webpack', 'vite', 'npm', 'yarn',
    
    # Other
    'git', 'linux', 'rest api', 'graphql', 'microservices', 'agile',
    'scrum', 'api', 'rest', 'soap',
]


def extract_skills_from_text(text: str, skill_list: List[str] = None) -> Set[str]:
    """
    Extract skills from job description text using keyword matching.
    
    Args:
        text: Job description text
        skill_list: List of skills to search for (defaults to TECH_SKILLS)
    
    Returns:
        Set of found skills
    """
    if not text:
        return set()
    
    if skill_list is None:
        skill_list = TECH_SKILLS
    
    text_lower = text.lower()
    found_skills = set()
    
    for skill in skill_list:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill.lower())
    
    return found_skills


def analyze_skills(role: str = None) -> Dict:
    """
    Analyze job postings and extract skill trends.
    
    Args:
        role: Optional role filter (e.g., 'python developer')
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Get job postings (last 365 days by default to include more historical data)
        date_threshold = timezone.now() - timedelta(days=365)
        queryset = JobPosting.objects.filter(posted_date__gte=date_threshold.date())
        
        # If no jobs found in last 365 days, use all jobs
        if not queryset.exists():
            queryset = JobPosting.objects.all()
        
        if role:
            # Normalize role for matching
            role_normalized = role.lower().strip()
            queryset = queryset.filter(
                Q(job_title__icontains=role) | Q(description__icontains=role)
            )
        
        job_postings = list(queryset.values('id', 'job_title', 'description', 'posted_date'))
        
        if not job_postings:
            logger.warning("No job postings found for analysis")
            return {'skills': {}, 'total_jobs': 0}
        
        # Extract skills from all job descriptions
        all_skills = Counter()
        role_skills_map = {}
        
        for job in job_postings:
            description = job.get('description', '')
            job_title = job.get('job_title', '')
            combined_text = f"{job_title} {description}"
            
            skills = extract_skills_from_text(combined_text)
            
            # Normalize job title for role grouping
            normalized_title = job_title.lower()
            for skill in skills:
                all_skills[skill] += 1
                
                # Group by role if specified
                if role:
                    role_key = role.lower()
                else:
                    # Extract role from title (simplified)
                    role_key = normalized_title.split()[0] if normalized_title else 'other'
                
                if role_key not in role_skills_map:
                    role_skills_map[role_key] = Counter()
                role_skills_map[role_key][skill] += 1
        
        # Update SkillTrend model
        for skill_name, frequency in all_skills.items():
            for role_key, role_skills in role_skills_map.items():
                if skill_name in role_skills:
                    skill_freq = role_skills[skill_name]
                    SkillTrend.objects.update_or_create(
                        skill_name=skill_name,
                        role=role_key,
                        defaults={'frequency': skill_freq}
                    )
        
        # Also store overall skill trends (no role)
        for skill_name, frequency in all_skills.items():
            SkillTrend.objects.update_or_create(
                skill_name=skill_name,
                role='',
                defaults={'frequency': frequency}
            )
        
        logger.info(f"Analyzed {len(job_postings)} job postings, found {len(all_skills)} unique skills")
        
        return {
            'skills': dict(all_skills.most_common(50)),
            'total_jobs': len(job_postings),
            'role_skills': {k: dict(v) for k, v in role_skills_map.items()}
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_skills: {str(e)}", exc_info=True)
        return {'skills': {}, 'total_jobs': 0, 'error': str(e)}


def get_job_volume_trends(days: int = 30, role: str = None) -> Dict:
    """
    Get job volume trends over time.
    
    Args:
        days: Number of days to analyze
        role: Optional role filter (e.g., 'python developer')
    
    Returns:
        Dictionary with date and job count
    """
    try:
        date_threshold = timezone.now() - timedelta(days=days)
        jobs = JobPosting.objects.filter(posted_date__gte=date_threshold.date())
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        # If no jobs found in the date range, try all jobs
        if not jobs.exists():
            jobs = JobPosting.objects.all()
            if role:
                role_normalized = role.lower().strip()
                jobs = jobs.filter(
                    Q(job_title__icontains=role_normalized) | 
                    Q(description__icontains=role_normalized)
                )
        
        # Group by date
        df = pd.DataFrame(list(jobs.values('posted_date')))
        if df.empty:
            return {'dates': [], 'counts': []}
        
        df['posted_date'] = pd.to_datetime(df['posted_date'])
        daily_counts = df.groupby(df['posted_date'].dt.date).size().reset_index(name='count')
        
        return {
            'dates': [str(date) for date in daily_counts['posted_date'].tolist()],
            'counts': daily_counts['count'].tolist()
        }
    except Exception as e:
        logger.error(f"Error in get_job_volume_trends: {str(e)}", exc_info=True)
        return {'dates': [], 'counts': []}


def get_avg_salary_by_role(role: str = None) -> Dict:
    """
    Calculate average salary by job role.
    
    Args:
        role: Optional role filter (e.g., 'python developer')
    
    Returns:
        Dictionary with role and average salary data
    """
    try:
        # Get jobs with salary data
        jobs_with_salary = JobPosting.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False
        )
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs_with_salary = jobs_with_salary.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs_with_salary.exists():
            return {'roles': [], 'avg_salaries': [], 'min_salaries': [], 'max_salaries': []}
        
        # Use pandas for easier aggregation
        df = pd.DataFrame(list(jobs_with_salary.values('job_title', 'salary_min', 'salary_max')))
        
        if role:
            # If role is specified, show average for that role
            df['avg_salary'] = (df['salary_min'] + df['salary_max']) / 2
            avg_salary = df['avg_salary'].mean()
            min_salary = df['salary_min'].mean()
            max_salary = df['salary_max'].mean()
            
            # Use the role name or extract from job titles
            role_name = role.lower().strip()
            if df['job_title'].notna().any():
                # Get most common job title that matches
                matching_titles = df[df['job_title'].str.lower().str.contains(role_name, na=False)]['job_title']
                if not matching_titles.empty:
                    role_name = matching_titles.mode()[0] if not matching_titles.mode().empty else role_name
            
            return {
                'roles': [role_name],
                'avg_salaries': [round(avg_salary, 2)],
                'min_salaries': [round(min_salary, 2)],
                'max_salaries': [round(max_salary, 2)],
                'counts': [len(df)]
            }
        else:
            # Normalize job titles for grouping
            df['normalized_title'] = df['job_title'].apply(lambda x: x.lower().split()[0] if x else 'other')
            df['avg_salary'] = (df['salary_min'] + df['salary_max']) / 2
            
            # Group by normalized title
            role_stats = df.groupby('normalized_title').agg({
                'avg_salary': 'mean',
                'salary_min': 'mean',
                'salary_max': 'mean',
                'job_title': 'count'
            }).reset_index()
            
            role_stats = role_stats.rename(columns={'job_title': 'count'})
            role_stats = role_stats.sort_values('avg_salary', ascending=False)
            
            return {
                'roles': role_stats['normalized_title'].tolist(),
                'avg_salaries': role_stats['avg_salary'].round(2).tolist(),
                'min_salaries': role_stats['salary_min'].round(2).tolist(),
                'max_salaries': role_stats['salary_max'].round(2).tolist(),
                'counts': role_stats['count'].tolist()
            }
    except Exception as e:
        logger.error(f"Error in get_avg_salary_by_role: {str(e)}", exc_info=True)
        return {'roles': [], 'avg_salaries': []}

