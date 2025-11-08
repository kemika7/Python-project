"""
Django management command to load Nepal job market data.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load Nepal job market data from fixtures'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading Nepal job market data...'))
        
        try:
            call_command('loaddata', 'nepal_job_market_data.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS(
                'Successfully loaded Nepal job market data!'
            ))
            self.stdout.write(self.style.SUCCESS(
                'Run "python manage.py analyze_skills" to extract skills from job descriptions.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            raise

