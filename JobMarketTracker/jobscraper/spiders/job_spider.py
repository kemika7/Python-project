"""
Scrapy spider for scraping job postings.
This spider uses mock data for demonstration purposes.
In production, replace with actual job board URLs.
"""
import scrapy
import random
from datetime import datetime, timedelta
from jobscraper.items import JobPostingItem


class JobSpider(scrapy.Spider):
    name = 'job_spider'
    allowed_domains = ['example.com']  # Replace with actual domains
    
    # Mock job data for demonstration
    # In production, replace start_urls with actual job board URLs
    start_urls = [
        'https://example.com/jobs',  # Replace with actual URLs
    ]
    
    # Mock job data for testing
    MOCK_JOBS = [
        {
            'job_title': 'Python Developer',
            'company': 'TechCorp Inc',
            'location': 'San Francisco, CA',
            'salary_range': '80000 - 120000',
            'description': 'We are looking for a Python Developer with experience in Django, Flask, and REST APIs. Knowledge of PostgreSQL, AWS, and Docker is required.',
        },
        {
            'job_title': 'Senior Software Engineer',
            'company': 'DataSolutions Ltd',
            'location': 'New York, NY',
            'salary_range': '120000 - 160000',
            'description': 'Senior Software Engineer needed. Skills: Python, Java, React, AWS, Kubernetes, Microservices, CI/CD.',
        },
        {
            'job_title': 'Full Stack Developer',
            'company': 'WebApps Co',
            'location': 'Austin, TX',
            'salary_range': '90000 - 130000',
            'description': 'Full Stack Developer role. Requirements: JavaScript, React, Node.js, PostgreSQL, Docker, Git, Agile methodologies.',
        },
        {
            'job_title': 'Data Scientist',
            'company': 'AI Innovations',
            'location': 'Seattle, WA',
            'salary_range': '100000 - 150000',
            'description': 'Data Scientist position. Must have experience with Python, Pandas, NumPy, Scikit-learn, TensorFlow, Machine Learning, and Data Science.',
        },
        {
            'job_title': 'DevOps Engineer',
            'company': 'CloudSystems',
            'location': 'Remote',
            'salary_range': '110000 - 140000',
            'description': 'DevOps Engineer needed. Skills: AWS, Docker, Kubernetes, Jenkins, Terraform, Ansible, CI/CD, Linux, Git.',
        },
        {
            'job_title': 'Backend Engineer',
            'company': 'APIServices',
            'location': 'Boston, MA',
            'salary_range': '95000 - 125000',
            'description': 'Backend Engineer role. Experience with Python, Django, FastAPI, PostgreSQL, Redis, REST API, GraphQL required.',
        },
        {
            'job_title': 'Frontend Developer',
            'company': 'UI Experts',
            'location': 'Los Angeles, CA',
            'salary_range': '85000 - 115000',
            'description': 'Frontend Developer position. Skills needed: JavaScript, TypeScript, React, Vue, Angular, HTML, CSS, Webpack, npm.',
        },
        {
            'job_title': 'Machine Learning Engineer',
            'company': 'ML Tech',
            'location': 'Palo Alto, CA',
            'salary_range': '130000 - 180000',
            'description': 'ML Engineer role. Requirements: Python, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Deep Learning, NLP.',
        },
        {
            'job_title': 'Software Engineer - Java',
            'company': 'Enterprise Solutions',
            'location': 'Chicago, IL',
            'salary_range': '90000 - 120000',
            'description': 'Java Developer needed. Skills: Java, Spring, MySQL, REST API, Microservices, Docker, Kubernetes, Agile.',
        },
        {
            'job_title': 'React Developer',
            'company': 'ModernWeb',
            'location': 'Denver, CO',
            'salary_range': '80000 - 110000',
            'description': 'React Developer position. Must know: React, JavaScript, TypeScript, Redux, HTML, CSS, Node.js, Git.',
        },
    ]
    
    def parse(self, response):
        """
        Parse job listings from the response.
        For mock data, generates items directly.
        In production, extract data from response HTML.
        """
        # MOCK DATA MODE: Generate mock jobs for demonstration
        # In production, remove this section and parse from response HTML
        
        # Generate some random jobs from mock data
        num_jobs = random.randint(5, 10)
        selected_jobs = random.sample(self.MOCK_JOBS, min(num_jobs, len(self.MOCK_JOBS)))
        
        for job_data in selected_jobs:
            item = JobPostingItem()
            
            # Add some variation to dates (last 30 days)
            days_ago = random.randint(0, 30)
            posted_date = datetime.now() - timedelta(days=days_ago)
            
            item['job_title'] = job_data['job_title']
            item['company'] = job_data['company']
            item['location'] = job_data['location']
            item['posted_date'] = posted_date.strftime('%Y-%m-%d')
            item['salary_range'] = job_data['salary_range']
            item['description'] = job_data['description']
            item['job_url'] = f"https://example.com/jobs/{random.randint(1000, 9999)}"
            
            yield item
        
        # PRODUCTION MODE: Uncomment and use this code for real scraping
        # for job in response.css('div.job-listing'):
        #     item = JobPostingItem()
        #     item['job_title'] = job.css('h2.title::text').get()
        #     item['company'] = job.css('span.company::text').get()
        #     item['location'] = job.css('span.location::text').get()
        #     item['description'] = job.css('div.description::text').get()
        #     yield item
        #
        # # Handle pagination
        # next_page = response.css('a.next-page::attr(href)').get()
        # if next_page:
        #     yield response.follow(next_page, self.parse)
    
    def start_requests(self):
        """
        Override to skip actual HTTP requests for mock data.
        In production, remove this override to use standard Scrapy requests.
        """
        # For mock data: create a dummy request that will trigger parse()
        # In production: remove this method to use standard start_urls behavior
        from scrapy.http import Request
        from scrapy.http import HtmlResponse
        
        # Create a dummy request that won't actually make HTTP call
        # We'll handle it in download middleware or just let parse() generate mock data
        for url in self.start_urls:
            # Create request but we'll generate mock data in parse()
            yield Request(url=url, callback=self.parse, dont_filter=True, errback=self.errback_httpbin)
    
    def errback_httpbin(self, failure):
        """
        Handle request errors. For mock data, we still generate items.
        """
        # Even if request fails, generate mock data using a dummy response
        from scrapy.http import HtmlResponse
        dummy_response = HtmlResponse(
            url=self.start_urls[0] if self.start_urls else 'https://example.com',
            body=b'<html><body>Mock</body></html>',
            encoding='utf-8'
        )
        for item in self.parse(dummy_response):
            yield item

