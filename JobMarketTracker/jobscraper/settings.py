"""
Scrapy settings for jobscraper project.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobMarketTracker.settings')
django.setup()

BOT_NAME = 'jobscraper'

SPIDER_MODULES = ['jobscraper.spiders']
NEWSPIDER_MODULE = 'jobscraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays for requests
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Enable and configure autothrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Configure retry middleware
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# User agent
USER_AGENT = 'JobMarketTracker (+http://www.yourdomain.com)'

# Enable pipelines
ITEM_PIPELINES = {
    'jobscraper.pipelines.DataCleaningPipeline': 200,
    'jobscraper.pipelines.DjangoPipeline': 300,
}

# Enable middlewares (for mock data)
DOWNLOADER_MIDDLEWARES = {
    'jobscraper.middlewares.MockDataMiddleware': 543,
}

# Mock data mode (set to False in production)
MOCK_DATA_ENABLED = True

# Enable extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# Logging
LOG_LEVEL = 'INFO'

# Set settings whose default value is deprecated
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

