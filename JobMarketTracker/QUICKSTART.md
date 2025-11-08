# Quick Start Guide

## Prerequisites

- Python 3.8+
- Redis (for Celery)
- PostgreSQL (optional, SQLite works for development)

## Installation Steps

### 1. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows:**
Download from https://redis.io/download

### 2. Setup Project

```bash
# Navigate to project directory
cd JobMarketTracker

# Run setup script (Linux/macOS)
./setup.sh

# OR manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
```

### 3. Load Test Data (Optional)

```bash
python manage.py loaddata jobdata/fixtures/initial_data.json
```

### 4. Run the Application

**Terminal 1 - Celery Worker:**
```bash
celery -A JobMarketTracker worker -l info
```

**Terminal 2 - Celery Beat:**
```bash
celery -A JobMarketTracker beat -l info
```

**Terminal 3 - Django Server:**
```bash
python manage.py runserver
```

### 5. Access the Application

- Dashboard: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/
- API: http://localhost:8000/api/

## Testing the Setup

### Run Spider Manually

```bash
python manage.py run_spider
```

### Analyze Skills

```bash
python manage.py analyze_skills
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

## Troubleshooting

### Redis Connection Error

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Celery Not Working

- Ensure Redis is running
- Check Celery worker logs for errors
- Verify Redis URL in `.env` file

### Database Issues

- For SQLite: No setup needed, works out of the box
- For PostgreSQL: Ensure database exists and credentials are correct in `.env`

### Scrapy Spider Issues

- Check Scrapy logs for errors
- Verify Django models are migrated
- Ensure Celery task is running properly

## Next Steps

1. Configure real job board URLs in `jobscraper/spiders/job_spider.py`
2. Customize skill extraction in `jobdata/analysis.py`
3. Adjust Celery Beat schedule in `JobMarketTracker/celery.py`
4. Customize dashboard in `dashboard/templates/dashboard/index.html`

