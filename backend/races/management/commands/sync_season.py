"""
Syncs an entire season's worth of races (both Race and Qualifying sessions)
by looping over FastF1's event schedule and calling the same sync logic as
sync_race_data, one round at a time. Skips rounds that fail instead of
aborting the whole season, and prints a summary at the end.

Usage:
    python manage.py sync_season --year 2023
    python manage.py sync_season --year 2023 --sessions R      (race only)
    python manage.py sync_season --year 2023 --sessions R,Q    (default)
"""

import time
import fastf1
from django.core.management import call_command
from django.core.management.base import BaseCommand

fastf1.Cache.enable_cache('.fastf1_cache')


class Command(BaseCommand):
    help = "Sync every race in a season (Race + Qualifying) from FastF1."

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument(
            '--sessions', type=str, default='R,Q',
            help='Comma-separated session types to sync, e.g. "R,Q" or just "R"'
        )

    def handle(self, *args, **options):
        year = options['year']
        session_types = [s.strip() for s in options['sessions'].split(',')]

        self.stdout.write(f'Fetching {year} event schedule...')
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        succeeded = []
        failed = []

        for _, event in schedule.iterrows():
            round_number = int(event['RoundNumber'])
            race_name = event['EventName']

            for session_type in session_types:
                label = f'{year} R{round_number} {race_name} ({session_type})'
                try:
                    self.stdout.write(f'--- Syncing {label} ---')
                    call_command(
                        'sync_race_data',
                        year=year,
                        race=round_number,
                        session=session_type,
                    )
                    succeeded.append(label)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'FAILED {label}: {e}'))
                    failed.append(label)

                time.sleep(90)  # stay under FastF1's ~500 calls/hour rate limit

        self.stdout.write(self.style.SUCCESS(
            f'\nSeason {year} sync complete: {len(succeeded)} succeeded, {len(failed)} failed.'
        ))
        if failed:
            self.stdout.write(self.style.WARNING('Failed sessions:'))
            for label in failed:
                self.stdout.write(f'  - {label}')
