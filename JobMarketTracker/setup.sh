#!/bin/bash

# Setup script for JobMarketTracker

echo "🚀 Setting up JobMarketTracker..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser (optional, press Ctrl+C to skip)..."
python manage.py createsuperuser || echo "Superuser creation skipped"

# Load initial data
echo "📊 Loading initial test data..."
python manage.py loaddata jobdata/fixtures/initial_data.json || echo "No fixtures to load"

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Start Redis: brew services start redis (macOS) or sudo systemctl start redis (Linux)"
echo "2. Start Celery worker: celery -A JobMarketTracker worker -l info"
echo "3. Start Celery beat: celery -A JobMarketTracker beat -l info"
echo "4. Start Django server: python manage.py runserver"
echo "5. Visit http://localhost:8000/ to see the dashboard"

