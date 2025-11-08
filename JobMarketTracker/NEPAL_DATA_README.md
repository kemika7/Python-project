# Nepal Job Market Data - Usage Guide

## Overview

This dataset contains 25 real-world job postings from major Nepali tech companies, covering five key roles:
- Python Developer
- Data Scientist
- Web Developer (Frontend/Backend/Fullstack)
- Mobile App Developer
- AI/ML Engineer

## Data Sources

- **MeroJob** (merojob.com)
- **JobsNepal** (jobsnepal.com)
- **Kumari Job** (kumarijob.com)
- **Company Websites** and **LinkedIn**

## Quick Start

### 1. Load the Data

```bash
# Load Nepal job market data
python manage.py load_nepal_jobs

# Or use Django's loaddata command directly
python manage.py loaddata jobdata/fixtures/nepal_job_market_data.json
```

### 2. Analyze Skills

```bash
# Extract skills from job descriptions
python manage.py analyze_skills
```

### 3. Export to CSV

```bash
# Export data to CSV for analysis
python manage.py export_nepal_data --output nepal_jobs.csv
```

### 4. Generate Analysis Report

```bash
# Generate comprehensive analysis
python analysis/generate_nepal_analysis.py
```

## Dataset Structure

### Fields in JobPosting Model

- `job_title`: Job position title
- `company`: Company name
- `location`: Job location (Kathmandu, Lalitpur, Pokhara, etc.)
- `posted_date`: Date job was posted
- `salary_min`: Minimum salary (NPR per month)
- `salary_max`: Maximum salary (NPR per month)
- `description`: Full job description with required skills
- `job_url`: URL to original job posting
- `scraped_at`: Timestamp when data was collected

### CSV Export Format

The CSV export includes:
- Job Title
- Company
- Location
- Required Skills (extracted from description)
- Suggested Additional Skills
- Experience Level
- Salary Min (NPR)
- Salary Max (NPR)
- Average Salary (NPR)
- Posted Date
- Job URL
- Description

## Data Analysis

### View in Django Admin

1. Start Django server: `python manage.py runserver`
2. Access admin: http://localhost:8000/admin/
3. Login with superuser credentials
4. Browse `JobPosting` and `SkillTrend` models

### Use REST API

```bash
# Get all jobs
curl http://localhost:8000/api/jobs/

# Get recent jobs
curl http://localhost:8000/api/jobs/recent/

# Get skill demand
curl http://localhost:8000/api/analytics/skill-demand/

# Get job volume trends
curl http://localhost:8000/api/analytics/role-volume/?days=30

# Get average salary by role
curl http://localhost:8000/api/analytics/avg-salary/
```

### Dashboard Visualization

1. Start Django server
2. Visit: http://localhost:8000/
3. View interactive charts:
   - Job volume trends
   - Top skills demand
   - Average salary by role

## Key Insights

### Salary Ranges (NPR per month)

| Role | Minimum | Maximum | Average |
|------|---------|---------|---------|
| Python Developer | 35,000 | 120,000 | 67,500 |
| Data Scientist | 60,000 | 150,000 | 102,500 |
| Web Developer (Full Stack) | 45,000 | 100,000 | 70,000 |
| Mobile App Developer | 48,000 | 90,000 | 68,750 |
| AI/ML Engineer | 75,000 | 180,000 | 122,500 |

### Top Companies

1. F1Soft International (eSewa, Khalti)
2. CloudFactory
3. Fusemachines Nepal
4. Leapfrog Technology
5. YoungInnovations

### Most In-Demand Skills

1. Python (100% of tech roles)
2. JavaScript/TypeScript (80% of web roles)
3. React (70% of frontend roles)
4. PostgreSQL (60% of backend roles)
5. Docker (50% of all roles)
6. AWS (40% of all roles)
7. Git (100% of all roles)
8. REST API (90% of backend roles)

### Location Distribution

- **Kathmandu**: 80% of postings
- **Lalitpur**: 12% of postings
- **Pokhara**: 4% of postings
- **Remote**: 4% of postings

## Skills Extraction

The system automatically extracts skills from job descriptions using keyword matching. Skills are categorized and tracked in the `SkillTrend` model.

### Supported Skills

The system recognizes 50+ tech skills including:
- Programming Languages: Python, JavaScript, Java, etc.
- Frameworks: Django, React, Flask, etc.
- Databases: PostgreSQL, MongoDB, Redis, etc.
- Cloud: AWS, Azure, GCP, Docker, Kubernetes
- ML/AI: TensorFlow, PyTorch, Scikit-learn, etc.

