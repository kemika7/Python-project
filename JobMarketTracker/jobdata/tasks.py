"""
Celery tasks for JobMarketTracker.
"""
import logging
from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobdata.analysis import analyze_skills

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_job_spider(self):
    """
    Celery task to run the job spider.
    """
    try:
        logger.info("Starting job spider task...")
        
        # Import here to avoid circular imports
        from jobscraper.spiders.job_spider import JobSpider
        
        # Get Scrapy settings
        settings = get_project_settings()
        
        # Create and configure crawler process
        process = CrawlerProcess(settings)
        
        # Run the spider
        process.crawl(JobSpider)
        
        # Start the process (blocking call)
        process.start(stop_after_crawl=True)
        
        logger.info("Job spider task completed successfully")
        
        # Trigger skill analysis after scraping
        analyze_skills_task.delay()
        
        return {"status": "success", "message": "Job spider completed"}
    
    except Exception as exc:
        logger.error(f"Error in run_job_spider task: {str(exc)}", exc_info=True)
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * 5)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def analyze_skills_task(self, role=None):
    """
    Celery task to analyze skills from job postings.
    """
    try:
        logger.info(f"Starting skill analysis task (role: {role})...")
        
        result = analyze_skills(role=role)
        
        logger.info(f"Skill analysis completed. Found {result.get('total_jobs', 0)} jobs.")
        
        return {
            "status": "success",
            "total_jobs": result.get('total_jobs', 0),
            "skills_count": len(result.get('skills', {}))
        }
    
    except Exception as exc:
        logger.error(f"Error in analyze_skills_task: {str(exc)}", exc_info=True)
        raise self.retry(exc=exc, countdown=60 * 10)  # Retry after 10 minutes

