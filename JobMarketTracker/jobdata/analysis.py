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


def get_company_distribution(role: str = None, top_n: int = 10) -> Dict:
    """
    Get job distribution by company for a specific role.
    
    Args:
        role: Optional role filter
        top_n: Number of top companies to return
    
    Returns:
        Dictionary with company names and job counts
    """
    try:
        jobs = JobPosting.objects.all()
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        # Group by company
        company_counts = jobs.values('company').annotate(
            count=Count('id')
        ).order_by('-count')[:top_n]
        
        companies = [item['company'] for item in company_counts]
        counts = [item['count'] for item in company_counts]
        
        return {
            'companies': companies,
            'counts': counts,
            'total': sum(counts)
        }
    except Exception as e:
        logger.error(f"Error in get_company_distribution: {str(e)}", exc_info=True)
        return {'companies': [], 'counts': [], 'total': 0}


def get_location_distribution(role: str = None) -> Dict:
    """
    Get job distribution by location (city) in Nepal.
    
    Args:
        role: Optional role filter
    
    Returns:
        Dictionary with locations and job counts
    """
    try:
        jobs = JobPosting.objects.all()
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        # Group by location
        location_counts = jobs.values('location').annotate(
            count=Count('id')
        ).order_by('-count')
        
        locations = []
        counts = []
        
        for item in location_counts:
            # Extract city name (handle formats like "Kathmandu, Nepal" or just "Kathmandu")
            location = item['location']
            if location:
                # Take first part before comma if exists
                city = location.split(',')[0].strip()
                locations.append(city)
                counts.append(item['count'])
        
        return {
            'locations': locations,
            'counts': counts,
            'total': sum(counts)
        }
    except Exception as e:
        logger.error(f"Error in get_location_distribution: {str(e)}", exc_info=True)
        return {'locations': [], 'counts': [], 'total': 0}


def get_experience_breakdown(role: str = None) -> Dict:
    """
    Get breakdown of jobs by experience level.
    
    Args:
        role: Optional role filter
    
    Returns:
        Dictionary with experience levels and counts
    """
    try:
        jobs = JobPosting.objects.all()
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        # Group by experience level
        exp_counts = jobs.values('experience_level').annotate(
            count=Count('id')
        )
        
        # Map experience levels to readable names
        exp_map = {
            'entry': 'Entry Level',
            'mid': 'Mid Level',
            'senior': 'Senior Level',
            'lead': 'Lead/Principal',
            '': 'Not Specified'
        }
        
        levels = []
        counts = []
        
        for item in exp_counts:
            level = item['experience_level'] or ''
            levels.append(exp_map.get(level, level.title()))
            counts.append(item['count'])
        
        return {
            'levels': levels,
            'counts': counts,
            'total': sum(counts)
        }
    except Exception as e:
        logger.error(f"Error in get_experience_breakdown: {str(e)}", exc_info=True)
        return {'levels': [], 'counts': [], 'total': 0}


def get_salary_distribution(role: str = None, bins: int = 10) -> Dict:
    """
    Get salary distribution histogram data for a role.
    
    Args:
        role: Optional role filter
        bins: Number of salary bins
    
    Returns:
        Dictionary with salary ranges and counts
    """
    try:
        jobs = JobPosting.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False
        )
        
        # Filter by role if provided
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs.exists():
            return {'ranges': [], 'counts': [], 'min_salary': 0, 'max_salary': 0}
        
        # Calculate average salary for each job
        df = pd.DataFrame(list(jobs.values('salary_min', 'salary_max')))
        df['avg_salary'] = (df['salary_min'] + df['salary_max']) / 2
        
        min_salary = df['avg_salary'].min()
        max_salary = df['avg_salary'].max()
        
        # Create bins
        bin_width = (max_salary - min_salary) / bins if max_salary > min_salary else 10000
        bin_edges = [min_salary + i * bin_width for i in range(bins + 1)]
        
        # Count jobs in each bin
        df['bin'] = pd.cut(df['avg_salary'], bins=bin_edges, include_lowest=True)
        bin_counts = df['bin'].value_counts().sort_index()
        
        ranges = []
        counts = []
        
        for bin_range, count in bin_counts.items():
            # Format range label
            left = int(bin_range.left)
            right = int(bin_range.right)
            ranges.append(f"NPR {left:,} - {right:,}")
            counts.append(int(count))
        
        return {
            'ranges': ranges,
            'counts': counts,
            'min_salary': int(min_salary),
            'max_salary': int(max_salary),
            'total': len(df)
        }
    except Exception as e:
        logger.error(f"Error in get_salary_distribution: {str(e)}", exc_info=True)
        return {'ranges': [], 'counts': [], 'min_salary': 0, 'max_salary': 0, 'total': 0}


