"""
Fetches a Wikipedia thumbnail image URL for each Driver and stores it in
photo_url. Safe to re-run -- only updates drivers that don't already have
a photo_url, unless --force is passed.

Usage:
    python manage.py sync_driver_photos
    python manage.py sync_driver_photos --force
"""

import time
import requests
from django.core.management.base import BaseCommand

from races.models import Driver

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

# Manual overrides for drivers whose full_name doesn't match their
# Wikipedia page title exactly (disambiguation pages, name collisions, etc.)
TITLE_OVERRIDES = {
    "Carlos Sainz": "Carlos_Sainz_Jr.",
    "George Russell": "George_Russell_(racing_driver)",
}
HEADERS = {
    "User-Agent": "PitToGrid/1.0 (educational project; contact: adamlotfi2004@gmail.com)"
}


class Command(BaseCommand):
    help = "Fetch driver photo URLs from Wikipedia and store them on the Driver model."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Re-fetch and overwrite drivers that already have a photo_url.'
        )

    def handle(self, *args, **options):
        force = options['force']

        drivers = Driver.objects.all()
        if not force:
            drivers = drivers.filter(photo_url='')

        self.stdout.write(f'Fetching photos for {drivers.count()} drivers...')

        succeeded = []
        failed = []

        for driver in drivers:
            title = TITLE_OVERRIDES.get(driver.full_name, driver.full_name.replace(' ', '_'))
            url = WIKI_API.format(title=title)

            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code != 200:
                    failed.append(f'{driver.full_name} (HTTP {response.status_code})')
                    continue

                data = response.json()
                thumbnail = data.get('thumbnail', {}).get('source')

                if not thumbnail:
                    failed.append(f'{driver.full_name} (no thumbnail found)')
                    continue

                driver.photo_url = thumbnail
                driver.save()
                succeeded.append(driver.full_name)
                self.stdout.write(f'  OK: {driver.full_name}')

            except requests.RequestException as e:
                failed.append(f'{driver.full_name} (request error: {e})')

            time.sleep(0.5)  # be polite to Wikipedia's API

        self.stdout.write(self.style.SUCCESS(
            f'\nDone: {len(succeeded)} succeeded, {len(failed)} failed.'
        ))
        if failed:
            self.stdout.write(self.style.WARNING('Failed drivers (need manual mapping):'))
            for label in failed:
                self.stdout.write(f'  - {label}')
