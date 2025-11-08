"""
Django management command to analyze skills from job postings.
"""
from django.core.management.base import BaseCommand
from jobdata.analysis import analyze_skills


class Command(BaseCommand):
    help = 'Analyze skills from job postings and update skill trends'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            help='Filter by role (e.g., "python developer")',
        )

    def handle(self, *args, **options):
        role = options.get('role')
        self.stdout.write(self.style.SUCCESS(f'Starting skill analysis (role: {role or "all"})...'))
        
        try:
            result = analyze_skills(role=role)
            self.stdout.write(self.style.SUCCESS(
                f'Skill analysis completed! '
                f'Found {result.get("total_jobs", 0)} jobs and '
                f'{len(result.get("skills", {}))} unique skills.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error analyzing skills: {str(e)}'))
            raise