def get_job_role_distribution(limit: int = 5) -> Dict:
    """
    Get distribution of jobs by role (for bar and pie charts).
    
    Args:
        limit: Number of top roles to return (default: 5)
    
    Returns:
        Dictionary with role names and job counts
    """
    try:
        # Get all jobs and group by job title (normalized)
        jobs = JobPosting.objects.all()
        
        # Use pandas for easier grouping
        df = pd.DataFrame(list(jobs.values('job_title')))
        
        if df.empty:
            return {'roles': [], 'counts': []}
        
        # Normalize job titles (take first word or common patterns)
        def normalize_title(title):
            if not title:
                return 'Other'
            title_lower = title.lower()
            # Common role patterns
            if 'python' in title_lower:
                return 'Python Developer'
            elif 'data scientist' in title_lower or 'data science' in title_lower:
                return 'Data Scientist'
            elif 'full stack' in title_lower or 'fullstack' in title_lower:
                return 'Full Stack Developer'
            elif 'backend' in title_lower:
                return 'Backend Developer'
            elif 'frontend' in title_lower or 'front-end' in title_lower:
                return 'Frontend Developer'
            elif 'ai' in title_lower or 'ml' in title_lower or 'machine learning' in title_lower:
                return 'AI/ML Engineer'
            elif 'mobile' in title_lower or 'android' in title_lower or 'ios' in title_lower:
                return 'Mobile Developer'
            elif 'devops' in title_lower:
                return 'DevOps Engineer'
            else:
                # Take first significant word
                words = title.split()
                if words:
                    return words[0] + ' Developer' if len(words[0]) > 3 else title
                return title
        
        df['normalized_role'] = df['job_title'].apply(normalize_title)
        
        # Count by normalized role
        role_counts = df['normalized_role'].value_counts().head(limit)
        
        return {
            'roles': role_counts.index.tolist(),
            'counts': role_counts.values.tolist(),
            'total': len(df)
        }
    except Exception as e:
        logger.error(f"Error in get_job_role_distribution: {str(e)}", exc_info=True)
        return {'roles': [], 'counts': [], 'total': 0}


def get_skill_correlations(role: str = None, top_skills: int = 10) -> Dict:
    """
    Get skill correlation data showing which skills appear together.
    
    Args:
        role: Optional role filter
        top_skills: Number of top skills to analyze
    
    Returns:
        Dictionary with skill pairs and co-occurrence counts
    """
    try:
        # First get top skills for the role
        if role:
            result = analyze_skills(role=role)
            skills_dict = result.get('skills', {})
        else:
            skills = SkillTrend.objects.filter(role='').order_by('-frequency')[:top_skills]
            skills_dict = {skill.skill_name: skill.frequency for skill in skills}
        
        if not skills_dict:
            return {'pairs': [], 'nodes': [], 'links': []}
        
        # Get top skills
        top_skill_names = sorted(skills_dict.items(), key=lambda x: x[1], reverse=True)[:top_skills]
        top_skill_names = [skill[0] for skill in top_skill_names]
        
        # Get jobs
        jobs = JobPosting.objects.all()
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        # Count co-occurrences
        skill_pairs = Counter()
        
        for job in jobs:
            description_lower = job.description.lower()
            job_skills = [skill for skill in top_skill_names if skill.lower() in description_lower]
            
            # Count pairs
            for i, skill1 in enumerate(job_skills):
                for skill2 in job_skills[i+1:]:
                    pair = tuple(sorted([skill1, skill2]))
                    skill_pairs[pair] += 1
        
        # Format for visualization
        pairs = []
        for (skill1, skill2), count in skill_pairs.most_common(20):
            pairs.append({
                'skill1': skill1,
                'skill2': skill2,
                'count': count
            })
        
        return {
            'pairs': pairs,
            'top_skills': top_skill_names
        }
    except Exception as e:
        logger.error(f"Error in get_skill_correlations: {str(e)}", exc_info=True)
        return {'pairs': [], 'top_skills': []}


def get_location_distribution(role: str = None) -> Dict:
    """
    Get job distribution by location (cities in Nepal).
    
    Args:
        role: Optional role filter
    
    Returns:
        Dictionary with locations and job counts
    """
    try:
        jobs = JobPosting.objects.all()
        
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs.exists():
            return {'locations': [], 'counts': []}
        
        df = pd.DataFrame(list(jobs.values('location')))
        
        # Extract city names (handle formats like "Kathmandu, Nepal" or just "Kathmandu")
        df['city'] = df['location'].apply(lambda x: x.split(',')[0].strip() if x else 'Unknown')
        location_counts = df['city'].value_counts()
        
        return {
            'locations': location_counts.index.tolist(),
            'counts': location_counts.values.tolist()
        }
    except Exception as e:
        logger.error(f"Error in get_location_distribution: {str(e)}", exc_info=True)
        return {'locations': [], 'counts': []}


