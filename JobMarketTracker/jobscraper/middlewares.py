"""
Scrapy middlewares for jobscraper project.
"""
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.exceptions import NotConfigured


class MockDataMiddleware:
    """
    Middleware to handle mock data generation without making HTTP requests.
    """
    
    def __init__(self):
        self.enabled = True  # Set to False in production
    
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('MOCK_DATA_ENABLED', True):
            raise NotConfigured('MockDataMiddleware not enabled')
        return cls()
    
    def process_request(self, request, spider):
        """
        Intercept requests and return a mock response for demonstration.
        In production, remove this middleware.
        """
        # Only process requests for our mock spider
        if spider.name == 'job_spider' and 'example.com' in request.url:
            # Return a mock response - this will trigger parse() method
            # The parse() method will generate mock data
            return HtmlResponse(
                url=request.url,
                body=b'<html><body>Mock Job Listings</body></html>',
                encoding='utf-8'
            )
        # For real URLs, let the request proceed normally
        return None