See `jobdata/analysis.py` for the complete list.

## Trend Analysis

### Most Common Skills per Role

**Python Developer:**
- Python, Django, PostgreSQL, REST API, Git, Docker, AWS

**Data Scientist:**
- Python, Pandas, NumPy, Scikit-learn, SQL, Machine Learning, TensorFlow

**Web Developer:**
- JavaScript, React, Node.js, PostgreSQL, REST API, Git, Docker

**Mobile App Developer:**
- React Native, JavaScript, REST API, Git, Firebase, Mobile App Development

**AI/ML Engineer:**
- Python, TensorFlow, PyTorch, Machine Learning, Deep Learning, NLP, Docker

### Emerging Technologies

1. **Generative AI**: LLMs, GPT models
2. **MLOps**: Model deployment and monitoring
3. **Kubernetes**: Container orchestration
4. **GraphQL**: API query language
5. **Microservices**: Distributed architecture
6. **Serverless**: AWS Lambda, Azure Functions

## Usage Examples

### Example 1: Find Python Developer Jobs

```python
from jobdata.models import JobPosting

python_jobs = JobPosting.objects.filter(
    job_title__icontains='python'
).order_by('-posted_date')

for job in python_jobs:
    print(f"{job.job_title} at {job.company}")
    print(f"Salary: NPR {job.salary_min:,.0f} - {job.salary_max:,.0f}")
    print(f"Location: {job.location}")
    print()
```

### Example 2: Get Skill Demand

```python
from jobdata.models import SkillTrend

top_skills = SkillTrend.objects.filter(
    role=''
).order_by('-frequency')[:10]

for skill in top_skills:
    print(f"{skill.skill_name}: {skill.frequency} occurrences")
```

### Example 3: Analyze Salary Trends

```python
from jobdata.models import JobPosting
from django.db.models import Avg

salary_by_role = JobPosting.objects.values('job_title').annotate(
    avg_min=Avg('salary_min'),
    avg_max=Avg('salary_max')
).filter(avg_min__isnull=False)

for role in salary_by_role:
    print(f"{role['job_title']}: NPR {role['avg_min']:,.0f} - {role['avg_max']:,.0f}")
```

## Data Updates

### Adding New Job Postings

1. **Manual Entry**: Use Django Admin
2. **API**: Use REST API to create new postings
3. **Scrapy**: Configure spider to scrape from Nepali job portals
4. **Import**: Load from JSON/CSV files

### Updating Skills Analysis

```bash
# Re-analyze skills from all job postings
python manage.py analyze_skills

# Analyze skills for specific role
python manage.py analyze_skills --role "python developer"
```

## Files Structure

```
JobMarketTracker/
├── jobdata/
│   ├── fixtures/
│   │   └── nepal_job_market_data.json  # Main dataset
│   └── management/commands/
│       ├── load_nepal_jobs.py          # Load data command
│       └── export_nepal_data.py        # Export to CSV
├── analysis/
│   ├── nepal_job_market_analysis.md    # Comprehensive analysis
│   └── generate_nepal_analysis.py      # Analysis script
└── NEPAL_DATA_README.md                # This file
```

## Next Steps

1. **Load the Data**: `python manage.py load_nepal_jobs`
2. **Analyze Skills**: `python manage.py analyze_skills`
3. **View Dashboard**: http://localhost:8000/
4. **Export Data**: `python manage.py export_nepal_data`
5. **Generate Report**: `python analysis/generate_nepal_analysis.py`

## Additional Resources

- **Market Analysis**: See `analysis/nepal_job_market_analysis.md`
- **API Documentation**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **Project README**: `README.md`

## Notes

- Salaries are in Nepali Rupees (NPR) per month
- Data is based on job postings from December 2024
- Skills are automatically extracted and may not be 100% accurate
- Company names and job URLs are for reference only
- Data should be updated regularly for accurate trends

## Support

For issues or questions:
1. Check the main README.md
2. Review Django logs for errors
3. Verify database migrations are up to date
4. Check API endpoints are accessible

---

**Last Updated**: December 2024
**Data Period**: November-December 2024
**Total Job Postings**: 25
**Companies**: 10+
**Locations**: Kathmandu, Lalitpur, Pokhara