def get_experience_level_breakdown(role: str = None) -> Dict:
    """
    Get breakdown of jobs by experience level.
    
    Args:
        role: Optional role filter
    
    Returns:
        Dictionary with experience levels and counts
    """
    try:
        jobs = JobPosting.objects.all()
        
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs.exists():
            return {'levels': [], 'counts': [], 'labels': []}
        
        # Infer experience level from job title and description if not set
        jobs_list = list(jobs.values('job_title', 'description', 'experience_level'))
        for job in jobs_list:
            if not job['experience_level']:
                title_lower = job['job_title'].lower()
                desc_lower = (job['description'] or '').lower()
                
                if any(word in title_lower or word in desc_lower for word in ['senior', 'lead', 'principal', 'architect', '5+', '6+', '7+']):
                    job['experience_level'] = 'senior'
                elif any(word in title_lower or word in desc_lower for word in ['junior', 'entry', 'fresher', '0-1', '1-2']):
                    job['experience_level'] = 'entry'
                elif any(word in title_lower or word in desc_lower for word in ['mid', '2-3', '3-4', '4-5']):
                    job['experience_level'] = 'mid'
                else:
                    job['experience_level'] = 'mid'  # Default
        
        df = pd.DataFrame(jobs_list)
        experience_counts = df['experience_level'].value_counts()
        
        # Map to readable labels
        level_labels = {
            'entry': 'Entry Level',
            'mid': 'Mid Level',
            'senior': 'Senior Level',
            'lead': 'Lead/Principal'
        }
        
        labels = [level_labels.get(level, level.title()) for level in experience_counts.index]
        
        return {
            'levels': experience_counts.index.tolist(),
            'counts': experience_counts.values.tolist(),
            'labels': labels
        }
    except Exception as e:
        logger.error(f"Error in get_experience_level_breakdown: {str(e)}", exc_info=True)
        return {'levels': [], 'counts': [], 'labels': []}


def get_salary_distribution(role: str = None, bins: int = 10) -> Dict:
    """
    Get salary distribution histogram data.
    
    Args:
        role: Optional role filter
        bins: Number of salary bins/ranges
    
    Returns:
        Dictionary with salary ranges and counts
    """
    try:
        jobs = JobPosting.objects.filter(
            salary_min__isnull=False,
            salary_max__isnull=False
        )
        
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs.exists():
            return {'ranges': [], 'counts': []}
        
        df = pd.DataFrame(list(jobs.values('salary_min', 'salary_max')))
        df['avg_salary'] = (df['salary_min'] + df['salary_max']) / 2
        
        # Create bins
        min_salary = df['avg_salary'].min()
        max_salary = df['avg_salary'].max()
        bin_width = (max_salary - min_salary) / bins
        
        # Create range labels
        ranges = []
        counts = []
        for i in range(bins):
            range_start = min_salary + (i * bin_width)
            range_end = min_salary + ((i + 1) * bin_width)
            range_label = f"NPR {int(range_start/1000)}K-{int(range_end/1000)}K"
            ranges.append(range_label)
            
            count = len(df[(df['avg_salary'] >= range_start) & (df['avg_salary'] < range_end)])
            counts.append(count)
        
        return {
            'ranges': ranges,
            'counts': counts
        }
    except Exception as e:
        logger.error(f"Error in get_salary_distribution: {str(e)}", exc_info=True)
        return {'ranges': [], 'counts': []}


def get_skill_correlations(role: str = None, top_skills: int = 15) -> Dict:
    """
    Get skill correlation data (which skills appear together).
    
    Args:
        role: Optional role filter
        top_skills: Number of top skills to analyze
    
    Returns:
        Dictionary with skill pairs and co-occurrence counts
    """
    try:
        date_threshold = timezone.now() - timedelta(days=365)
        jobs = JobPosting.objects.filter(posted_date__gte=date_threshold.date())
        
        if not jobs.exists():
            jobs = JobPosting.objects.all()
        
        if role:
            role_normalized = role.lower().strip()
            jobs = jobs.filter(
                Q(job_title__icontains=role_normalized) | 
                Q(description__icontains=role_normalized)
            )
        
        if not jobs.exists():
            return {'skills': [], 'connections': []}
        
        # Extract skills from all job descriptions
        all_skills = []
        for job in jobs:
            skills = extract_skills_from_text(job.description)
            all_skills.append(list(skills))
        
        # Get top skills
        skill_counts = Counter([skill for skills_list in all_skills for skill in skills_list])
        top_skill_names = [skill for skill, _ in skill_counts.most_common(top_skills)]
        
        # Count co-occurrences
        skill_pairs = {}
        for skills_list in all_skills:
            skills_in_list = [s for s in skills_list if s in top_skill_names]
            for i, skill1 in enumerate(skills_in_list):
                for skill2 in skills_in_list[i+1:]:
                    pair = tuple(sorted([skill1, skill2]))
                    skill_pairs[pair] = skill_pairs.get(pair, 0) + 1
        
        # Format for visualization
        connections = []
        for (skill1, skill2), count in sorted(skill_pairs.items(), key=lambda x: x[1], reverse=True)[:30]:
            connections.append({
                'source': skill1,
                'target': skill2,
                'value': count
            })
        
        return {
            'skills': top_skill_names,
            'connections': connections
        }
    except Exception as e:
        logger.error(f"Error in get_skill_correlations: {str(e)}", exc_info=True)
        return {'skills': [], 'connections': []}

