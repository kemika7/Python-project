"""
Utility functions for job data processing.
"""
import re
from datetime import datetime
from typing import Optional, Tuple


def parse_salary(salary_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse salary range from text.
    Returns (min_salary, max_salary) tuple.
    """
    if not salary_text:
        return None, None
    
    # Remove currency symbols and commas
    salary_text = re.sub(r'[$,£€¥]', '', salary_text)
    salary_text = salary_text.replace(',', '')
    
    # Look for range pattern: "50000 - 80000" or "50k-80k"
    range_pattern = r'(\d+(?:\.\d+)?)\s*(?:k|K|000)?\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:k|K|000)?'
    match = re.search(range_pattern, salary_text)
    
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        # Convert k to thousands
        if 'k' in salary_text.lower():
            min_val *= 1000
            max_val *= 1000
        return min_val, max_val
    
    # Look for single value: "70000" or "70k"
    single_pattern = r'(\d+(?:\.\d+)?)\s*(?:k|K|000)?'
    match = re.search(single_pattern, salary_text)
    
    if match:
        val = float(match.group(1))
        if 'k' in salary_text.lower():
            val *= 1000
        return val, val
    
    return None, None


def parse_date(date_text: str) -> Optional[datetime]:
    """
    Parse date from various formats.
    Returns datetime object or None.
    """
    if not date_text:
        return None
    
    # Common date formats
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y',
    ]
    
    # Clean date text
    date_text = date_text.strip()
    
    # Handle relative dates like "2 days ago", "yesterday"
    if 'ago' in date_text.lower():
        from datetime import timedelta
        days_match = re.search(r'(\d+)', date_text)
        if days_match:
            days = int(days_match.group(1))
            return datetime.now() - timedelta(days=days)
        if 'yesterday' in date_text.lower():
            return datetime.now() - timedelta(days=1)
        if 'today' in date_text.lower():
            return datetime.now()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    
    return None


def normalize_job_title(title: str) -> str:
    """
    Normalize job title for comparison.
    Examples: "Python Dev" -> "python developer"
    """
    if not title:
        return ""
    
    title = title.lower().strip()
    
    # Common abbreviations
    replacements = {
        'dev': 'developer',
        'eng': 'engineer',
        'mgr': 'manager',
        'sr': 'senior',
        'jr': 'junior',
        'sw': 'software',
    }
    
    for abbrev, full in replacements.items():
        title = re.sub(rf'\b{abbrev}\b', full, title)
    
    # Remove special characters
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    
    return title.strip()

