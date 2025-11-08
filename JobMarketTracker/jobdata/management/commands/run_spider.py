"""
Django management command to run the job spider manually.
"""
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from jobscraper.spiders.job_spider import JobSpider


class Command(BaseCommand):
    help = 'Run the job spider to scrape job postings'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting job spider...'))
        
        try:
            # Get Scrapy settings
            settings = get_project_settings()
            
            # Create and configure crawler process
            process = CrawlerProcess(settings)
            
            # Run the spider
            process.crawl(JobSpider)
            
            # Start the process (blocking call)
            process.start(stop_after_crawl=True)
            
            self.stdout.write(self.style.SUCCESS('Job spider completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running spider: {str(e)}'))
            raise

