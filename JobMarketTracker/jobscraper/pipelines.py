"""
Scrapy pipelines for processing scraped items.
"""
import logging
from datetime import datetime
from jobdata.models import JobPosting
from jobdata.utils import parse_salary, parse_date, normalize_job_title

logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """
    Pipeline to clean and normalize scraped data.
    """
    
    def process_item(self, item, spider):
        """
        Clean and normalize item data.
        """
        # Clean job title
        if 'job_title' in item and item['job_title']:
            item['job_title'] = item['job_title'].strip()
        
        # Clean company name
        if 'company' in item and item['company']:
            item['company'] = item['company'].strip()
        
        # Clean location
        if 'location' in item and item['location']:
            item['location'] = item['location'].strip()
        
        # Parse salary
        if 'salary_range' in item and item['salary_range']:
            salary_min, salary_max = parse_salary(item['salary_range'])
            item['salary_min'] = salary_min
            item['salary_max'] = salary_max
            del item['salary_range']
        elif 'salary_min' not in item or not item.get('salary_min'):
            item['salary_min'] = None
        if 'salary_max' not in item or not item.get('salary_max'):
            item['salary_max'] = None
        
        # Parse posted date
        if 'posted_date' in item:
            if isinstance(item['posted_date'], str):
                parsed_date = parse_date(item['posted_date'])
                if parsed_date:
                    item['posted_date'] = parsed_date.date()
                else:
                    # Default to today if parsing fails
                    item['posted_date'] = datetime.now().date()
            elif isinstance(item['posted_date'], datetime):
                item['posted_date'] = item['posted_date'].date()
        
        # Clean description
        if 'description' in item and item['description']:
            item['description'] = item['description'].strip()
        
        return item


class DjangoPipeline:
    """
    Pipeline to save items to Django database.
    """
    
    def process_item(self, item, spider):
        """
        Save item to Django database, avoiding duplicates.
        """
        try:
            # Check for duplicates based on job_title, company, and posted_date
            job_title = item.get('job_title')
            company = item.get('company')
            posted_date = item.get('posted_date')
            
            if not all([job_title, company, posted_date]):
                logger.warning(f"Incomplete item data: {item}")
                return item
            
            # Check if job already exists
            existing_job = JobPosting.objects.filter(
                job_title=job_title,
                company=company,
                posted_date=posted_date
            ).first()
            
            if existing_job:
                logger.info(f"Duplicate job found: {job_title} at {company}")
                return item
            
            # Create new job posting
            job_posting = JobPosting(
                job_title=job_title,
                company=company,
                location=item.get('location', ''),
                posted_date=posted_date,
                salary_min=item.get('salary_min'),
                salary_max=item.get('salary_max'),
                description=item.get('description', ''),
                job_url=item.get('job_url', ''),
            )
            
            job_posting.save()
            logger.info(f"Saved job: {job_title} at {company}")
            
            return item
        
        except Exception as e:
            logger.error(f"Error saving item to database: {str(e)}", exc_info=True)
            # Don't raise exception to allow pipeline to continue
            return item

