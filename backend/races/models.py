from django.db import models

# Create your models here.
from django.db import models


class Season(models.Model):
    """A single F1 season/year, e.g. 2023."""
    year = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ['year']

    def __str__(self):
        return str(self.year)


class Team(models.Model):
    """A constructor within a season (teams are re-created per season since
    livery/name/lineup can change, e.g. 'Alfa Romeo' -> 'Kick Sauber')."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('season', 'name')

    def __str__(self):
        return f'{self.name} ({self.season.year})'


class Driver(models.Model):
    """A driver. Kept season-agnostic at the identity level (same person,
    same row, across years) since FastF1 driver codes/numbers are stable."""
    driver_code = models.CharField(max_length=10)   # e.g. 'VER', 'HAM'
    driver_number = models.PositiveIntegerField(null=True, blank=True)
    full_name = models.CharField(max_length=100)
    photo_url = models.URLField(max_length=500, blank=True)
    
    class Meta:
        unique_together = ('driver_code', 'driver_number')

    def __str__(self):
        return f'{self.full_name} ({self.driver_code})'


class DriverSeasonEntry(models.Model):
    """Links a Driver to the Team they raced for in a given Season.
    This is what lets the same driver be tied to different teams by year."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='season_entries')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='driver_entries')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='driver_entries')

    class Meta:
        unique_together = ('driver', 'season')

    def __str__(self):
        return f'{self.driver.driver_code} - {self.team.name} ({self.season.year})'


class Race(models.Model):
    """A single Grand Prix weekend (round) within a season."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='races')
    round_number = models.PositiveIntegerField()
    name = models.CharField(max_length=150)          # e.g. 'Monaco Grand Prix'
    circuit = models.CharField(max_length=150)
    country = models.CharField(max_length=100, blank=True)
    event_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('season', 'round_number')
        ordering = ['season__year', 'round_number']

    def __str__(self):
        return f'{self.name} {self.season.year}'


class Session(models.Model):
    """A specific session within a race weekend: Race or Qualifying (extend
    later with Practice/Sprint if needed)."""
    SESSION_TYPES = [
        ('R', 'Race'),
        ('Q', 'Qualifying'),
    ]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=2, choices=SESSION_TYPES)
    air_temp = models.FloatField(null=True, blank=True)
    track_temp = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    rainfall = models.BooleanField(default=False)

    class Meta:
        unique_together = ('race', 'session_type')

    def __str__(self):
        return f'{self.race.name} - {self.get_session_type_display()}'


class Lap(models.Model):
    """A single lap by a driver in a session."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='laps')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='laps')
    lap_number = models.PositiveIntegerField()
    lap_time_seconds = models.FloatField(null=True, blank=True)   # null = no time set (retirement, red flag, etc.)
    sector1_seconds = models.FloatField(null=True, blank=True)
    sector2_seconds = models.FloatField(null=True, blank=True)
    sector3_seconds = models.FloatField(null=True, blank=True)
    compound = models.CharField(max_length=20, blank=True)        # e.g. 'SOFT', 'MEDIUM', 'HARD', 'WET'
    tyre_life = models.PositiveIntegerField(null=True, blank=True)  # laps on this set of tyres
    position = models.PositiveIntegerField(null=True, blank=True)
    is_pit_lap = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'driver', 'lap_number')
        ordering = ['session', 'lap_number']

    def __str__(self):
        return f'{self.driver.driver_code} - Lap {self.lap_number} ({self.session})'


class PitStop(models.Model):
    """A single pit stop event."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='pit_stops')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='pit_stops')
    lap_number = models.PositiveIntegerField()
    duration_seconds = models.FloatField()

    class Meta:
        ordering = ['session', 'lap_number']

    def __str__(self):
        return f'{self.driver.driver_code} pit @ lap {self.lap_number} ({self.duration_seconds}s)'


class Result(models.Model):
    """Final classification for a driver in a session (race or qualifying)."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='results')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='results')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='results')
    finishing_position = models.PositiveIntegerField(null=True, blank=True)
    grid_position = models.PositiveIntegerField(null=True, blank=True)
    points = models.FloatField(default=0)
    status = models.CharField(max_length=50, blank=True)   # 'Finished', 'DNF', 'DSQ', etc.
    q1_seconds = models.FloatField(null=True, blank=True)
    q2_seconds = models.FloatField(null=True, blank=True)
    q3_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('session', 'driver')
        ordering = ['session', 'finishing_position']

    def __str__(self):
        return f'{self.driver.driver_code} - P{self.finishing_position} ({self.session})'