# JobMarketTracker

A comprehensive Django-based Real-Time Job Market Tracker that collects job postings, analyzes demand trends, extracts required skills, and visualizes insights through an interactive dashboard.

## 🚀 Features

- **Web Scraping**: Automated job posting collection using Scrapy
- **Task Scheduling**: Celery + Redis for automated scraping and analysis
- **NLP Analysis**: Skill extraction from job descriptions using keyword matching
- **REST API**: Django REST Framework endpoints for job data and analytics
- **Interactive Dashboard**: Real-time visualization of job trends, skills, and salaries
- **Data Analytics**: Job volume trends, skill demand analysis, and salary statistics

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite for development)
- Redis (for Celery broker)
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the repository and navigate to the project directory

```bash
cd JobMarketTracker
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install spaCy language model (optional, for advanced NLP)

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_NAME=jobmarkettracker
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Note**: For SQLite (development), you can leave database settings empty.

### 6. Set up the database

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 7. Load initial test data (optional)

```bash
python manage.py loaddata jobdata/fixtures/initial_data.json
```

## 🚀 Running the Application

### 1. Start Redis (required for Celery)

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**On Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**On Windows:**
Download and install Redis from https://redis.io/download

### 2. Start Celery Worker (in a separate terminal)

```bash
celery -A JobMarketTracker worker -l info
```

### 3. Start Celery Beat (in another separate terminal)

```bash
celery -A JobMarketTracker beat -l info
```

### 4. Start Django Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Dashboard**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

## 📡 API Endpoints

### Job Postings

- `GET /api/jobs/` - List all job postings (paginated)
- `GET /api/jobs/recent/` - Get recent job postings (last 7 days)
- `GET /api/jobs/{id}/` - Get specific job posting
- `GET /api/jobs/?company=TechCorp&location=San Francisco` - Filter jobs

### Analytics

- `GET /api/analytics/skill-demand/` - Get skill demand statistics
- `GET /api/analytics/skill-demand/?role=python developer&top=20` - Filter by role
- `GET /api/analytics/role-volume/?days=30` - Get job volume trends
- `GET /api/analytics/avg-salary/` - Get average salary by role

### Skills

- `GET /api/skills/` - List all skill trends
- `GET /api/skills/?role=python` - Filter skills by role

## 🕷️ Scrapy Integration

### Running the Spider Manually

```bash
cd JobMarketTracker
scrapy crawl job_spider
```

### Configuring Real Job Sources

Edit `jobscraper/spiders/job_spider.py` to replace mock data with actual job board URLs:

1. Update `start_urls` with real job board URLs
2. Implement `parse()` method to extract data from HTML
3. Add pagination handling for multi-page results

Example:
```python
def parse(self, response):
    for job in response.css('div.job-listing'):
        item = JobPostingItem()
        item['job_title'] = job.css('h2.title::text').get()
        item['company'] = job.css('span.company::text').get()
        # ... extract other fields
        yield item
```

## 🔧 Configuration

### Celery Beat Schedule

The scraping task runs automatically every 6 hours. To modify the schedule, edit `JobMarketTracker/celery.py`:

```python
app.conf.beat_schedule = {
    'run-job-spider-every-6-hours': {
        'task': 'jobdata.tasks.run_job_spider',
        'schedule': 21600.0,  # Change this value (in seconds)
    },
}
```

### Skill Extraction

To add more skills for extraction, edit `jobdata/analysis.py` and add to the `TECH_SKILLS` list.

## 📊 Dashboard Features

- **Job Volume Trends**: Line chart showing job postings over time
- **Top Skills**: Bar chart displaying most demanded skills
- **Average Salaries**: Bar chart showing salary ranges by role
- **Filters**: Filter by date range, role, and location
- **Real-time Updates**: Data refreshes automatically

## 🧪 Testing

### Run Django Tests

```bash
python manage.py test
```

### Test API Endpoints

```bash
# Get recent jobs
curl http://localhost:8000/api/jobs/recent/

# Get skill demand
curl http://localhost:8000/api/analytics/skill-demand/

# Get job volume trends
curl http://localhost:8000/api/analytics/role-volume/?days=30
```

## 🗂️ Project Structure

```
JobMarketTracker/
├── JobMarketTracker/          # Django project settings
│   ├── settings.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── jobdata/                   # Main app for data models and API
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── analysis.py
│   ├── tasks.py
│   └── utils.py
├── jobscraper/                # Scrapy integration
│   ├── spiders/
│   │   └── job_spider.py
│   ├── pipelines.py
│   ├── items.py
│   └── settings.py
├── dashboard/                 # Frontend dashboard
│   ├── templates/
│   │   └── dashboard/
│   │       └── index.html
│   ├── views.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── README.md
```

## 🔒 Security Notes

- Change the `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` properly
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints in production

## 🐛 Troubleshooting

### Celery not working

- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check Celery worker logs for errors
- Verify Redis URL in `.env` file

### Database connection errors

- Verify database credentials in `.env`
- Ensure PostgreSQL is running (if using PostgreSQL)
- For SQLite, ensure file permissions are correct

### Scrapy spider not running

- Check Scrapy settings in `jobscraper/settings.py`
- Verify Django models are migrated
- Check Celery task logs for errors

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the GitHub repository.

---

**Note**: This project uses mock data for demonstration. In production, configure the spider to scrape from actual job boards and ensure compliance with their terms of service and robots.txt files.

