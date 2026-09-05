from django.contrib import admin
from .models import (
    Season, Team, Driver, DriverSeasonEntry,
    Race, Session, Lap, PitStop, Result,
)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season')
    list_filter = ('season',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('driver_code', 'full_name', 'driver_number')
    search_fields = ('driver_code', 'full_name')


@admin.register(DriverSeasonEntry)
class DriverSeasonEntryAdmin(admin.ModelAdmin):
    list_display = ('driver', 'season', 'team')
    list_filter = ('season', 'team')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'round_number', 'circuit', 'event_date')
    list_filter = ('season',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('race', 'session_type', 'rainfall')
    list_filter = ('session_type', 'race__season')


@admin.register(Lap)
class LapAdmin(admin.ModelAdmin):
    list_display = ('session', 'driver', 'lap_number', 'lap_time_seconds', 'compound', 'is_pit_lap')
    list_filter = ('session__race__season', 'compound')
    search_fields = ('driver__driver_code',)


@admin.register(PitStop)
class PitStopAdmin(admin.ModelAdmin):
    list_display = ('session', 'driver', 'lap_number', 'duration_seconds')
    list_filter = ('session__race__season',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('session', 'driver', 'team', 'finishing_position', 'grid_position', 'points', 'status')
    list_filter = ('session__race__season', 'status')