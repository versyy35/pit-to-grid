"""
Pulls a single session (Race or Qualifying) from FastF1 and writes it into
the local database using update-or-create logic, so re-running this command
for the same session never duplicates data.

Usage:
    python manage.py sync_race_data --year 2023 --race 6 --session R
    python manage.py sync_race_data --year 2023 --race "Monaco" --session Q

Note: --race accepts either a round number (int, e.g. 6) or a race name
(str, e.g. "Monaco"). Round numbers are strongly preferred for automation
since FastF1 does fuzzy name-matching on strings, which can silently
resolve to the wrong race. This also handles being called programmatically
via call_command() with race passed as an actual int (not a CLI string).
"""

import fastf1
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from races.models import (
    Season, Team, Driver, DriverSeasonEntry,
    Race, Session, Lap, PitStop, Result,
)

fastf1.Cache.enable_cache('.fastf1_cache')


class Command(BaseCommand):
    help = 'Sync one race/qualifying session from FastF1 into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument('--race', type=str, required=True,
                             help='Round number (e.g. 6) or race name (e.g. "Monaco")')
        parser.add_argument('--session', type=str, required=True, choices=['R', 'Q'])

    def handle(self, *args, **options):
        year = options['year']
        race_input = options['race']
        session_type = options['session']

        if isinstance(race_input, int):
            race_arg = race_input
        elif isinstance(race_input, str) and race_input.isdigit():
            race_arg = int(race_input)
        else:
            race_arg = race_input

        self.stdout.write(f'Fetching {year} {race_input} ({session_type}) from FastF1...')
        ff1_session = fastf1.get_session(year, race_arg, session_type)
        ff1_session.load()

        with transaction.atomic():
            season_obj = self._sync_season(year)
            race_obj = self._sync_race(season_obj, ff1_session)
            session_obj = self._sync_session(race_obj, session_type, ff1_session)
            driver_map = self._sync_drivers_and_teams(season_obj, ff1_session)
            self._sync_laps(session_obj, ff1_session, driver_map)
            self._sync_pit_stops(session_obj, ff1_session, driver_map)
            self._sync_results(session_obj, ff1_session, driver_map, session_type)

        self.stdout.write(self.style.SUCCESS(
            f'Synced {year} {race_obj.name} ({session_type}) successfully.'
        ))

    # ---- helpers -----------------------------------------------------

    def _sync_season(self, year):
        season_obj, _ = Season.objects.get_or_create(year=year)
        return season_obj

    def _sync_race(self, season_obj, ff1_session):
        event = ff1_session.event
        race_obj, _ = Race.objects.update_or_create(
            season=season_obj,
            round_number=event['RoundNumber'],
            defaults={
                'name': event['EventName'],
                'circuit': event['Location'],
                'country': event['Country'],
                'event_date': event['EventDate'].date() if pd.notnull(event['EventDate']) else None,
            }
        )
        return race_obj

    def _sync_session(self, race_obj, session_type, ff1_session):
        try:
            weather = ff1_session.weather_data
        except Exception:
            weather = None
        defaults = {}
        if weather is not None and not weather.empty:
            defaults = {
                'air_temp': float(weather['AirTemp'].mean()),
                'track_temp': float(weather['TrackTemp'].mean()),
                'humidity': float(weather['Humidity'].mean()),
                'rainfall': bool(weather['Rainfall'].any()),
            }
        session_obj, _ = Session.objects.update_or_create(
            race=race_obj,
            session_type=session_type,
            defaults=defaults,
        )
        return session_obj

    def _sync_drivers_and_teams(self, season_obj, ff1_session):
        """Returns a dict mapping FastF1 driver abbreviation -> Driver instance."""
        driver_map = {}
        results = ff1_session.results
        for _, row in results.iterrows():
            team_obj, _ = Team.objects.get_or_create(
                season=season_obj,
                name=row['TeamName'],
            )
            driver_obj, _ = Driver.objects.update_or_create(
                driver_code=row['Abbreviation'],
                driver_number=int(row['DriverNumber']) if pd.notnull(row['DriverNumber']) else None,
                defaults={'full_name': row['FullName']},
            )
            DriverSeasonEntry.objects.update_or_create(
                driver=driver_obj, season=season_obj,
                defaults={'team': team_obj},
            )
            driver_map[row['Abbreviation']] = driver_obj
        return driver_map

    def _sync_laps(self, session_obj, ff1_session, driver_map):
        laps = ff1_session.laps
        for _, lap in laps.iterrows():
            driver_obj = driver_map.get(lap['Driver'])
            if driver_obj is None or pd.isnull(lap['LapNumber']):
                continue
            Lap.objects.update_or_create(
                session=session_obj,
                driver=driver_obj,
                lap_number=int(lap['LapNumber']),
                defaults={
                    'lap_time_seconds': lap['LapTime'].total_seconds() if pd.notnull(lap['LapTime']) else None,
                    'sector1_seconds': lap['Sector1Time'].total_seconds() if pd.notnull(lap['Sector1Time']) else None,
                    'sector2_seconds': lap['Sector2Time'].total_seconds() if pd.notnull(lap['Sector2Time']) else None,
                    'sector3_seconds': lap['Sector3Time'].total_seconds() if pd.notnull(lap['Sector3Time']) else None,
                    'compound': lap['Compound'] or '',
                    'tyre_life': int(lap['TyreLife']) if pd.notnull(lap['TyreLife']) else None,
                    'position': int(lap['Position']) if pd.notnull(lap['Position']) else None,
                    'is_pit_lap': pd.notnull(lap['PitInTime']) or pd.notnull(lap['PitOutTime']),
                }
            )

    def _sync_pit_stops(self, session_obj, ff1_session, driver_map):
        """
        PitInTime is recorded on the lap a driver enters the pits (the 'in-lap').
        PitOutTime is recorded on the FOLLOWING lap, when they exit (the 'out-lap').
        These are two different rows, so we pair each in-lap with the next
        out-lap for that same driver, rather than looking for both on one row.
        """
        laps = ff1_session.laps
        for driver_code, driver_obj in driver_map.items():
            driver_laps = laps[laps['Driver'] == driver_code].sort_values('LapNumber')
            in_laps = driver_laps[pd.notnull(driver_laps['PitInTime'])]

            for _, in_lap in in_laps.iterrows():
                later_laps = driver_laps[driver_laps['LapNumber'] > in_lap['LapNumber']]
                out_laps = later_laps[pd.notnull(later_laps['PitOutTime'])]
                if out_laps.empty:
                    continue
                out_lap = out_laps.iloc[0]

                duration = (out_lap['PitOutTime'] - in_lap['PitInTime']).total_seconds()
                if duration <= 0:
                    continue

                PitStop.objects.update_or_create(
                    session=session_obj,
                    driver=driver_obj,
                    lap_number=int(in_lap['LapNumber']),
                    defaults={'duration_seconds': duration},
                )

    def _sync_results(self, session_obj, ff1_session, driver_map, session_type):
        results = ff1_session.results
        for _, row in results.iterrows():
            driver_obj = driver_map.get(row['Abbreviation'])
            team_obj = Team.objects.filter(
                season=session_obj.race.season, name=row['TeamName']
            ).first()
            if driver_obj is None or team_obj is None:
                continue

            defaults = {
                'team': team_obj,
                'grid_position': int(row['GridPosition']) if pd.notnull(row.get('GridPosition')) else None,
                'points': float(row['Points']) if pd.notnull(row.get('Points')) else 0,
                'status': row.get('Status', '') or '',
            }
            if session_type == 'R':
                defaults['finishing_position'] = int(row['Position']) if pd.notnull(row['Position']) else None
            else:
                defaults['q1_seconds'] = row['Q1'].total_seconds() if pd.notnull(row.get('Q1')) else None
                defaults['q2_seconds'] = row['Q2'].total_seconds() if pd.notnull(row.get('Q2')) else None
                defaults['q3_seconds'] = row['Q3'].total_seconds() if pd.notnull(row.get('Q3')) else None

            Result.objects.update_or_create(
                session=session_obj,
                driver=driver_obj,
                defaults=defaults,
            )
